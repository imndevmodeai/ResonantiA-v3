#!/usr/bin/env python3
"""
CrystallizedObjectiveGenerator (COG)
Turns natural-language mandates into CrystallizedObjective artifacts.
"""

import uuid
import time
import json
import math
import hashlib
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

# -------------------------
# Domain Data Structures
# -------------------------

@dataclass
class Mandate:
    id: str
    issuer: str
    text: str
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    seed: Optional[int] = None
    domain: str = "cognitive"

    @staticmethod
    def normalize(raw: Dict[str, Any]) -> "Mandate":
        mid = raw.get("id") or str(uuid.uuid4())
        return Mandate(
            id=mid,
            issuer=raw.get("issuer", "user"),
            text=(raw.get("text") or "").strip(),
            priority=int(raw.get("priority", 1)),
            tags=list(raw.get("tags") or []),
            constraints=dict(raw.get("constraints") or {}),
            deadline=raw.get("deadline"),
            context=dict(raw.get("context") or {}),
            seed=raw.get("seed"),
            domain=raw.get("domain", "cognitive")
        )

@dataclass
class FeatureVector:
    numerical: Dict[str, float] = field(default_factory=dict)
    categorical: Dict[str, str] = field(default_factory=dict)
    embeddings: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class TemporalScope:
    start: float
    end: Optional[float]
    granularity: str
    horizons: Dict[str, Tuple[Optional[float], Optional[float]]] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)  # results from H,T,F,C,E,Tr

@dataclass
class SPR:
    id: str
    name: str
    tags: List[str]
    signature: Dict[str, Any]
    pattern: str
    preconditions: Dict[str, Any]
    effects: Dict[str, Any]
    cost: float = 1.0
    temporal_hint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActivatedSPR:
    spr_id: str
    spr_name: str
    weight: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    matched_features: Dict[str, Any] = field(default_factory=dict)
    activated_at: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Step:
    id: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    temporal_window: Optional[Dict[str, float]] = None
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrystallizedObjective:
    id: str
    mandate_id: str
    steps: List[Step]
    acceptance_score: float
    explanations: List[str] = field(default_factory=list)
    temporal_scope: Optional[TemporalScope] = None
    created_at: float = field(default_factory=time.time)
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

# -------------------------
# Utilities
# -------------------------

def deterministic_hash(obj: Any) -> str:
    s = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

# -------------------------
# CrystallizedObjectiveGenerator
# -------------------------

