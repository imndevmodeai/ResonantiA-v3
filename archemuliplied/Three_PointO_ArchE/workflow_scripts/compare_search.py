import sys
import json


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    # Handle the case where JSON is the literal null -> Python None
    if data is None:
        data = {}

    def coerce_dict(obj):
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, str):
            try:
                parsed = json.loads(obj)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}
        return {}

    def coerce_list(obj):
        if obj is None:
            return []
        if isinstance(obj, list):
            return obj
        if isinstance(obj, str):
            try:
                parsed = json.loads(obj)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []

    external_results = coerce_list(data.get("external_api_results"))
    internal_results = coerce_list(data.get("internal_codebase_results"))
    ext_reflection = coerce_dict(data.get("external_search_reflection"))
    int_reflection = coerce_dict(data.get("internal_search_reflection"))

    ext_count = len(external_results) if isinstance(external_results, list) else 0
    int_count = len(internal_results) if isinstance(internal_results, list) else 0

    # Extract IAR cues
    ext_status = ext_reflection.get("status", "N/A")
    ext_conf = ext_reflection.get("confidence", "N/A")
    ext_issues = ext_reflection.get("potential_issues") or []

    int_status = (int_reflection.get("status") or int_reflection.get("Status") or "N/A")
    int_conf = (int_reflection.get("confidence") or int_reflection.get("Confidence") or "N/A")
    int_issues = int_reflection.get("potential_issues") or []

    summary_lines = []
    summary_lines.append(f"External web search returned {ext_count} items.")
    summary_lines.append(f"Internal codebase search returned {int_count} items.")

    if ext_count > 0 and int_count > 0:
        summary_lines.append("Both sources have relevant data.")
    elif ext_count > 0:
        summary_lines.append("Only external sources returned results; consider expanding internal artifacts.")
    elif int_count > 0:
        summary_lines.append("Only internal codebase returned results; external corpus may be sparse for this query.")
    else:
        summary_lines.append("Neither external nor internal search yielded results.")

    if ext_count > int_count:
        summary_lines.append("External knowledge base appears broader for this query.")
    elif int_count > ext_count:
        summary_lines.append("Internal codebase has more direct hits; indicates focused internal R&D.")
    elif ext_count > 0:
        summary_lines.append("Comparable number of results from external and internal searches.")

    # IAR notes
    summary_lines.append(f"External Search IAR: Status='{ext_status}', Confidence={ext_conf}.")
    if ext_issues:
        summary_lines.append("External Search Potential Issues: " + "; ".join(map(str, ext_issues)) + ".")
    if isinstance(ext_conf, (int, float)) and ext_conf < 0.7:
        summary_lines.append("Note: External search confidence is moderate/low; cross-verify.")

    summary_lines.append(f"Internal Search IAR: Status='{int_status}', Confidence={int_conf}.")
    if int_issues:
        summary_lines.append("Internal Search Potential Issues: " + "; ".join(map(str, int_issues)) + ".")

    print(" ".join(summary_lines))


if __name__ == "__main__":
    main()


