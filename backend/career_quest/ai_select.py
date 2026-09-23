from __future__ import annotations

import json
import time

from openai import APIError, APITimeoutError, OpenAI

MAX_RECOMMENDATIONS = 3
FACTORS = (
    "grade",
    "skill_gap",
    "participation_history",
    "next_level_requirements",
)
SERVER_FIELDS = (
    "event_id",
    "title",
    "type",
    "format",
    "duration_hours",
    "upcoming_sessions",
    "target",
    "gaps",
    "critical_gaps",
    "potential_skill_changes",
    "participation",
)
SYSTEM_INSTRUCTIONS = (
    "You are a constrained career-development ranking layer. "
    "You may only select activities supplied in candidates. "
    "All numeric facts are authoritative and must not be recalculated. "
    "Never invent an activity, skill, requirement or participation fact. "
    "Rank the best 1-3 next development activities. "
    "Consider all four factors: current grade, actual skill gaps, "
    "participation history, and requirements of the next grade. "
    "Critical next-grade gaps deserve special attention. "
    "Past no_show, declined and dropped are signals, not permanent bans. "
    "If there is no negative participation, say that relevant negative "
    "participation history is absent. "
    "Do not decide a promotion and do not say the employee is ready for promotion. "
    "You may state how many next-grade requirements are already met. "
    "Write reasoning_summary, tradeoff and comparison.summary in Russian. "
    "Return only the requested structured result. "
    "When only one candidate exists, comparison must be null. "
    "Otherwise chosen_event_id must be rank 1 and alternative_event_id must differ."
)