class CrystallizedObjectiveGenerator:
    """
    COG: turns natural-language mandates into CrystallizedObjective (◊).
    Domain: Cognitive Architecture / Agent Reasoning
    """

    def __init__(
        self,
        spr_bank_loader: Callable[[], List[SPR]],
        scoring_fn: Optional[Callable[[FeatureVector, SPR, TemporalScope], float]] = None,
        max_candidates: int = 128,
        rng_seed: Optional[int] = None,
        safety_validator: Optional[Callable[[CrystallizedObjective, Mandate], Tuple[bool, List[str]]]] = None,
    ):
        self._spr_bank_loader = spr_bank_loader
        self._spr_bank: List[SPR] = []
        self._spr_bank_version: str = "unloaded"
        self.max_candidates = max_candidates
        self.scoring_fn = scoring_fn or self._default_scoring_fn
        self.rng = random.Random(rng_seed)
        self.safety_validator = safety_validator or self._default_safety_validator
        self._load_spr_bank()

    # -------------------------
    # Public API
    # -------------------------

    def generate(self, raw_mandate: Dict[str, Any], context: Optional[Dict[str, Any]] = None, mode: str = "deterministic") -> CrystallizedObjective:
        """
        End-to-end pipeline orchestrator following the 8-stage crystallization process.
        """
        # Stage 1: Intake & Normalization (⟦Q⟧)
        merged = {**(raw_mandate or {}), "context": {**(context or {}), **(raw_mandate.get("context", {}) or {})}}
        mandate = Mandate.normalize(merged)

        # determinism handling
        if mandate.seed is not None:
            self.rng.seed(mandate.seed)
        elif mode == "deterministic":
            # use stable hash of mandate id + text
            h = deterministic_hash({"id": mandate.id, "text": mandate.text})
            self.rng.seed(int(h[:16], 16))

        # Stage 2: Feature Extraction (⦅ ⦆)
        features = self._extract_features(mandate)

        # Stage 3: Temporal Scoping (Δ) + resonance analyses (H,T,F,C,E,Tr)
        temporal = self._build_temporal_scope(mandate, features)
        # attach detailed temporal analyses
        temporal.analysis_results = self._run_temporal_resonance_subsystems(mandate, features, temporal)

        # Stage 4: Candidate Retrieval
        candidates = self._retrieve_candidates(features, temporal)

        # Stage 5: Activation & Scoring (⊢)
        activated = self._activate_sprs(features, temporal, candidates, mode=mode)

        # Stage 6: Mandate Selection / Domain Customization (⊨)
        customized_activated = self._apply_mandate_customization(activated, mandate, temporal)

        # Stage 7: Template Assembly / Composition (⊧)
        draft_obj = self._compose_objective(customized_activated, temporal, mandate)

        # Stage 8: Validation + Finalization (◊)
        ok, reasons = self.safety_validator(draft_obj, mandate)
        draft_obj.explanations.extend(reasons)
        final_obj = self._finalize_objective(draft_obj, mandate, ok)

        # store provenance
        final_obj.metadata["spr_bank_version"] = self._spr_bank_version
        final_obj.metadata["mode"] = mode

        return final_obj

    # -------------------------
    # Stage helpers
    # -------------------------

    def _extract_features(self, mandate: Mandate) -> FeatureVector:
        """
        Deterministic lightweight NLP features + hash-based embeddings placeholder.
        """
        fv = FeatureVector()
        fv.numerical["priority"] = float(mandate.priority)
        fv.numerical["text_length"] = float(len(mandate.text or ""))
        fv.numerical["tag_count"] = float(len(mandate.tags))
        fv.categorical["issuer"] = mandate.issuer
        fv.categorical["domain"] = mandate.domain
        fv.categorical["top_tag"] = (mandate.tags[0] if mandate.tags else "none")
        # lightweight deterministic embedding: split sha into floats
        base = deterministic_hash({"id": mandate.id, "text": mandate.text})[:64]
        emb = []
        for i in range(16):
            chunk = base[i*4:(i+1)*4]
            val = int(chunk, 16) / float(0xFFFF)
            emb.append(float(val))
        fv.embeddings = emb
        # metadata: simple keyword extracts
        keywords = self._simple_keyword_extract(mandate.text)
        fv.metadata["keywords"] = keywords
        fv.timestamp = time.time()
        return fv

    def _simple_keyword_extract(self, text: str) -> List[str]:
        words = [w.strip(".,;:()[]").lower() for w in (text or "").split()]
        # naive frequency pick
        freq: Dict[str, int] = {}
        stop = {"the","and","is","a","of","to","in"}
        for w in words:
            if not w or w in stop or len(w) < 3:
                continue
            freq[w] = freq.get(w, 0) + 1
        # return top 6
        sorted_words = sorted(freq.items(), key=lambda x: -x[1])
        return [w for (w, _) in sorted_words[:6]]

    def _build_temporal_scope(self, mandate: Mandate, features: FeatureVector) -> TemporalScope:
        """
        Build Δ: compute start/end, granularity, horizons.
        """
        now = time.time()
        start = now
        end = mandate.deadline
        if end is None:
            if mandate.priority >= 9:
                end = now + 3600 * 6   # 6 hours
                granularity = "minute"
            elif mandate.priority >= 5:
                end = now + 3600 * 24  # 1 day
                granularity = "hour"
            else:
                end = now + 3600 * 24 * 30  # 30 days
                granularity = "day"
        else:
            delta = end - now
            if delta <= 3600 * 24:
                granularity = "hour"
            elif delta <= 3600 * 24 * 90:
                granularity = "day"
            else:
                granularity = "week"
        horizons = {
            "immediate": (start, start + 3600),
            "short": (start + 3600, start + 3600 * 24),
            "medium": (start + 3600 * 24, start + 3600 * 24 * 7),
            "long": (start + 3600 * 24 * 7, end)
        }
        return TemporalScope(start=start, end=end, granularity=granularity, horizons=horizons)

    def _run_temporal_resonance_subsystems(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        Run subcomponents H, T, F, C, E, Tr and return aggregated results.
        """
        results = {}
        results["H"] = self._historical_contextualization(mandate, features, temporal)
        results["T"] = self._temporal_dynamics(mandate, features, temporal)
        results["F"] = self._future_state_analysis(mandate, features, temporal)
        results["C"] = self._causal_lag_detection(mandate, features, temporal)
        results["E"] = self._emergence_over_time(mandate, features, temporal)
        results["Tr"] = self._trajectory_comparison(mandate, features, temporal)
        return results

    # Temporal subroutines (H, T, F, C, E, Tr)
    def _historical_contextualization(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        H: produce summary stats or signals about historical analogs.
        Here, placeholder: returns counts and similarity scores from metadata or context.
        """
        ctx = mandate.context or {}
        history_matches = ctx.get("historical_matches", [])
        score = 0.0
        if history_matches:
            score = clamp(len(history_matches) / 10.0)
        return {"matches_count": len(history_matches), "score": score, "examples": history_matches[:3]}

    def _temporal_dynamics(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        T: compute dynamics like time-to-impact heuristics or decay rates.
        """
        # naive heuristics: priority-driven urgency and expected reaction time
        urgency = clamp(features.numerical.get("priority", 1) / 10.0)
        expected_lag_seconds = (1.0 - urgency) * 3600 * 24  # lower urgency -> longer expected lag
        return {"urgency": urgency, "expected_lag_seconds": expected_lag_seconds}

    def _future_state_analysis(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        F: produce quick Monte-Carlo style or heuristic forecasts (lightweight).
        """
        # placeholder: produce n candidate futures with score proxies
        futures = []
        for i in range(3):
            trend = clamp(0.5 + 0.1 * i + 0.1 * features.numerical.get("priority", 1) / 10.0)
            futures.append({"id": f"fut_{i}", "trend_score": trend})
        return {"futures": futures}

    def _causal_lag_detection(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        C: estimate causal lags between action and outcome
        """
        # heuristic: based on keyword presence and priority
        if "deployment" in (features.metadata.get("keywords") or []):
            lag = 3600 * 24
        else:
            lag = 3600 * 6
        return {"estimated_causal_lag_seconds": lag}

    def _emergence_over_time(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        E: detect risk of emergent non-linear effects (placeholder heuristic)
        """
        # heuristics: many keywords => more emergence risk
        kw_count = len(features.metadata.get("keywords") or [])
        risk = clamp(kw_count / 6.0)
        return {"emergence_risk": risk}

    def _trajectory_comparison(self, mandate: Mandate, features: FeatureVector, temporal: TemporalScope) -> Dict[str, Any]:
        """
        Tr: compare candidate trajectories — here returns similarity matrix stub
        """
        # naive: return three synthetic trajectories distances
        trajs = [{"id": "t0", "divergence": 0.1}, {"id": "t1", "divergence": 0.4}, {"id": "t2", "divergence": 0.75}]
        return {"trajectories": trajs}

    def _retrieve_candidates(self, features: FeatureVector, temporal: TemporalScope) -> List[SPR]:
        """
        Stage 4: candidate retrieval using tag overlap, signature hints, and cheap embedding similarity.
        """
        if not self._spr_bank:
            self._load_spr_bank()
        tag_set = set()
        top_tag = features.categorical.get("top_tag")
        if top_tag:
            tag_set.add(top_tag)
        # scoring pool
        scored: List[Tuple[float, SPR]] = []
        for spr in self._spr_bank:
            score = 0.0
            # tag overlap
            score += len(tag_set.intersection(set(spr.tags))) * 0.4
            # signature domain match
            if spr.signature.get("domain") and spr.signature.get("domain") == features.categorical.get("domain"):
                score += 0.3
            # temporal hint compatibility
            if spr.temporal_hint and spr.temporal_hint in temporal.horizons:
                score += 0.1
            # embedding proxy match if available
            se = spr.metadata.get("embeddings")
            if se and features.embeddings:
                n = min(len(se), len(features.embeddings))
                dot = sum(se[i] * features.embeddings[i] for i in range(n))
                score += clamp((dot / max(1.0, n)) * 0.2, 0.0, 0.2)
            if score > 0.0:
                scored.append((score, spr))
        scored.sort(key=lambda x: -x[0])
        picked = [s for (_, s) in scored[:self.max_candidates]]
        return picked

    def _activate_sprs(self, features: FeatureVector, temporal: TemporalScope, candidates: List[SPR], mode: str = "deterministic") -> List[ActivatedSPR]:
        """
        Stage 5: compute score + breakdown for each candidate and return ActivatedSPR list (⊢).
        """
        scored: List[Tuple[float, SPR, Dict[str, float]]] = []
        for spr in candidates:
            base_score = self.scoring_fn(features, spr, temporal)
            tag_boost = 0.05 * sum(1 for t in spr.tags if t in (features.metadata.get("keywords") or []))
            time_boost = 0.05 if spr.temporal_hint and spr.temporal_hint in temporal.horizons else 0.0
            temporal_resonance_bonus = 0.0
            # if M6-like resonance requested in mandate context, apply resonance heuristics later; for now leave zero
            final = clamp(base_score + tag_boost + time_boost + temporal_resonance_bonus, 0.0, 1.0)
            breakdown = {"base": base_score, "tag_boost": tag_boost, "time_boost": time_boost}
            scored.append((final, spr, breakdown))
        if mode == "explore":
            # probabilistic sampling proportional to score
            weights = [s for (s, _, _) in scored]
            total = sum(weights) + 1e-9
            probs = [w / total for w in weights]
            chosen = set()
            for _ in range(min(len(scored), max(1, int(len(scored) * 0.5)))):
                idx = self._sample_index(probs)
                chosen.add(idx)
            activated = []
            for idx in chosen:
                final_score, spr, breakdown = scored[idx]
                activated.append(ActivatedSPR(
                    spr_id=spr.id, spr_name=spr.name, weight=float(final_score),
                    score_breakdown=breakdown, matched_features={"top_tag": features.categorical.get("top_tag")},
                    provenance={"mode": mode}
                ))
            activated.sort(key=lambda a: -a.weight)
            return activated
        else:
            scored.sort(key=lambda x: -x[0])
            activated = []
            for final_score, spr, breakdown in scored[: self.max_candidates]:
                activated.append(ActivatedSPR(
                    spr_id=spr.id, spr_name=spr.name, weight=float(final_score),
                    score_breakdown=breakdown, matched_features={"top_tag": features.categorical.get("top_tag")},
                    provenance={"mode": mode}
                ))
            return activated

    def _apply_mandate_customization(self, activated: List[ActivatedSPR], mandate: Mandate, temporal: TemporalScope) -> List[ActivatedSPR]:
        """
        Stage 6: apply Mandate-level customizations (⊨). For known Mandates M₆ and M₉, adjust weights and add constraints.
        """
        out: List[ActivatedSPR] = []
        for a in activated:
            spr = self._lookup_spr(a.spr_id)
            # deep copy of activation
            new_act = ActivatedSPR(
                spr_id=a.spr_id, spr_name=a.spr_name, weight=a.weight,
                score_breakdown=dict(a.score_breakdown), matched_features=dict(a.matched_features),
                activated_at=a.activated_at, provenance=dict(a.provenance)
            )
            # If Mandate M6 (Temporal Resonance), prioritize SPRs with temporal_hint matching high-urgency horizons
            mtype = mandate.context.get("mandate_type") or mandate.context.get("mandate_symbol")
            if mtype in ("M6","M₆","M_6","M6:TemporalResonance"):
                if spr.temporal_hint in ("immediate","short","medium"):
                    new_act.weight = clamp(new_act.weight + 0.08, 0.0, 1.0)
                    new_act.provenance["mandate_adjustment"] = "M6_temporal_boost"
            if mtype in ("M9","M₉","M_9","M9:ComplexVision"):
                # prefer SPRs that mention systemic/meta tags
                if "system" in (spr.tags or []) or spr.signature.get("complex_system"):
                    new_act.weight = clamp(new_act.weight + 0.06, 0.0, 1.0)
                    new_act.provenance["mandate_adjustment"] = "M9_system_boost"
            out.append(new_act)
        # renormalize weights
        total = sum(a.weight for a in out) + 1e-9
        for a in out:
            a.weight = a.weight / total
        out.sort(key=lambda x: -x.weight)
        return out

    def _compose_objective(self, activated: List[ActivatedSPR], temporal: TemporalScope, mandate: Mandate) -> CrystallizedObjective:
        """
        Stage 7: assemble activated SPRs into a CrystallizedObjective (⊧).
        """
        steps: List[Step] = []
        explanations: List[str] = []
        outputs_used = set()
        idx = 0
        # greedily create steps from top activated SPRs
        for a in activated:
            spr = self._lookup_spr(a.spr_id)
            if not spr:
                continue
            # create step
            step_id = f"step-{idx}-{spr.id}"
            desc = spr.pattern
            deps = []
            # naive precondition linking: if a precondition key appears in any previous step outputs, link it
            for k in (spr.preconditions or {}).keys():
                for s in steps:
                    if k in s.outputs:
                        deps.append(s.id)
            est_cost = float(spr.cost) * (1.0 / (a.weight + 1e-6))
            temporal_window = None
            if spr.temporal_hint and spr.temporal_hint in temporal.horizons:
                start, end = temporal.horizons.get(spr.temporal_hint, (temporal.start, temporal.end))
                temporal_window = {"start": start or temporal.start, "end": end or temporal.end}
            step_outputs = dict(spr.effects or {})
            # conflict detection
            conflict = False
            for out in step_outputs.keys():
                if out in outputs_used:
                    explanations.append(f"conflict: output '{out}' duplicated by SPR {spr.id}, skipping")
                    conflict = True
                    break
            if conflict:
                continue
            outputs_used.update(step_outputs.keys())
            step = Step(
                id=step_id, title=spr.name, description=desc,
                dependencies=deps, estimated_cost=est_cost, temporal_window=temporal_window,
                outputs=step_outputs, metadata={"activ_weight": a.weight}
            )
            steps.append(step)
            idx += 1
            if len(steps) >= 64:
                break
        # scoring acceptance: combine avg activation weight and coverage of mandate tags
        if activated:
            avg_weight = sum(a.weight for a in activated) / max(1, len(activated))
        else:
            avg_weight = 0.0
        mandate_tags = set(mandate.tags)
        covered = 0
        for s in steps:
            blob = (s.title + " " + s.description + " " + json.dumps(s.outputs)).lower()
            for t in mandate_tags:
                if t.lower() in blob:
                    covered += 1
        coverage_score = clamp(float(covered) / max(1, len(mandate_tags))) if mandate_tags else 1.0
        acceptance_score = clamp(0.7 * avg_weight + 0.3 * coverage_score, 0.0, 1.0)
        obj = CrystallizedObjective(
            id=str(uuid.uuid4()), mandate_id=mandate.id, steps=steps,
            acceptance_score=acceptance_score, explanations=explanations,
            temporal_scope=temporal, metadata={"activated_count": len(activated)}
        )
        return obj

    def _finalize_objective(self, obj: CrystallizedObjective, mandate: Mandate, ok: bool) -> CrystallizedObjective:
        """
        Stage 8: finalize and fingerprint.
        """
        if not ok:
            obj.acceptance_score = clamp(obj.acceptance_score * 0.5, 0.0, 1.0)
            obj.metadata["finalized_warning"] = True
        else:
            obj.metadata["finalized_warning"] = False
        obj.metadata["fingerprint"] = deterministic_hash({
            "mandate_id": obj.mandate_id, "steps": [s.id for s in obj.steps], "ts": obj.created_at, "version": obj.version
        })
        return obj

    # -------------------------
    # Scoring & Validation (pluggable)
    # -------------------------

    def _default_scoring_fn(self, features: FeatureVector, spr: SPR, temporal: TemporalScope) -> float:
        """
        Default hybrid heuristic scoring:
        - tag/domain alignment
        - cheap embedding dot proxy (if available)
        - temporal compatibility
        Returns value in [0,1]
        """
        score = 0.0
        top_tag = features.categorical.get("top_tag")
        if top_tag and top_tag in spr.tags:
            score += 0.4
        # domain signature
        if spr.signature.get("domain") and spr.signature.get("domain") == features.categorical.get("domain"):
            score += 0.2
        # cheap embedding proxy
        se = spr.metadata.get("embeddings")
        if se and features.embeddings:
            n = min(len(se), len(features.embeddings))
            dot = sum(se[i] * features.embeddings[i] for i in range(n))
            score += clamp((dot / max(1.0, n)) * 0.3, 0.0, 0.3)
        # penalty for cost
        score -= clamp(0.03 * spr.cost, 0.0, 0.15)
        return clamp(score, 0.0, 1.0)

    def _default_safety_validator(self, obj: CrystallizedObjective, mandate: Mandate) -> Tuple[bool, List[str]]:
        """
        Ensures constraints from mandate are satisfied.
        """
        reasons: List[str] = []
        ok = True
        # budget constraint
        budget = mandate.constraints.get("budget")
        total_cost = sum(s.estimated_cost for s in (obj.steps or []))
        if budget is not None and total_cost > float(budget):
            ok = False
            reasons.append(f"budget_exceeded: estimated {total_cost:.2f} > budget {budget}")
        # forbidden outputs
        forbidden = set(mandate.constraints.get("forbidden_outputs", []))
        for s in obj.steps:
            common = set(s.outputs.keys()).intersection(forbidden)
            if common:
                ok = False
                reasons.append(f"forbidden_outputs_in_step {s.id}: {sorted(list(common))}")
        # deadline compatibility: naive check if any step ends before deadline
        if mandate.deadline:
            fits = any(s.temporal_window and s.temporal_window.get("end") and s.temporal_window["end"] <= mandate.deadline for s in obj.steps)
            if not fits:
                ok = False
                reasons.append("no_step_fits_deadline")
        return ok, reasons

    # -------------------------
    # SPR Bank management & loaders
    # -------------------------

    def _load_spr_bank(self) -> None:
        try:
            sprs = self._spr_bank_loader()
            normalized: List[SPR] = []
            for s in sprs:
                if isinstance(s, SPR):
                    normalized.append(s)
                elif isinstance(s, dict):
                    normalized.append(SPR(
                        id=s.get("id", str(uuid.uuid4())),
                        name=s.get("name", s.get("id", "unnamed")),
                        tags=s.get("tags", []),
                        signature=s.get("signature", {}),
                        pattern=s.get("pattern", ""),
                        preconditions=s.get("preconditions", {}),
                        effects=s.get("effects", {}),
                        cost=float(s.get("cost", 1.0)),
                        temporal_hint=s.get("temporal_hint"),
                        metadata=s.get("metadata", {})
                    ))
            self._spr_bank = normalized
            self._spr_bank_version = deterministic_hash([s.id for s in self._spr_bank])[:12]
        except Exception as e:
            self._spr_bank = []
            self._spr_bank_version = "empty"

    def _lookup_spr(self, spr_id: str) -> Optional[SPR]:
        for s in self._spr_bank:
            if s.id == spr_id:
                return s
        return None

    # -------------------------
    # Symbolic header parser (for input like: ⟦Q⟧→⦅...⦆→⊢... )
    # -------------------------

    def parse_symbolic_header(self, header: str) -> Dict[str, Any]:
        """
        Parse a compact symbolic header into a structured dict.
        Example header: "⟦Q⟧→⦅temporal:[circ...→Δ⦅explicit...→⊢H⊢T→⊨M₆⊨Ω→⊧T→⊨D→⟧PD⟧"
        This parser is conservative: it maps symbols we know into keys.
        """
        mapping = {
            "⟦": "query_start", "⟧": "query_end",
            "⦅": "feature_start", "⦆": "feature_end",
            "⊢": "activate",
            "⊨": "mandate_select",
            "⊧": "template_assemble",
            "Δ": "temporal_scope",
            "Ω": "cognitive_resonance",
            "H": "historical_contextualization",
            "T": "temporal_dynamics",
            "F": "future_state_analysis",
            "C": "causal_lag_detection",
            "E": "emergence_over_time",
            "Tr": "trajectory_comparison",
            "M₆": "mandate_M6",
            "M₉": "mandate_M9",
            "◊": "final_objective"
        }
        result: Dict[str, Any] = {"raw": header, "symbols": []}
        for sym, name in mapping.items():
            if sym in header:
                result["symbols"].append(name)
        return result

    # -------------------------
    # Helper utilities
    # -------------------------

    def _sample_index(self, probs: List[float]) -> int:
        r = self.rng.random()
        cum = 0.0
        for i, p in enumerate(probs):
            cum += p
            if r <= cum:
                return i
        return max(0, len(probs) - 1)

    # -------------------------
    # Example static loaders
    # -------------------------

    @staticmethod
    def load_sprs_from_json(path: str) -> List[SPR]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = []
        for item in data:
            out.append(SPR(
                id=item.get("id", str(uuid.uuid4())),
                name=item.get("name", item.get("id", "unnamed")),
                tags=item.get("tags", []),
                signature=item.get("signature", {}),
                pattern=item.get("pattern", ""),
                preconditions=item.get("preconditions", {}),
                effects=item.get("effects", {}),
                cost=float(item.get("cost", 1.0)),
                temporal_hint=item.get("temporal_hint"),
                metadata=item.get("metadata", {})
            ))
        return out

    @staticmethod
    def example_spr_bank() -> List[SPR]:
        return [
            SPR(
                id="spr-lookup-001",
                name="SearchMemoryAndGround",
                tags=["search","memory","grounding"],
                signature={"domain":"cognitive"},
                pattern="Search agent memory, memory store, and grounding sources to retrieve precedent artifacts.",
                preconditions={},
                effects={"memory_snippet":"text"},
                cost=0.8,
                temporal_hint="short",
                metadata={"description":"Ground user query in prior knowledge"}
            ),
            SPR(
                id="spr-sim-001",
                name="SimulateCounterfactuals",
                tags=["simulate","forecast","ensemble"],
                signature={"domain":"cognitive","complex_system":True},
                pattern="Run lightweight counterfactual simulations across state-space dimensions.",
                preconditions={},
                effects={"ensemble_outcomes":"list"},
                cost=2.0,
                temporal_hint="medium",
                metadata={"description":"Generate projected futures"}
            ),
            SPR(
                id="spr-plan-001",
                name="DecomposePlan",
                tags=["plan","decompose","task"],
                signature={"domain":"cognitive"},
                pattern="Decompose objective into sequential steps with dependencies and acceptance criteria.",
                preconditions={},
                effects={"plan":"steps"},
                cost=1.5,
                temporal_hint="medium",
                metadata={"description":"Planning primitive"}
            ),
            SPR(
                id="spr-validate-001",
                name="ConstraintValidator",
                tags=["validate","safety"],
                signature={"domain":"cognitive"},
                pattern="Validate proposed plan against constraints, ethics, and safety policies.",
                preconditions={},
                effects={"validation_report":"json"},
                cost=0.5,
                temporal_hint="short",
                metadata={"description":"Validation primitive"}
            )
        ]


