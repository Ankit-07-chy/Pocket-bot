"""
Rule-based support system for common financial questions and patterns
"""

import re
import sys
import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

try:
    from .schemas import RuleBasedResponse
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from personalised_support.schemas import RuleBasedResponse

logger = logging.getLogger(__name__)


class SupportCategory(Enum):
    """Categories of financial support"""
    BUDGET_PLANNING = "budget_planning"
    SPENDING_REDUCTION = "spending_reduction"
    SAVINGS_GOALS = "savings_goals"
    EXPENSE_TRACKING = "expense_tracking"
    DEBT_MANAGEMENT = "debt_management"
    EMERGENCY_FUND = "emergency_fund"
    INVESTMENT_BASICS = "investment_basics"
    TAX_PLANNING = "tax_planning"


class RuleBasedSupport:
    """Rule-based system for predefined financial guidance"""

    # Rule patterns for matching user queries
    RULES = {
        # Spending reduction
        SupportCategory.SPENDING_REDUCTION: [
            {
                "patterns": [
                    r"(reduce|cut|decrease|save).*?(spending|expense|cost|money)",
                    r"(overspend|overspending|spending.*too|spend.*much)",
                    r"(how.*save|save.*money|ways.*save)",
                ],
                "responses": [
                    "- Track every expense in Poket Bot, even small ones.\n"
                    "- Set a weekly category limit and check it every Sunday.\n"
                    "- Cancel any subscriptions you haven't used this month.\n"
                    "- Wait 24 hours before any non-essential purchase.\n"
                    "- Which category do you overspend on most?"
                ]
            },
            {
                "patterns": [r"(food|grocery|groceries|eating out|restaurants|dining)"],
                "responses": [
                    "- Plan meals weekly before shopping to avoid waste.\n"
                    "- Cook at home — restaurant meals cost 3–5× more.\n"
                    "- Switch to store brands (20–30% cheaper, same quality).\n"
                    "- Log all food expenses to see your real weekly spend.\n"
                    "- Set a food category budget in Poket Bot."
                ]
            },
            {
                "patterns": [r"(entertainment|subscriptions|streaming|gaming|hobbies)"],
                "responses": [
                    "- List every active subscription and cancel unused ones.\n"
                    "- Share family plans to split costs.\n"
                    "- Use free alternatives (library, parks, free events).\n"
                    "- Set a fixed monthly entertainment budget.\n"
                    "- Check last 3 months — what have you actually used?"
                ]
            },
        ],

        # Budget planning
        SupportCategory.BUDGET_PLANNING: [
            {
                "patterns": [
                    r"(create|make|set.*budget|budgeting|how.*budget|plan.*budget)",
                    r"(allocate|distribution|percentage|ratio).*budget",
                ],
                "responses": [
                    "- Use the 50/30/20 rule: needs / wants / savings.\n"
                    "- Fix your essential costs first (rent, food, bills).\n"
                    "- Set per-category limits in Poket Bot.\n"
                    "- Review your budget every Sunday — adjust if needed.\n"
                    "- Start with last month's data to set realistic targets."
                ]
            },
        ],

        # Savings goals
        SupportCategory.SAVINGS_GOALS: [
            {
                "patterns": [
                    r"(save|savings|goal|target|accumulate).*?(money|amount|fund)",
                    r"(how.*save|save.*for|build.*fund)",
                    r"(emergency|rainy day|unexpected)",
                ],
                "responses": [
                    "- Target 3–6 months of expenses as your emergency fund.\n"
                    "- Calculate your monthly expenses first (Poket Bot has this).\n"
                    "- Save a fixed amount on payday before spending anything.\n"
                    "- Even ₹500/month builds to ₹6,000 in a year.\n"
                    "- What's your current savings target?"
                ]
            },
        ],

        # Expense tracking
        SupportCategory.EXPENSE_TRACKING: [
            {
                "patterns": [
                    r"(track|tracking|record|log|monitor).*?(expense|spending|money)",
                    r"(where.*money|what.*spending|understand.*spending)",
                ],
                "responses": [
                    "- Log every purchase the same day — small ones too.\n"
                    "- Use Poket Bot categories for accurate breakdowns.\n"
                    "- Review weekly to catch patterns early.\n"
                    "- Compare month-over-month to see if you're improving.\n"
                    "- Enable spending alerts so nothing surprises you."
                ]
            },
        ],

        # Debt management
        SupportCategory.DEBT_MANAGEMENT: [
            {
                "patterns": [
                    r"(debt|loan|credit|owe|owing|repay|payment)",
                    r"(interest|apr|monthly payment|debt payoff)",
                ],
                "responses": [
                    "- List all debts: amount, interest rate, minimum payment.\n"
                    "- Pay minimums on all, then extra on highest-interest debt.\n"
                    "- Never take new debt while actively repaying old debt.\n"
                    "- Call your lender — they may lower your rate if you ask.\n"
                    "- Track payoff progress monthly to stay motivated."
                ]
            },
        ],

        # Investment basics
        SupportCategory.INVESTMENT_BASICS: [
            {
                "patterns": [
                    r"(invest|investment|stock|mutual|fund|return)",
                    r"(retirement|401k|ira|pension|wealth)",
                ],
                "responses": [
                    "- Build a 3–6 month emergency fund before investing.\n"
                    "- Start with your employer's 401(k) — get the full match.\n"
                    "- Index funds are low-cost and diversified for beginners.\n"
                    "- Time in the market beats timing the market.\n"
                    "- ⚠️ Consult a financial advisor for personal investment advice."
                ]
            },
        ],

        # Tax planning
        SupportCategory.TAX_PLANNING: [
            {
                "patterns": [
                    r"(tax|taxes|return|deduction|refund|irs)",
                    r"(withholding|401k.*tax|tax.*save)",
                ],
                "responses": [
                    "- Max retirement contributions to reduce taxable income.\n"
                    "- Keep receipts for all business and charitable expenses.\n"
                    "- Review your W-4 if your income changed this year.\n"
                    "- HSA contributions have a triple tax advantage.\n"
                    "- ⚠️ Consult a tax professional for your specific situation."
                ]
            },
        ],

        # General
        "general": [
            {
                "patterns": [r"(financial|money|finance)"],
                "responses": [
                    "- Start with a budget — know where your money goes.\n"
                    "- Build an emergency fund (3–6 months of expenses).\n"
                    "- Pay down high-interest debt before saving.\n"
                    "- Track spending in Poket Bot for visibility.\n"
                    "- What specific area would you like help with?"
                ]
            },
        ],
    }

    def __init__(self):
        """Initialize rule-based support system"""
        self.compiled_rules = self._compile_rules()

    def _compile_rules(self) -> Dict[str, List[Dict]]:
        """Compile regex patterns for faster matching"""
        compiled = {}
        for category, rules in self.RULES.items():
            compiled[str(category.value if hasattr(category, 'value') else category)] = []
            for rule in rules:
                compiled_rule = rule.copy()
                compiled_rule["compiled_patterns"] = [
                    re.compile(pattern, re.IGNORECASE)
                    for pattern in rule.get("patterns", [])
                ]
                compiled[str(category.value if hasattr(category, 'value') else category)].append(compiled_rule)
        return compiled

    def process_query(
        self,
        user_query: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Optional[RuleBasedResponse]:
        """Process user query and return rule-based response"""
        # Find matching rule
        matched_rule, responses, category = self._find_matching_rule(user_query)

        if not matched_rule or not responses:
            return None

        # Select appropriate response based on context
        response_text = self._select_response(responses, context_data)

        return RuleBasedResponse(
            matched_rule=matched_rule,
            response=response_text,
            category=str(category),
            suggested_next_steps=self._suggest_next_steps(category, context_data)
        )

    def _find_matching_rule(self, query: str) -> Tuple[Optional[str], List[str], Optional[str]]:
        """Find matching rule for query"""
        query_lower = query.lower()

        for category, rules in self.compiled_rules.items():
            for rule in rules:
                for pattern in rule.get("compiled_patterns", []):
                    if pattern.search(query_lower):
                        return (
                            rule.get("patterns", [None])[0],
                            rule.get("responses", []),
                            category
                        )

        return None, [], None

    @staticmethod
    def _select_response(responses: List[str], context_data: Optional[Dict] = None) -> str:
        """Select most appropriate response"""
        if not responses:
            return "I don't have specific guidance for that question. Please try asking differently."

        # For now, select first response
        # Could be enhanced with ML-based selection based on context
        return responses[0]

    @staticmethod
    def _suggest_next_steps(
        category: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Suggest next steps based on category"""
        suggestions = {
            "spending_reduction": [
                "Review your spending categories in Poket Bot",
                "Set category budgets",
                "Enable spending alerts"
            ],
            "budget_planning": [
                "Input your monthly income",
                "Analyze previous 3 months of spending",
                "Set budget targets per category"
            ],
            "savings_goals": [
                "Define your savings target",
                "Calculate required monthly savings",
                "Set up automatic transfers"
            ],
            "expense_tracking": [
                "Log all expenses for 30 days",
                "Review weekly spending patterns",
                "Identify areas to optimize"
            ],
            "debt_management": [
                "List all debts with amounts and rates",
                "Calculate total interest cost",
                "Choose a repayment strategy"
            ],
        }

        return suggestions.get(category, ["Ask me another question to continue"])

    def get_all_categories(self) -> List[str]:
        """Get all available support categories"""
        return [cat.value for cat in SupportCategory]

    def search_knowledge_base(self, query: str) -> List[Dict[str, str]]:
        """Search knowledge base for relevant topics"""
        results = []
        for category, rules in self.RULES.items():
            for rule in rules:
                for pattern in rule.get("patterns", []):
                    if re.search(pattern, query, re.IGNORECASE):
                        results.append({
                            "category": str(category),
                            "pattern": pattern,
                            "responses": rule.get("responses", [])
                        })
                        break
        return results
