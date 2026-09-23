from __future__ import annotations

import json
import urllib.error
import urllib.request

MAX_RECOMMENDATIONS = 3


def select_recommendations(
    candidates_payload: dict[str, object],
    *,
    api_key: str | None,
    model: str,
    timeout_seconds: float,
    complete=None,
) -> dict[str, object]:
    facts = list(candidates_payload.get("candidates") or [])
    status = candidates_payload.get("candidate_status")
    if not facts:
        return _empty(status, "not_applicable", None)
    if not api_key:
        return _empty(status, "fallback", "missing_api_key")
    allowed = {item["event_id"]: item for item in facts}
    caller = complete or _openai_complete
    try:
        raw = caller(
            api_key,
            model,
            timeout_seconds,
            _messages(facts),
        )
        chosen = _validated(raw, allowed)
    except (OSError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return _empty(status, "fallback", "invalid_ai_response")
    return {
        "used_ai": True,
        "selection_status": "selected",
        "fallback_reason": None,
        "model": model,
        "candidate_status": status,
        "recommendations": [
            {
                "event_id": item["event_id"],
                "title": allowed[item["event_id"]]["title"],
                "format": allowed[item["event_id"]]["format"],
                "upcoming_sessions": list(
                    allowed[item["event_id"]]["upcoming_sessions"]
                ),
                "why": item["why"],
                "alternative_event_id": item["alternative_event_id"],
                "why_not_alternative": item["why_not_alternative"],
            }
            for item in chosen
        ],
    }


def _empty(status: object, selection_status: str, reason: str | None) -> dict[str, object]:
    return {
        "used_ai": False,
        "selection_status": selection_status,
        "fallback_reason": reason,
        "model": None,
        "candidate_status": status,
        "recommendations": [],
    }


def _messages(facts: list[dict]) -> list[dict[str, str]]:
    slim = [
        {
            "event_id": item["event_id"],
            "title": item["title"],
            "type": item["type"],
            "format": item["format"],
            "duration_hours": item["duration_hours"],
            "critical_gaps": item["critical_gaps"],
            "potential_skill_changes": [
                {
                    "skill_id": change["skill_id"],
                    "delta": change["delta"],
                    "current_level": change["current_level"],
                    "new_level": change["new_level"],
                }
                for change in item["potential_skill_changes"]
            ],
            "participation": item["participation"],
        }
        for item in facts
    ]
    return [
        {
            "role": "system",
            "content": (
                "Choose 1 to 3 activities only from the supplied event_id list. "
                "Do not invent events, skills, levels, requirements, or history. "
                "Do not assign numeric scores. Explain in Russian why each chosen "
                "activity is preferable to one other supplied alternative. "
                'Return JSON {"recommendations":[{"event_id":"","why":"",'
                '"alternative_event_id":null,"why_not_alternative":""}]}.'
            ),
        },
        {"role": "user", "content": json.dumps({"eligible": slim}, ensure_ascii=False)},
    ]


def _validated(raw: dict, allowed: dict[str, dict]) -> list[dict[str, object]]:
    items = raw.get("recommendations")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_RECOMMENDATIONS:
        raise ValueError("recommendation count")
    seen: set[str] = set()
    chosen = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("recommendation shape")
        event_id = item.get("event_id")
        alternative = item.get("alternative_event_id")
        why = item.get("why")
        why_not = item.get("why_not_alternative")
        if event_id not in allowed or event_id in seen or not isinstance(why, str) or not why.strip():
            raise ValueError("event")
        if len(allowed) > 1:
            if alternative not in allowed or alternative == event_id:
                raise ValueError("alternative")
            if not isinstance(why_not, str) or not why_not.strip():
                raise ValueError("comparison")
        elif alternative not in (None, ""):
            raise ValueError("unexpected alternative")
        seen.add(event_id)
        chosen.append(
            {
                "event_id": event_id,
                "why": why.strip(),
                "alternative_event_id": alternative or None,
                "why_not_alternative": "" if not isinstance(why_not, str) else why_not.strip(),
            }
        )
    return chosen


def _openai_complete(api_key: str, model: str, timeout_seconds: float, messages: list[dict[str, str]]) -> dict:
    body = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": messages,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        exc.read()
        raise ValueError("openai_http") from exc
    content = payload["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("openai_json")
    return parsed
