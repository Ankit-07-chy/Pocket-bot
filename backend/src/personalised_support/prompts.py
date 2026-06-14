"""
Prompt templates for personalized support chatbot.
All prompts enforce short, bullet-point responses.
"""
from __future__ import annotations
from typing import Optional


SYSTEM_PROMPT = """You are a concise financial support assistant for PocketBuddy.

STRICT RESPONSE RULES — follow every time:
• Reply ONLY in bullet points (use • or - for each point)
• Max 5 bullet points per response — never more
• Each bullet must be 1 short sentence, max 12 words
• No paragraphs, no long explanations, no padding
• No greetings, no sign-offs, no filler phrases
• If the user's data is available, reference 1-2 real numbers
• If you don't know, say "I need more data to advise on that." (1 line)

Your expertise: budgeting, expense tracking, savings, stress around money."""


def build_system_prompt(user_context: Optional[dict] = None) -> str:
    """
    Build system prompt, optionally injecting user financial context.
    Context is appended as a compact data block — not as prose.
    """
    prompt = SYSTEM_PROMPT

    if user_context:
        lines = ["\n\nUSER DATA (use these numbers in your bullets when relevant):"]

        if user_context.get("current_month_total") is not None:
            lines.append(f"spent_this_month=₹{user_context['current_month_total']:,.0f}")

        if user_context.get("previous_month_total") is not None:
            lines.append(f"last_month=₹{user_context['previous_month_total']:,.0f}")

        if user_context.get("budget") is not None:
            lines.append(f"budget=₹{user_context['budget']:,.0f}")

        if user_context.get("budget_status"):
            lines.append(f"status={user_context['budget_status']}")

        if user_context.get("biggest_category"):
            lines.append(f"top_category={user_context['biggest_category']}")

        if user_context.get("trend"):
            lines.append(f"trend={user_context['trend']}")

        if user_context.get("category_spending"):
            cats = ", ".join(
                f"{cat}:₹{amt:,.0f}"
                for cat, amt in user_context["category_spending"].items()
            )
            lines.append(f"categories={cats}")

        prompt += "\n".join(lines)

    return prompt


# ---------------------------------------------------------------------------
# Standalone template strings used by langchain_chatbot for special analysis
# All templates enforce bullet-point, short output.
# ---------------------------------------------------------------------------

SPENDING_ANALYSIS_TEMPLATE = """Analyse this spending data. Reply ONLY in bullet points (max 5 bullets, 1 sentence each).

spent=₹{current_total} | last_month=₹{previous_total} | top_categories={categories}
status={budget_status} | trend={trend}

Cover: biggest concern, one positive, and 2 specific action steps. Nothing else."""


GOAL_SETTING_TEMPLATE = """Give a goal plan. Reply ONLY in bullet points (max 5 bullets, 1 sentence each).

income=₹{monthly_income} | spending=₹{current_spending} | budget=₹{budget}
goal={goal_description}

Cover: feasibility, monthly savings needed, 2 action steps. Nothing else."""


CONTEXTUAL_ADVICE_TEMPLATE = """Give personalised advice. Reply ONLY in bullet points (max 4 bullets, 1 sentence each).

budget=₹{budget} | top_expense={biggest_expense} | trend={trend}
question={user_input}

Be direct. Reference their numbers. No fluff."""


CRISIS_SUPPORT_TEMPLATE = """The user is stressed about money. Reply ONLY in bullet points (max 4 bullets, 1 sentence each).

situation={situation} | emotional_state={emotional_state}

Cover: acknowledge feeling, 1 immediate step, 1 resource, 1 encouragement. Nothing else."""


CONVERSATION_CONTEXT_TEMPLATE = """Analyse this financial support conversation. Respond ONLY with valid JSON.

Conversation:
{conversation_history}

Latest message: {latest_message}

JSON keys required: issues (list of strings), support_type (one of: ai, rule_based, peer),
urgency (one of: low, medium, high), confidence (float 0-1), reasoning (string)."""
