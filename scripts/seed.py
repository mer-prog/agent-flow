"""Seed script: creates demo users, sample KB articles, and sample tickets.

Idempotent — checks for existing data before inserting.
Does NOT create tables or enums; Alembic handles schema creation.

Seed passwords default to demo values and MUST be changed in production
via SEED_ADMIN_PASSWORD, SEED_AGENT_PASSWORD, SEED_CUSTOMER_PASSWORD env vars.
"""

import asyncio
import os

from sqlalchemy import select

from app.core.security import hash_password
from app.database import async_session
from app.models import (
    Conversation,
    ConversationStatus,
    KBArticle,
    Ticket,
    TicketPriority,
    TicketStatus,
    User,
    UserRole,
)
from app.services.knowledge import chunk_and_embed_article

ARTICLES = [
    {
        "title": "Getting Started with AgentFlow",
        "content": (
            "AgentFlow is a multi-agent customer support platform. "
            "To get started, create an account and log in. "
            "You can chat with our AI assistant, create support tickets, "
            "and browse our knowledge base. The AI agent automatically "
            "classifies your intent and routes you to the right service."
        ),
        "category": "general",
    },
    {
        "title": "Pricing Plans",
        "content": (
            "We offer three pricing plans. "
            "Basic plan at $9.99/month includes 1000 messages and email support. "
            "Pro plan at $29.99/month includes 10000 messages, priority support, and analytics. "
            "Enterprise plan at $99.99/month includes unlimited messages, dedicated support, SSO, and custom integrations. "
            "All plans include a 14-day free trial with no credit card required."
        ),
        "category": "billing",
    },
    {
        "title": "Return and Refund Policy",
        "content": (
            "We accept returns within 30 days of purchase. "
            "Items must be in their original condition and packaging. "
            "To initiate a return, contact our support team with your order number. "
            "Refunds are processed within 5-7 business days after we receive the returned item. "
            "Digital products are eligible for refund within 7 days if unused."
        ),
        "category": "billing",
    },
    {
        "title": "Technical Requirements",
        "content": (
            "AgentFlow works with all modern browsers including Chrome, Firefox, Safari, and Edge. "
            "Minimum requirements: 2GB RAM, stable internet connection. "
            "Mobile apps are available for iOS 16+ and Android 13+. "
            "API access requires an API key which can be generated from the Settings page."
        ),
        "category": "technical",
    },
    {
        "title": "Account Security",
        "content": (
            "We take security seriously. All passwords are hashed with bcrypt. "
            "We support two-factor authentication (2FA) via authenticator apps. "
            "Sessions expire after 30 minutes of inactivity. "
            "If you suspect unauthorized access, contact our security team immediately. "
            "We perform regular security audits and penetration testing."
        ),
        "category": "account",
    },
]


async def seed() -> None:
    async with async_session() as db:
        # Check if seed data already exists
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none():
            print("Seed data already exists, skipping.")
            return

        # Users — passwords from env vars, falling back to demo defaults
        admin_pw = os.environ.get("SEED_ADMIN_PASSWORD", "admin123")
        agent_pw = os.environ.get("SEED_AGENT_PASSWORD", "agent123")
        customer_pw = os.environ.get("SEED_CUSTOMER_PASSWORD", "demo1234")

        admin = User(
            email="admin@example.com",
            hashed_password=hash_password(admin_pw),
            full_name="Admin User",
            role=UserRole.admin,
        )
        agent = User(
            email="agent@example.com",
            hashed_password=hash_password(agent_pw),
            full_name="Support Agent",
            role=UserRole.agent,
        )
        customer = User(
            email="demo@example.com",
            hashed_password=hash_password(customer_pw),
            full_name="Demo Customer",
            role=UserRole.customer,
        )
        db.add_all([admin, agent, customer])
        await db.flush()

        # KB Articles
        for article_data in ARTICLES:
            article = KBArticle(**article_data)
            db.add(article)
            await db.flush()
            await chunk_and_embed_article(db, article.id, article.content)

        # Sample tickets
        db.add_all([
            Ticket(
                user_id=customer.id,
                title="Cannot reset password",
                description="I'm trying to reset my password but the reset email never arrives.",
                priority=TicketPriority.high,
                status=TicketStatus.open,
                category="account",
            ),
            Ticket(
                user_id=customer.id,
                title="Billing question about Pro plan",
                description="I was charged twice for my Pro plan subscription this month.",
                priority=TicketPriority.urgent,
                status=TicketStatus.in_progress,
                category="billing",
                assigned_to=agent.id,
            ),
            Ticket(
                user_id=customer.id,
                title="Feature request: dark mode",
                description="It would be great to have a dark mode option in the dashboard.",
                priority=TicketPriority.low,
                status=TicketStatus.resolved,
                category="feature",
            ),
        ])

        # Sample conversation
        db.add(Conversation(
            user_id=customer.id,
            title="Pricing inquiry",
            status=ConversationStatus.active,
        ))

        await db.commit()

    print("Seed data created successfully!")
    print("  Users: admin@example.com/admin123, agent@example.com/agent123, demo@example.com/demo123")
    print(f"  KB Articles: {len(ARTICLES)}")
    print("  Tickets: 3")


if __name__ == "__main__":
    asyncio.run(seed())
