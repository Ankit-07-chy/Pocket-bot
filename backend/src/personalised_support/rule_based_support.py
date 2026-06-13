"""
Rule-based support system for common financial questions and patterns
"""

import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from .schemas import RuleBasedResponse

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
        # Spending reduction queries
        SupportCategory.SPENDING_REDUCTION: [
            {
                "patterns": [
                    r"(reduce|cut|decrease|save).*?(spending|expense|cost|money)",
                    r"(overspend|overspending|spending.*too|spend.*much)",
                    r"(how.*save|save.*money|ways.*save)",
                ],
                "responses": [
                    "Here are proven strategies to reduce spending:\n\n1. **Track Everything** - Use Poket Bot to categorize all expenses\n2. **Set Category Limits** - Define budgets per category and monitor weekly\n3. **Identify Leaks** - Look for recurring charges you forgot about\n4. **Cut Subscriptions** - Review and cancel unused services\n5. **Meal Planning** - Plan meals to reduce food waste and impulse purchases\n6. **Use the 24-hour Rule** - Wait 24 hours before non-essential purchases\n\nWhich category would you like to focus on first?",
                    "I can help! Let's identify quick wins:\n\n- **Subscription Audit**: Review last month's transactions for recurring charges\n- **Category Analysis**: Which category is your biggest expense?\n- **Behavioral Changes**: Small daily habits lead to big savings\n- **Timing Strategy**: Identify your high-spend times (evenings, weekends, paydays)\n\nWhat's your main spending challenge?",
                ]
            },
            {
                "patterns": [r"(food|grocery|groceries|eating out|restaurants|dining)"],
                "responses": [
                    "Food spending is often the easiest category to optimize:\n\n1. **Meal Planning**: Plan 7 meals weekly before shopping\n2. **Shopping Strategy**: Shop with a list, avoid aisles temptingly\n3. **Cooking at Home**: Restaurant meals cost 3-5x more than home cooking\n4. **Store Brands**: Usually 20-30% cheaper with same quality\n5. **Batch Cooking**: Make large portions and freeze\n6. **Track Dining Out**: Often reveals surprising patterns\n\nTrack your food expenses in Poket Bot to see the breakdown.",
                ]
            },
            {
                "patterns": [r"(entertainment|subscriptions|streaming|gaming|hobbies)"],
                "responses": [
                    "Entertainment spending often has hidden opportunities:\n\n1. **Subscription Audit**: Most people have forgotten subscriptions\n2. **Consolidate**: Share family plans to reduce costs\n3. **Free Alternatives**: Libraries, parks, free events\n4. **Trial Periods**: Cancel before auto-renewal\n5. **Limit Discretionary**: Set a weekly entertainment budget\n6. **Group Activities**: Often cheaper than solo entertainment\n\nReview your last 3 months - what are you actually using?",
                ]
            },
        ],

        # Budget planning queries
        SupportCategory.BUDGET_PLANNING: [
            {
                "patterns": [
                    r"(create|make|set.*budget|budgeting|how.*budget|plan.*budget)",
                    r"(allocate|distribution|percentage|ratio).*budget",
                ],
                "responses": [
                    "Here's a proven budgeting framework:\n\n**The 50/30/20 Rule:**\n- 50% Essential Needs (housing, food, utilities)\n- 30% Wants (entertainment, hobbies, dining out)\n- 20% Savings & Debt Repayment\n\n**How to implement with Poket Bot:**\n1. Analyze your previous 3 months\n2. Categorize each expense as need/want/savings\n3. Calculate your current percentages\n4. Adjust to fit the 50/30/20 model\n5. Set monthly limits in Poket Bot\n6. Review weekly to stay on track\n\nNote: Your percentages might differ based on income and goals.",
                    "Effective budgeting starts with understanding:\n\n**Step 1: Income** - What's your monthly net income?\n**Step 2: Fixed Costs** - Housing, insurance, subscriptions\n**Step 3: Variable Costs** - Food, entertainment, utilities\n**Step 4: Goals** - Emergency fund, savings, debt payment\n\n**Then allocate:**\n- Essentials: 50-60% of income\n- Flexibility: 20-30% of income\n- Savings/Debt: 10-20% of income\n\nUse Poket Bot's budget feature to set these limits.",
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
                    "Building savings is the foundation of financial health:\n\n**Emergency Fund Goals:**\n- Beginner: $500-$1,000 (starter fund)\n- Intermediate: $2,500-$5,000 (1 month expenses)\n- Advanced: $10,000-$20,000 (3-6 months expenses)\n\n**Strategy:**\n1. Calculate monthly expenses from Poket Bot\n2. Set target (e.g., $5,000 for 3 months)\n3. Calculate monthly savings needed\n4. Automate transfers\n5. Track progress monthly\n\n**Quick Wins:**\n- Cut $50/month spending → $600/year\n- Add small side income → amplify savings\n- Review every 3 months\n\nWhat's your target emergency fund amount?",
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
                    "Tracking expenses is crucial for financial awareness:\n\n**How to Track Effectively:**\n1. **Log Everything** - Even small purchases add up\n2. **Categorize** - Use Poket Bot's categories\n3. **Real-time** - Log purchases the same day\n4. **Weekly Review** - Check spending every Sunday\n5. **Monthly Analysis** - Identify patterns and trends\n\n**Tips:**\n- Use phone banking for immediate notification of charges\n- Save receipts for large purchases\n- Set spending alerts in Poket Bot\n- Compare month-to-month trends\n\n**Benefits:**\n- Find unexpected spending patterns\n- Identify cost-saving opportunities\n- Stay accountable to your budget\n- Celebrate progress\n\nStart by logging your last 30 days!",
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
                    "Effective debt repayment strategies:\n\n**Methods to Consider:**\n1. **Snowball** - Pay smallest debts first (psychological wins)\n2. **Avalanche** - Pay highest interest first (financial wins)\n3. **Consolidation** - Combine loans for lower rates\n\n**Action Plan:**\n1. List all debts (amount, rate, minimum payment)\n2. Calculate total interest cost\n3. Choose method that fits your situation\n4. Automate minimum payments\n5. Apply extra funds to target debt\n6. Track payoff progress\n\n**Pro Tips:**\n- Contact creditors about lower rates\n- Avoid new debt while repaying\n- Celebrate milestones\n- Use Poket Bot to visualize progress\n\nWould you like help with a specific debt?",
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
                    "Investment basics for beginners:\n\n**Start Here:**\n1. **Build Emergency Fund First** - 3-6 months of expenses\n2. **Understand Risk** - Higher returns = higher risk\n3. **Time Horizon** - Longer time = more risk tolerance\n4. **Diversification** - Don't put all in one place\n\n**Common Vehicles:**\n- 401(k) - Employer-sponsored, get matching if available\n- IRA - Individual retirement account (Traditional or Roth)\n- Index Funds - Low-cost, diversified\n- ETFs - Similar to mutual funds, trade like stocks\n\n**Next Steps:**\n1. Take advantage of employer 401(k) matching\n2. Max out IRA contributions\n3. Invest remaining in diversified index funds\n4. Review allocation yearly\n\n⚠️ This is general education only. Consult a financial advisor for personal advice.",
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
                    "Tax planning tips for individuals:\n\n**Key Strategies:**\n1. **Maximize Retirement Contributions** - Pre-tax contributions reduce taxable income\n2. **Track Deductions** - Keep receipts for business expenses, donations\n3. **Health Savings** - HSA triple tax advantage if eligible\n4. **Tax-Loss Harvesting** - Offset gains with losses (investments)\n\n**Throughout the Year:**\n- Review W-4 withholding (if employed)\n- Track charitable donations\n- Keep business expense receipts\n- Monitor income changes\n\n**Year-End Checklist:**\n- Estimate taxes if self-employed\n- Make IRA contributions before deadline\n- Harvest tax losses in investments\n- Plan Q1 estimated taxes\n\n⚠️ Consult a tax professional for your specific situation.",
                ]
            },
        ],

        # General financial health
        "general": [
            {
                "patterns": [r"(financial|money|finance)"],
                "responses": [
                    "Financial wellness includes several areas:\n\n**Foundation:**\n1. **Budget** - Know where your money goes\n2. **Emergency Fund** - 3-6 months of expenses\n3. **Debt Management** - Plan to pay it down\n\n**Growth:**\n4. **Savings Goals** - Short and long term\n5. **Investments** - Start early, compound interest helps\n6. **Insurance** - Protect against catastrophes\n\n**Protection:**\n7. **Estate Planning** - Will, POA if applicable\n8. **Credit Score** - Monitor and improve\n9. **Tax Planning** - Optimize what you keep\n\nWhat area would you like to focus on first?",
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
