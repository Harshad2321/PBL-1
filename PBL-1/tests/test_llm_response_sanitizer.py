"""Regression tests for LocalLLM response sanitization."""

from nurture.utils.llm_interface import LocalLLM


def _local_llm_without_init() -> LocalLLM:
    """Create LocalLLM instance without running network availability checks."""
    return LocalLLM.__new__(LocalLLM)


def test_sanitize_response_strips_chained_role_labels() -> None:
    llm = _local_llm_without_init()

    raw = "Mother: You: Well, I expect you'll show it too, then. Let's work together as a team."
    cleaned = llm._sanitize_response(raw)

    assert cleaned == "Well, I expect you'll show it too, then. Let's work together as a team."


def test_sanitize_response_fixes_known_typo_phrase_and_contractions() -> None:
    llm = _local_llm_without_init()

    raw = "we came make sure this doesnt happen again and dont repeat it"
    cleaned = llm._sanitize_response(raw)

    assert cleaned == "we can make sure this doesn't happen again and don't repeat it"
