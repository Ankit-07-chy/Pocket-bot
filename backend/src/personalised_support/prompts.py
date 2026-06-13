"""
LangChain prompt templates for personalized support chatbot
"""
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import FewShotPromptTemplate

# System prompt for financial support chatbot
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
- Data-driven when possible
- Practical and actionable

You have access to the user's expense data and can provide personalized advice."""

user_prompt = None # ---------- Here To load prompt and make full prompt
prompt = prompt = SYSTEM_PROMPT + "\n\nUser Context:\n" + user_prompt

# Main chat template
CHAT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", prompt),
    ("human", "{input}"),
    ("ai", "{chat_history}"),
])

# Few-shot examples for budget advice
BUDGET_EXAMPLES = [
    {
        "question": "How can I reduce my food expenses?",
        "answer": """Great question! Here are some practical strategies:

1. **Meal Planning**: Plan your meals weekly and create a shopping list to avoid impulse purchases
2. **Track Categories**: Break down food into groceries vs dining out - most people spend 30-40% more on restaurants
3. **Set Limits**: Consider a weekly food budget and track against it
4. **Smart Shopping**: Shop during sales, use coupons, and consider store brands
5. **Cook More**: Cooking at home is typically 3-5x cheaper than eating out

From your spending patterns, I notice you spend more on weekends. Would you like strategies specifically for weekend spending?"""
    },
    {
        "question": "I'm overspending in my entertainment category",
        "answer": """Let me help you get control of entertainment spending. First, let's understand:

1. **Categorize**: Is this subscriptions, events, hobbies, or streaming services?
2. **Audit**: Review last month's transactions - you might find forgotten subscriptions
3. **Set Boundaries**: Decide a realistic budget that still allows fun activities
4. **Alternatives**: Free or low-cost activities in your area
5. **Timing**: Reduce spending during high-risk times (evenings, weekends)

A common pattern is subscription creep - many people have 3-5 forgotten subscriptions. Would you like me to help review yours?"""
    },
]

BUDGET_PROMPT = FewShotPromptTemplate(
    examples=BUDGET_EXAMPLES,
    example_prompt=PromptTemplate(
        input_variables=["question", "answer"],
        template="Question: {question}\nAnswer: {answer}"
    ),
    prefix="You are a budget expert helping users reduce expenses.\n\n{examples}",
    suffix="Question: {question}\nAnswer:",
    input_variables=["question"]
)

# Spending analysis template
SPENDING_ANALYSIS_TEMPLATE = """Analyze the following spending data and provide insights:

User: {user_id}
Current Month Total: ${current_total}
Previous Month Total: ${previous_total}
Top Categories: {categories}
Budget Status: {budget_status}
Trend: {trend}

Provide:
1. Key observations about spending patterns
2. Areas of concern or over-spending
3. 2-3 specific, actionable recommendations
4. Positive trends to encourage

Keep response concise and motivating."""

SPENDING_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["user_id", "current_total", "previous_total", "categories", "budget_status", "trend"],
    template=SPENDING_ANALYSIS_TEMPLATE
)

# Goal setting template
GOAL_SETTING_TEMPLATE = """Help the user set a realistic financial goal based on their data:

Current Situation:
- Monthly Income: ${monthly_income}
- Current Spending: ${current_spending}
- Budget: ${budget}
- Goal: {goal_description}

Provide:
1. Feasibility assessment (realistic timeline)
2. Required monthly savings needed
3. Specific action steps to achieve the goal
4. Potential challenges and solutions
5. Motivation and encouragement

Be honest but encouraging."""

GOAL_SETTING_PROMPT = PromptTemplate(
    input_variables=["monthly_income", "current_spending", "budget", "goal_description"],
    template=GOAL_SETTING_TEMPLATE
)

# Contextual advice template
CONTEXTUAL_ADVICE_TEMPLATE = """Provide personalized financial advice based on user context:

User Profile:
- Spending Pattern: {spending_pattern}
- Monthly Budget: ${budget}
- Biggest Expense: {biggest_expense}
- Recent Trend: {trend}

User Question/Issue: {user_input}

Provide advice that:
1. Acknowledges their specific situation
2. References their actual spending data
3. Gives 2-3 concrete, actionable steps
4. Is empathetic and encouraging

Keep it concise (2-3 paragraphs)."""

CONTEXTUAL_ADVICE_PROMPT = PromptTemplate(
    input_variables=["spending_pattern", "budget", "biggest_expense", "trend", "user_input"],
    template=CONTEXTUAL_ADVICE_TEMPLATE
)

# Emergency financial support template
CRISIS_SUPPORT_TEMPLATE = """The user is experiencing financial stress or crisis. Respond with:

Situation: {situation}
User's Emotion: {emotional_state}

Provide:
1. Empathetic acknowledgment
2. Immediate practical steps (if applicable)
3. Breathing room/relief strategies
4. Resources and next steps
5. When to seek professional help

Be compassionate, practical, and clear about limitations of this support."""

CRISIS_SUPPORT_PROMPT = PromptTemplate(
    input_variables=["situation", "emotional_state"],
    template=CRISIS_SUPPORT_TEMPLATE
)

# Template for analyzing conversation context
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

Format as JSON."""

CONVERSATION_CONTEXT_PROMPT = PromptTemplate(
    input_variables=["conversation_history", "latest_message"],
    template=CONVERSATION_CONTEXT_TEMPLATE
)
