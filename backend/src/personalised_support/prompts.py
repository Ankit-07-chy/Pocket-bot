"""
Prompt templates for personalized support chatbot
"""
from __future__ import annotations
from typing import Optional

# System prompt for financial support chatbot — user context is injected at runtime
SYSTEM_PROMPT = """You are a compassionate and knowledgeable personal finance support assistant for Poket Bot,
an expense management application. Your role is to help users with:

1. Budget planning and expense management advice
2. Understanding their spending patterns
3. Financial goal setting and tracking
4. Money-saving tips and strategies
5. Emotional support around financial stress
6. Actionable recommendations based on their data

Your communication style should be:
- Empathetic and non-judgmental
- Clear and easy to understand
- Encouraging and motivating
- Data-driven when possible (reference the user's actual numbers when available)
- Practical and actionable

Always personalise your advice using the user context provided to you."""


def build_system_prompt(user_context: Optional[dict] = None) -> str:
    """
    Build a full system prompt, optionally injecting the user's financial context.

    Args:
        user_context: dict with keys such as:
            - current_month_total (float)
            - previous_month_total (float)
            - budget (float)
            - category_spending (dict[str, float])
            - biggest_category (str)
            - trend (str)  e.g. "increasing", "decreasing", "stable"
            - budget_status (str)  e.g. "within budget", "over budget"

    Returns:
        Full system prompt string.
    """
    prompt = SYSTEM_PROMPT

    if user_context:
        lines = ["\n\n--- User Financial Context ---"]

        if user_context.get("current_month_total") is not None:
            lines.append(f"Current month spending: ₹{user_context['current_month_total']:,.2f}")

        if user_context.get("previous_month_total") is not None:
            lines.append(f"Previous month spending: ₹{user_context['previous_month_total']:,.2f}")

        if user_context.get("budget") is not None:
            lines.append(f"Monthly budget: ₹{user_context['budget']:,.2f}")

        if user_context.get("budget_status"):
            lines.append(f"Budget status: {user_context['budget_status']}")

        if user_context.get("biggest_category"):
            lines.append(f"Biggest spending category: {user_context['biggest_category']}")

        if user_context.get("trend"):
            lines.append(f"Spending trend: {user_context['trend']}")

        if user_context.get("category_spending"):
            cat_lines = ", ".join(
                f"{cat}: ₹{amt:,.2f}"
                for cat, amt in user_context["category_spending"].items()
            )
            lines.append(f"Category breakdown: {cat_lines}")

        lines.append("--- End of Context ---")
        prompt += "\n".join(lines)

    return prompt


# ---------------------------------------------------------------------------
# Standalone template strings (used by langchain_chatbot for direct prompts)
# ---------------------------------------------------------------------------

SPENDING_ANALYSIS_TEMPLATE = """Analyze the following spending data and provide insights:

User: {user_id}
Current Month Total: ₹{current_total}
Previous Month Total: ₹{previous_total}
Top Categories: {categories}
Budget Status: {budget_status}
Trend: {trend}

Provide:
1. Key observations about spending patterns
2. Areas of concern or over-spending
3. 2-3 specific, actionable recommendations
4. Positive trends to encourage

Keep response concise and motivating."""


GOAL_SETTING_TEMPLATE = """Help the user set a realistic financial goal based on their data:

Current Situation:
- Monthly Income: ₹{monthly_income}
- Current Spending: ₹{current_spending}
- Budget: ₹{budget}
- Goal: {goal_description}

Provide:
1. Feasibility assessment (realistic timeline)
2. Required monthly savings needed
3. Specific action steps to achieve the goal
4. Potential challenges and solutions
5. Motivation and encouragement

Be honest but encouraging."""


CONTEXTUAL_ADVICE_TEMPLATE = """Provide personalized financial advice based on user context:

User Profile:
- Spending Pattern: {spending_pattern}
- Monthly Budget: ₹{budget}
- Biggest Expense: {biggest_expense}
- Recent Trend: {trend}

User Question/Issue: {user_input}

Provide advice that:
1. Acknowledges their specific situation
2. References their actual spending data
3. Gives 2-3 concrete, actionable steps
4. Is empathetic and encouraging

Keep it concise (2-3 paragraphs)."""


CRISIS_SUPPORT_TEMPLATE = """The user is experiencing financial stress or crisis.

Situation: {situation}
User's Emotion: {emotional_state}

Provide:
1. Empathetic acknowledgment
2. Immediate practical steps (if applicable)
3. Breathing room/relief strategies
4. Resources and next steps
5. When to seek professional help

Be compassionate, practical, and clear about limitations of this support."""


CONVERSATION_CONTEXT_TEMPLATE = """You are an expert at understanding financial conversations.

Conversation so far:
{conversation_history}

Latest user message: {latest_message}

Determine:
1. Main issue/question being asked
2. Emotional tone (positive, neutral, stressed, frustrated)
3. Urgency level (low, medium, high)
4. Type of support needed (educational, practical, emotional, urgent)
5. Key context from conversation

Format as JSON with keys: issues (list), support_type (ai/rule_based/peer), urgency (low/medium/high), confidence (0-1), reasoning (string)."""