def select_recommendations(
    candidates_payload: dict[str, object],
    *,
    api_key: str | None,
    model: str,
    timeout_seconds: float,
    context: dict[str, object] | None = None,
    complete=None,
) -> dict[str, object]:
    facts = list(candidates_payload.get("candidates") or [])
    if not facts:
        return _envelope(
            used_ai=False,
            selection_status="not_applicable",
            model=None,
            latency_ms=0,
            fallback_reason=None,
            recommendations=[],
            comparison=None,
        )
    if not api_key:
        return _fallback(facts, model=None, reason="missing_api_key", latency_ms=0)
    payload = _model_payload(facts, context or {})
    caller = complete or _openai_complete
    started = time.perf_counter()
    try:
        raw = caller(api_key, model, timeout_seconds, payload)
    except (TimeoutError, APITimeoutError):
        return _fallback(
            facts,
            model=model,
            reason="timeout",
            latency_ms=_elapsed(started),
        )
    except APIError:
        return _fallback(
            facts,
            model=model,
            reason="provider_error",
            latency_ms=_elapsed(started),
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return _fallback(
            facts,
            model=model,
            reason="invalid_ai_output",
            latency_ms=_elapsed(started),
        )
    except Exception:
        return _fallback(
            facts,
            model=model,
            reason="provider_error",
            latency_ms=_elapsed(started),
        )
    try:
        chosen, comparison = _validated(raw, facts)
    except (TypeError, ValueError, KeyError):
        return _fallback(
            facts,
            model=model,
            reason="invalid_ai_output",
            latency_ms=_elapsed(started),
        )
    by_id = {item["event_id"]: item for item in facts}
    recommendations = [
        _enrich(by_id[item["event_id"]], item)
        for item in chosen
    ]
    return _envelope(
        used_ai=True,
        selection_status="ai_ranked",
        model=model,
        latency_ms=_elapsed(started),
        fallback_reason=None,
        recommendations=recommendations,
        comparison=_comparison_payload(comparison, by_id, recommendations),
    )


def _fallback(
    facts: list[dict],
    *,
    model: str | None,
    reason: str,
    latency_ms: int,
) -> dict[str, object]:
    ordered = sorted(facts, key=_fallback_key)[:MAX_RECOMMENDATIONS]
    recommendations = []
    for index, candidate in enumerate(ordered, start=1):
        alternative = ordered[1]["event_id"] if index == 1 and len(ordered) > 1 else None
        recommendations.append(
            _enrich(
                candidate,
                {
                    "reasoning_summary": _fallback_summary(candidate),
                    "factor_types": list(FACTORS),
                    "tradeoff": _fallback_tradeoff(candidate, alternative, ordered),
                },
            )
        )
    comparison = None
    if len(ordered) > 1:
        comparison = _comparison_payload(
            {
                "chosen_event_id": ordered[0]["event_id"],
                "alternative_event_id": ordered[1]["event_id"],
                "summary": _fallback_tradeoff(
                    ordered[0], ordered[1]["event_id"], ordered
                ),
            },
            {item["event_id"]: item for item in facts},
            recommendations,
        )
    return _envelope(
        used_ai=False,
        selection_status="fallback_ranked",
        model=model,
        latency_ms=latency_ms,
        fallback_reason=reason,
        recommendations=recommendations,
        comparison=comparison,
    )


def _envelope(**payload: object) -> dict[str, object]:
    return payload


def _elapsed(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def _model_payload(facts: list[dict], context: dict[str, object]) -> dict[str, object]:
    safe_context = {
        key: context[key]
        for key in (
            "role",
            "grade",
            "primary_target",
            "requirements_met_count",
            "requirements_total",
            "requirement_gaps",
        )
        if key in context
    }
    return {
        "employee": safe_context,
        "candidates": [_slim_candidate(item) for item in facts],
    }


def _slim_candidate(item: dict) -> dict[str, object]:
    counts = item["participation"]["event_status_counts"]
    return {
        "event_id": item["event_id"],
        "title": item["title"],
        "type": item["type"],
        "format": item["format"],
        "duration_hours": item["duration_hours"],
        "impacted_gaps": [
            {
                "skill_id": gap["skill_id"],
                "missing_level": gap["missing_level"],
                "critical": gap["critical"],
            }
            for gap in item["gaps"]
        ],
        "critical_gaps": list(item["critical_gaps"]),
        "potential_skill_deltas": [
            {"skill_id": change["skill_id"], "delta": change["delta"]}
            for change in item["potential_skill_changes"]
        ],
        "prerequisites_already_verified": [
            {
                "skill_id": check["skill_id"],
                "met": check["met"],
            }
            for check in item["prerequisites"]
        ],
        "participation_counts": {
            "completed": counts.get("completed", 0),
            "no_show": counts.get("no_show", 0),
            "declined": counts.get("declined", 0),
            "dropped": counts.get("dropped", 0),
        },
    }


def _validated(raw: dict, facts: list[dict]) -> tuple[list[dict], dict | None]:
    if not isinstance(raw, dict):
        raise ValueError("object")
    items = raw.get("recommendations")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_RECOMMENDATIONS:
        raise ValueError("count")
    allowed = {item["event_id"] for item in facts}
    seen: set[str] = set()
    ranks: list[int] = []
    chosen: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("item")
        event_id = item.get("event_id")
        factors = item.get("factor_types")
        if event_id not in allowed or event_id in seen:
            raise ValueError("event")
        if not isinstance(item.get("reasoning_summary"), str) or not item["reasoning_summary"].strip():
            raise ValueError("summary")
        if not isinstance(item.get("tradeoff"), str) or not item["tradeoff"].strip():
            raise ValueError("tradeoff")
        if not isinstance(factors, list):
            raise ValueError("factors")
        distinct = []
        for factor in factors:
            if factor not in FACTORS or factor in distinct:
                continue
            distinct.append(factor)
        if len(distinct) < 3 or any(factor not in FACTORS for factor in factors):
            raise ValueError("factors")
        rank = item.get("rank")
        if not isinstance(rank, int):
            raise ValueError("rank")
        seen.add(event_id)
        ranks.append(rank)
        chosen.append(
            {
                "event_id": event_id,
                "rank": rank,
                "reasoning_summary": item["reasoning_summary"].strip(),
                "factor_types": distinct,
                "tradeoff": item["tradeoff"].strip(),
            }
        )
    if ranks != list(range(1, len(chosen) + 1)):
        ordered = sorted(chosen, key=lambda item: item["rank"])
        if [item["rank"] for item in ordered] != list(range(1, len(chosen) + 1)):
            raise ValueError("ranks")
        chosen = ordered
    else:
        chosen = sorted(chosen, key=lambda item: item["rank"])
    comparison = raw.get("comparison")
    if len(facts) == 1:
        if comparison is not None:
            raise ValueError("comparison")
        return chosen, None
    if not isinstance(comparison, dict):
        raise ValueError("comparison")
    chosen_id = comparison.get("chosen_event_id")
    alternative_id = comparison.get("alternative_event_id")
    summary = comparison.get("summary")
    if chosen_id != chosen[0]["event_id"] or alternative_id not in allowed or alternative_id == chosen_id:
        raise ValueError("comparison ids")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("comparison summary")
    return chosen, {
        "chosen_event_id": chosen_id,
        "alternative_event_id": alternative_id,
        "summary": summary.strip(),
    }


def _enrich(candidate: dict, text: dict) -> dict[str, object]:
    enriched = {field: candidate[field] for field in SERVER_FIELDS}
    enriched["reasoning_summary"] = text["reasoning_summary"]
    enriched["factor_types"] = list(text["factor_types"])
    enriched["tradeoff"] = text["tradeoff"]
    return enriched


def _comparison_payload(
    comparison: dict | None,
    by_id: dict[str, dict],
    recommendations: list[dict],
) -> dict[str, object] | None:
    if comparison is None:
        return None
    chosen = next(
        item for item in recommendations
        if item["event_id"] == comparison["chosen_event_id"]
    )
    alternative = _server_facts(by_id[comparison["alternative_event_id"]])
    return {
        "chosen_event": chosen,
        "alternative_event": alternative,
        "summary": comparison["summary"],
    }


def _server_facts(candidate: dict) -> dict[str, object]:
    return {field: candidate[field] for field in SERVER_FIELDS}


def _fallback_key(item: dict) -> tuple:
    gap_ids = {gap["skill_id"] for gap in item["gaps"]}
    deltas = [
        change["delta"]
        for change in item["potential_skill_changes"]
        if change["skill_id"] in gap_ids and change["delta"] > 0
    ]
    counts = item["participation"]["event_status_counts"]
    negative = sum(counts.get(name, 0) for name in ("no_show", "declined", "dropped"))
    return (
        -len(item["critical_gaps"]),
        -sum(deltas),
        -len(deltas),
        negative,
        item["event_id"],
    )


def _negative_count(item: dict) -> int:
    counts = item["participation"]["event_status_counts"]
    return sum(counts.get(name, 0) for name in ("no_show", "declined", "dropped"))


def _target_delta(item: dict) -> int:
    gap_ids = {gap["skill_id"] for gap in item["gaps"]}
    return sum(
        change["delta"]
        for change in item["potential_skill_changes"]
        if change["skill_id"] in gap_ids and change["delta"] > 0
    )


def _fallback_summary(item: dict) -> str:
    negative = _negative_count(item)
    history = (
        "Релевантной негативной истории участия нет."
        if negative == 0
        else (
            f"Негативные статусы участия: {negative}. "
            "Это сигнал, а не запрет."
        )
    )
    return (
        f"Сервер уже проверил грейд и допуск. Активность закрывает "
        f"{len(item['critical_gaps'])} критических разрывов следующего грейда "
        f"и даёт суммарный прирост {_target_delta(item)} по целевым навыкам. "
        f"{history}"
    )


def _fallback_tradeoff(item: dict, alternative_id: str | None, ordered: list[dict]) -> str:
    if alternative_id is None:
        return "Другого допустимого занятия в этом списке нет."
    other = next(candidate for candidate in ordered if candidate["event_id"] == alternative_id)
    return (
        f"{item['event_id']} стоит выше {alternative_id}: "
        f"критических разрывов {len(item['critical_gaps'])} против {len(other['critical_gaps'])}, "
        f"прирост по цели {_target_delta(item)} против {_target_delta(other)}, "
        f"негативных участий {_negative_count(item)} против {_negative_count(other)}."
    )


def _openai_complete(
    api_key: str,
    model: str,
    timeout_seconds: float,
    payload: dict[str, object],
) -> dict:
    client = OpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=0)
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=json.dumps(payload, ensure_ascii=False),
        text={
            "format": {
                "type": "json_schema",
                "name": "career_recommendations",
                "strict": True,
                "schema": _schema(),
            }
        },
    )
    parsed = json.loads(response.output_text)
    if not isinstance(parsed, dict):
        raise ValueError("openai response was not an object")
    return parsed


def _schema() -> dict[str, object]:
    recommendation = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "event_id",
            "rank",
            "reasoning_summary",
            "factor_types",
            "tradeoff",
        ],
        "properties": {
            "event_id": {"type": "string"},
            "rank": {"type": "integer"},
            "reasoning_summary": {"type": "string"},
            "factor_types": {
                "type": "array",
                "items": {"type": "string", "enum": list(FACTORS)},
            },
            "tradeoff": {"type": "string"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["recommendations", "comparison"],
        "properties": {
            "recommendations": {
                "type": "array",
                "items": recommendation,
            },
            "comparison": {
                "anyOf": [
                    {"type": "null"},
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "chosen_event_id",
                            "alternative_event_id",
                            "summary",
                        ],
                        "properties": {
                            "chosen_event_id": {"type": "string"},
                            "alternative_event_id": {"type": "string"},
                            "summary": {"type": "string"},
                        },
                    },
                ]
            },
        },
    }
