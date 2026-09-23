import json

from openai import APIError

from backend.career_quest.ai_select import select_recommendations

FACTORS = [
    "grade",
    "skill_gap",
    "participation_history",
    "next_level_requirements",
]


def _candidate(event_id: str, *, critical: int = 1, delta: int = 1, negative: int = 0) -> dict:
    return {
        "event_id": event_id,
        "title": f"Activity {event_id}",
        "type": "course",
        "format": "self_paced",
        "duration_hours": 2,
        "upcoming_sessions": [],
        "target": {"role": "Engineer", "grade": "Middle"},
        "gaps": [
            {
                "skill_id": "S_ARCH",
                "current_level": 1,
                "required_level": 2,
                "missing_level": 1,
                "critical": True,
            }
        ],
        "critical_gaps": ["S_ARCH"] * critical,
        "prerequisites": [{"skill_id": "S_CODE", "current_level": 2, "required_level": 1, "met": True}],
        "potential_skill_changes": [
            {
                "skill_id": "S_ARCH",
                "current_level": 1,
                "gain": delta,
                "max_level": 5,
                "delta": delta,
                "new_level": 1 + delta,
            }
        ],
        "participation": {
            "event_status_counts": {
                "no_show": negative,
                "declined": 0,
                "dropped": 0,
            },
            "related_skill_negative_status_counts": {"S_ARCH": {"no_show": 9}},
        },
    }


def _facts(*candidates: dict) -> dict:
    return {"candidate_status": "candidates_available", "candidates": list(candidates)}


def _ai_item(event_id: str, rank: int, alternative: str | None = None) -> dict:
    return {
        "event_id": event_id,
        "rank": rank,
        "reasoning_summary": "Закрывает разрыв следующего грейда.",
        "factor_types": FACTORS,
        "tradeoff": "Сильнее альтернативы по критическому разрыву.",
    }


def _valid(event_ids: list[str]) -> dict:
    return {
        "recommendations": [
            _ai_item(event_id, index)
            for index, event_id in enumerate(event_ids, start=1)
        ],
        "comparison": None
        if len(event_ids) == 1
        else {
            "chosen_event_id": event_ids[0],
            "alternative_event_id": event_ids[1],
            "summary": "Первое сильнее закрывает критический разрыв.",
        },
    }


def _run(facts, raw=None, *, api_key="test-key", context=None, error=None):
    seen = {}

    def complete(key, model, timeout, payload):
        seen["payload"] = payload
        seen["key"] = key
        if error is not None:
            raise error
        return raw

    result = select_recommendations(
        facts,
        api_key=api_key,
        model="gpt-5.6-terra",
        timeout_seconds=7,
        context=context,
        complete=complete,
    )
    return result, seen


def test_ai_selects_only_supplied_candidates() -> None:
    facts = _facts(_candidate("EV_A"), _candidate("EV_B", critical=0))
    raw = _valid(["EV_A"])
    raw["comparison"] = {
        "chosen_event_id": "EV_A",
        "alternative_event_id": "EV_B",
        "summary": "Первое сильнее закрывает критический разрыв.",
    }
    result, seen = _run(facts, raw)
    assert result["used_ai"] is True
    assert result["selection_status"] == "ai_ranked"
    assert result["model"] == "gpt-5.6-terra"
    assert [item["event_id"] for item in result["recommendations"]] == ["EV_A"]
    assert result["recommendations"][0]["title"] == "Activity EV_A"
    assert result["recommendations"][0]["potential_skill_changes"][0]["delta"] == 1
    assert len(result["recommendations"][0]["factor_types"]) >= 3
    assert "EV_A" in json.dumps(seen["payload"])


def test_unknown_duplicate_and_too_many_results_fall_back() -> None:
    facts = _facts(_candidate("EV_A", critical=2), _candidate("EV_B", critical=0))
    unknown = _valid(["EV_FAKE"])
    duplicate = _valid(["EV_A", "EV_A"])
    too_many = _valid(["EV_A", "EV_B", "EV_A", "EV_B"])
    for raw in (unknown, duplicate, too_many):
        result, _seen = _run(facts, raw)
        assert result["used_ai"] is False
        assert result["selection_status"] == "fallback_ranked"
        assert result["fallback_reason"] == "invalid_ai_output"
        assert [item["event_id"] for item in result["recommendations"]] == ["EV_A", "EV_B"]


def test_insufficient_factors_fall_back() -> None:
    facts = _facts(_candidate("EV_A"), _candidate("EV_B"))
    raw = _valid(["EV_A", "EV_B"])
    raw["recommendations"][0]["factor_types"] = ["grade", "skill_gap"]
    result, _seen = _run(facts, raw)
    assert result["fallback_reason"] == "invalid_ai_output"


def test_timeout_and_provider_errors_fall_back() -> None:
    facts = _facts(_candidate("EV_A"))
    timeout, _seen = _run(facts, error=TimeoutError("slow"))
    assert timeout["fallback_reason"] == "timeout"
    assert timeout["recommendations"][0]["event_id"] == "EV_A"
    provider, _seen = _run(facts, error=APIError("down", request=None, body=None))
    assert provider["fallback_reason"] == "provider_error"
    assert provider["model"] == "gpt-5.6-terra"


def test_missing_key_and_no_candidates_do_not_call_model() -> None:
    def complete(*_args):
        raise AssertionError("model called")

    missing = select_recommendations(
        _facts(_candidate("EV_A")),
        api_key=None,
        model="gpt-5.6-terra",
        timeout_seconds=7,
        complete=complete,
    )
    assert missing["fallback_reason"] == "missing_api_key"
    assert missing["model"] is None
    assert missing["recommendations"]
    empty = select_recommendations(
        {"candidate_status": "no_next_grade", "candidates": []},
        api_key="test-key",
        model="gpt-5.6-terra",
        timeout_seconds=7,
        complete=complete,
    )
    assert empty["selection_status"] == "not_applicable"
    assert empty["recommendations"] == []


def test_model_payload_omits_personal_data() -> None:
    facts = _facts(_candidate("EV_A"), _candidate("EV_B"))
    _result, seen = _run(
        facts,
        _valid(["EV_A"]),
        context={
            "role": "Engineer",
            "grade": "Junior",
            "primary_target": {"role": "Engineer", "grade": "Middle"},
            "full_name": "Hidden Person",
            "department": "Secret",
            "manager_id": "E0001",
            "history": [{"record_id": "R1"}],
        },
    )
    encoded = json.dumps(seen["payload"])
    assert "full_name" not in encoded
    assert "Hidden Person" not in encoded
    assert "department" not in encoded
    assert "manager_id" not in encoded
    assert "record_id" not in encoded
    assert "related_skill_negative_status_counts" not in encoded


def test_fallback_order_is_stable() -> None:
    facts = _facts(
        _candidate("EV_B", critical=1, delta=1, negative=2),
        _candidate("EV_A", critical=2, delta=3, negative=0),
    )
    first, _seen = _run(facts, api_key=None)
    second, _seen = _run(facts, api_key=None)
    assert [item["event_id"] for item in first["recommendations"]] == ["EV_A", "EV_B"]
    assert first["recommendations"] == second["recommendations"]
    assert first["comparison"]["chosen_event"]["event_id"] == "EV_A"
    assert first["comparison"]["alternative_event"]["event_id"] == "EV_B"
