from backend.career_quest.ai_select import select_recommendations


def _facts(*event_ids: str) -> dict:
    return {
        "candidate_status": "candidates_available",
        "candidates": [
            {
                "event_id": event_id,
                "title": f"Activity {event_id}",
                "type": "course",
                "format": "self_paced",
                "duration_hours": 2,
                "upcoming_sessions": [],
                "critical_gaps": ["S_ARCH"],
                "potential_skill_changes": [
                    {
                        "skill_id": "S_ARCH",
                        "delta": 1,
                        "current_level": 1,
                        "new_level": 2,
                    }
                ],
                "participation": {"event_status_counts": {}},
            }
            for event_id in event_ids
        ],
    }


def test_valid_selection_keeps_server_facts() -> None:
    def complete(api_key, model, timeout, messages):
        assert api_key == "test-key"
        assert "EV_OTHER" in messages[1]["content"]
        return {
            "recommendations": [
                {
                    "event_id": "EV_A",
                    "why": "Закрывает critical gap.",
                    "alternative_event_id": "EV_OTHER",
                    "why_not_alternative": "Даёт меньший прирост по цели.",
                }
            ]
        }

    result = select_recommendations(
        _facts("EV_A", "EV_OTHER"),
        api_key="test-key",
        model="gpt-4o-mini",
        timeout_seconds=8,
        complete=complete,
    )
    assert result["used_ai"] is True
    assert result["selection_status"] == "selected"
    assert result["recommendations"][0]["title"] == "Activity EV_A"
    assert result["recommendations"][0]["format"] == "self_paced"


def test_invented_event_becomes_explicit_fallback() -> None:
    def complete(*_args):
        return {
            "recommendations": [
                {
                    "event_id": "EV_INVENTED",
                    "why": "Нет такого занятия.",
                    "alternative_event_id": "EV_A",
                    "why_not_alternative": "Нельзя.",
                }
            ]
        }

    result = select_recommendations(
        _facts("EV_A", "EV_OTHER"),
        api_key="test-key",
        model="gpt-4o-mini",
        timeout_seconds=8,
        complete=complete,
    )
    assert result["used_ai"] is False
    assert result["selection_status"] == "fallback"
    assert result["fallback_reason"] == "invalid_ai_response"
    assert result["recommendations"] == []


def test_missing_key_does_not_call_model() -> None:
    def complete(*_args):
        raise AssertionError("model called")

    result = select_recommendations(
        _facts("EV_A"),
        api_key=None,
        model="gpt-4o-mini",
        timeout_seconds=8,
        complete=complete,
    )
    assert result["fallback_reason"] == "missing_api_key"


def test_no_candidates_skips_model() -> None:
    def complete(*_args):
        raise AssertionError("model called")

    result = select_recommendations(
        {"candidate_status": "no_next_grade", "candidates": []},
        api_key="test-key",
        model="gpt-4o-mini",
        timeout_seconds=8,
        complete=complete,
    )
    assert result["selection_status"] == "not_applicable"
    assert result["used_ai"] is False
