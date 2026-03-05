"""Tests for Pydantic schema validation: input constraints, edge cases."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import UserLogin, UserRegister
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.knowledge import KBArticleCreate, KBArticleUpdate


# --- Auth schemas ---

def test_register_valid():
    user = UserRegister(email="a@b.com", password="12345678", full_name="Test")
    assert user.email == "a@b.com"


def test_register_password_too_short():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="short", full_name="Test")


def test_register_password_empty():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="", full_name="Test")


def test_register_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(email="not-an-email", password="12345678", full_name="Test")


def test_register_full_name_empty():
    with pytest.raises(ValidationError):
        UserRegister(email="a@b.com", password="12345678", full_name="")


def test_login_valid():
    login = UserLogin(email="a@b.com", password="x")
    assert login.password == "x"


# --- Ticket schemas ---

def test_ticket_create_valid():
    t = TicketCreate(title="Bug report", description="Something broke")
    assert t.priority.value == "medium"


def test_ticket_create_title_too_long():
    with pytest.raises(ValidationError):
        TicketCreate(title="x" * 256, description="desc")


def test_ticket_create_empty_title():
    with pytest.raises(ValidationError):
        TicketCreate(title="", description="desc")


def test_ticket_create_empty_description():
    with pytest.raises(ValidationError):
        TicketCreate(title="title", description="")


def test_ticket_update_partial():
    u = TicketUpdate(title="New Title")
    data = u.model_dump(exclude_unset=True)
    assert data == {"title": "New Title"}


# --- KB schemas ---

def test_kb_article_create_valid():
    a = KBArticleCreate(title="FAQ", content="Some content here")
    assert a.category is None


def test_kb_article_create_title_too_long():
    with pytest.raises(ValidationError):
        KBArticleCreate(title="x" * 256, content="content")


def test_kb_article_update_partial():
    u = KBArticleUpdate(is_published=False)
    data = u.model_dump(exclude_unset=True)
    assert data == {"is_published": False}
