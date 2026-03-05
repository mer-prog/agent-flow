"""Tests for agent logic: intent classification, sentiment analysis, ticket extraction."""

import pytest

from app.agents import extract_last_message
from app.agents.router import _classify_demo, CONFIDENCE_KEYWORD_MATCH, CONFIDENCE_DEFAULT_CHITCHAT
from app.agents.escalation import _analyze_sentiment_demo, SENTIMENT_VERY_NEGATIVE, SENTIMENT_NEUTRAL
from app.agents.ticket import _extract_ticket_demo
from app.agents.chitchat import _respond_demo
from app.agents.faq import _generate_demo_answer
from app.agents.graph import route_by_intent


# --- extract_last_message ---

def test_extract_last_message_from_dict():
    state = {"messages": [{"role": "user", "content": "hello"}]}
    assert extract_last_message(state) == "hello"


def test_extract_last_message_empty():
    assert extract_last_message({}) == ""
    assert extract_last_message({"messages": []}) == ""


# --- Router (demo mode) ---

def test_classify_faq_intent():
    intent, conf = _classify_demo("How do I reset my password?")
    assert intent == "faq"
    assert conf == CONFIDENCE_KEYWORD_MATCH


def test_classify_ticket_intent():
    intent, conf = _classify_demo("I want to create a ticket about a bug")
    assert intent == "ticket"
    assert conf == CONFIDENCE_KEYWORD_MATCH


def test_classify_escalation_intent():
    intent, conf = _classify_demo("I am furious, let me speak to a manager")
    assert intent == "escalation"
    assert conf == CONFIDENCE_KEYWORD_MATCH


def test_classify_chitchat_fallback():
    intent, conf = _classify_demo("Good morning!")
    assert intent == "chitchat"
    assert conf == CONFIDENCE_DEFAULT_CHITCHAT


# --- route_by_intent ---

def test_route_faq():
    assert route_by_intent({"intent": "faq"}) == "faq_agent"


def test_route_ticket():
    assert route_by_intent({"intent": "ticket"}) == "ticket_agent"


def test_route_escalation():
    assert route_by_intent({"intent": "escalation"}) == "escalation_agent"


def test_route_unknown_falls_to_chitchat():
    assert route_by_intent({"intent": "unknown"}) == "chitchat_agent"
    assert route_by_intent({}) == "chitchat_agent"


# --- Escalation sentiment ---

def test_sentiment_very_negative():
    score = _analyze_sentiment_demo("I am angry furious and disgusted")
    assert score == SENTIMENT_VERY_NEGATIVE


def test_sentiment_neutral():
    score = _analyze_sentiment_demo("Hello, nice day today")
    assert score == SENTIMENT_NEUTRAL


def test_sentiment_bounded():
    score = _analyze_sentiment_demo("anything")
    assert 0.0 <= score <= 1.0


# --- Ticket extraction ---

def test_extract_ticket_priority_urgent():
    result = _extract_ticket_demo("This is an urgent issue with billing")
    assert result["priority"] == "urgent"
    assert result["category"] == "billing"


def test_extract_ticket_default_priority():
    result = _extract_ticket_demo("Some random request")
    assert result["priority"] == "medium"
    assert result["category"] == "general"


# --- Chitchat ---

def test_chitchat_hello():
    resp = _respond_demo("hello there")
    assert "Hello" in resp or "Hi" in resp


def test_chitchat_thanks():
    resp = _respond_demo("thanks for help")
    assert "welcome" in resp.lower() or "anything" in resp.lower()


# --- FAQ ---

def test_faq_with_kb_results():
    kb = [{"article_title": "Test", "content": "Answer text here"}]
    resp = _generate_demo_answer("question", kb)
    assert "Test" in resp
    assert "Answer text here" in resp


def test_faq_template_fallback():
    resp = _generate_demo_answer("what is the price?", [])
    assert "$" in resp or "plan" in resp.lower()


def test_faq_no_match():
    resp = _generate_demo_answer("xyzzy", [])
    assert len(resp) > 0
