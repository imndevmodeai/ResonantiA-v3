import os
import re
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple


def _run_ripgrep(pattern: str,
                 root: str,
                 case_insensitive: bool,
                 context_lines: int,
                 include_globs: Optional[List[str]],
                 exclude_globs: Optional[List[str]],
                 max_results: int) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Run ripgrep if available and parse basic results."""
    rg_cmd = ["rg", "--line-number", "--no-heading", "--color", "never"]
    if case_insensitive:
        rg_cmd.append("-i")
    if context_lines and context_lines > 0:
        rg_cmd.extend(["-C", str(context_lines)])
    if include_globs:
        for g in include_globs:
            rg_cmd.extend(["--glob", g])
    if exclude_globs:
        for g in exclude_globs:
            rg_cmd.extend(["--glob", f"!{g}"])

    # Limit matches (per file) not global; handle post-truncation instead
    rg_cmd.extend([pattern, root])

    try:
        proc = subprocess.run(
            rg_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
    except FileNotFoundError:
        return [], "ripgrep_not_found"
    except Exception as e:
        return [], f"ripgrep_error: {e}"

    if proc.returncode not in (0, 1):  # 0=matches, 1=no matches
        return [], f"ripgrep_failed: {proc.stderr.strip()}"

    results: List[Dict[str, Any]] = []
    total = 0
    for line in proc.stdout.splitlines():
        # Format: path:line:content  (context lines look like path-line-content)
        # We'll only collect direct match lines (with ':') and ignore leading context markers.
        if not line:
            continue
        # Identify match vs context by presence of ':' delimiters
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        file_path, line_num, content = parts[0], parts[1], parts[2]
        # Ensure integers where possible
        try:
            ln = int(line_num)
        except ValueError:
            # Some context lines may not be numeric; skip
            continue

        results.append({
            "file_path": file_path,
            "line": ln,
            "text": content
        })
        total += 1
        if total >= max_results:
            break

    return results, None


def _walk_and_search(pattern: str,
                     root: str,
                     case_insensitive: bool,
                     context_lines: int,
                     include_globs: Optional[List[str]],
                     exclude_globs: Optional[List[str]],
                     max_results: int) -> List[Dict[str, Any]]:
    """Fallback Python search using regex and os.walk (slower)."""
    flags = re.IGNORECASE if case_insensitive else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error:
        # Treat as literal if invalid regex
        regex = re.compile(re.escape(pattern), flags)

    def _match_globs(path: str, globs: List[str]) -> bool:
        from fnmatch import fnmatch
        return any(fnmatch(path, g) for g in globs)

    results: List[Dict[str, Any]] = []
    total = 0
    include = include_globs or ["**/*"]
    exclude = exclude_globs or ["**/.git/**", "**/node_modules/**", "**/.venv/**", "**/venv/**", "**/__pycache__/**"]

    for dirpath, dirnames, filenames in os.walk(root):
        # Apply directory excludes early
        dirnames[:] = [d for d in dirnames if not _match_globs(os.path.join(dirpath, d), exclude)]
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            if not _match_globs(fpath, include) or _match_globs(fpath, exclude):
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                continue

            for idx, text in enumerate(lines, start=1):
                if regex.search(text):
                    entry: Dict[str, Any] = {
                        "file_path": fpath,
                        "line": idx,
                        "text": text.rstrip('\n')
                    }
                    if context_lines > 0:
                        start = max(0, idx - 1 - context_lines)
                        end = min(len(lines), idx - 1 + context_lines + 1)
                        entry["context_before"] = [l.rstrip('\n') for l in lines[start:idx - 1]]
                        entry["context_after"] = [l.rstrip('\n') for l in lines[idx:end]]
                    results.append(entry)
                    total += 1
                    if total >= max_results:
                        return results
    return results


def search_codebase(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search the project codebase for a pattern.

    Inputs:
      - query (str): regex or literal text to search for
      - root (str, optional): starting directory; defaults to current repo root (cwd)
      - case_insensitive (bool): default True
      - context_lines (int): default 0
      - include_globs (list[str]): file/path include globs
      - exclude_globs (list[str]): file/path exclude globs
      - max_results (int): default 200

    Returns:
      {
        "search_results": [ {file_path, line, text, context_before?, context_after?}, ... ],
        "results_count": int,
        "reflection": { status, message, confidence }
      }
    """
    query = inputs.get("query")
    if not query or not isinstance(query, str):
        return {
            "error": "Input 'query' is required (string).",
            "reflection": {
                "status": "failure",
                "message": "Missing required input 'query'.",
                "confidence": 0.0
            }
        }

    root = inputs.get("root") or os.getcwd()
    case_insensitive = bool(inputs.get("case_insensitive", True))
    context_lines = int(inputs.get("context_lines", 0))
    include_globs = inputs.get("include_globs") or []
    exclude_globs = inputs.get("exclude_globs") or []
    max_results = int(inputs.get("max_results", 200))

    # Try ripgrep first
    rg_results, rg_err = _run_ripgrep(query, root, case_insensitive, context_lines, include_globs, exclude_globs, max_results)
    if rg_err is None:
        return {
            "search_results": rg_results,
            "results_count": len(rg_results),
            "reflection": {
                "status": "success",
                "message": f"ripgrep search completed with {len(rg_results)} results.",
                "confidence": 0.95
            }
        }

    # Fallback Python walker
    py_results = _walk_and_search(query, root, case_insensitive, context_lines, include_globs, exclude_globs, max_results)
    return {
        "search_results": py_results,
        "results_count": len(py_results),
        "reflection": {
            "status": "success" if py_results else "warning",
            "message": f"python-walk search completed with {len(py_results)} results (fallback used: {rg_err}).",
            "confidence": 0.75 if py_results else 0.6
        }
    }


if __name__ == "__main__":
    # Simple ad-hoc manual test
    out = search_codebase({"query": "search_codebase", "context_lines": 1, "max_results": 5})
    print(json.dumps(out, indent=2))


