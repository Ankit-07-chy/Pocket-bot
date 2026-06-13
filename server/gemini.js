// ============================================================
// GEMINI AI SERVICE - Generates insights and purchase advice
// ============================================================
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Initialize Gemini client (fallback to dummy key if unset to prevent crashes)
const apiKey = process.env.GEMINI_API_KEY || '';
let genAI = null;
if (apiKey) {
    try {
        genAI = new GoogleGenerativeAI(apiKey);
    } catch (e) {
        console.error('Failed to initialize GoogleGenerativeAI with key:', e.message);
    }
}

/**
 * Fallback rule-based recommendation generator when Gemini API key is missing or fails
 */
function generateRuleBasedRecommendation(context) {
    const sleep = context.sleep_hours;
    const stress = context.stress_level;
    const mood = context.mood || 'neutral';
    const totalSpent = context.total_spent || 0;
    const monthlyPocketMoney = context.monthly_pocket_money || 0;
    const foodPercent = context.food_percent || 0;

    // Rule 1: High Stress & Low Sleep
    if (stress > 7 && sleep < 6) {
        return {
            type: 'Burnout',
            message: "⚠️ You seem stressed and sleep-deprived. Your sleep is critically low and stress is high. Try getting at least 7 hours of sleep tonight and take regular breaks from studying."
        };
    }

    // Rule 2: Food Spending exceeds 50%
    if (totalSpent > 0 && foodPercent > 50) {
        return {
            type: 'Finance',
            message: `🍔 Food expenses are consuming ${foodPercent.toFixed(0)}% of your budget, which is above 50%. Consider utilizing campus mess meals or cooking at home to save pocket money this week.`
        };
    }

    // Rule 3: High Stress & Low Food Spending (skip meals alert)
    if (stress > 6 && foodPercent < 15) {
        return {
            type: 'Wellness',
            message: "🍛 You may be skipping meals during a stressful period. Make sure to maintain regular meals even when you're busy with assignments."
        };
    }

    // Rule 4: Budget Almost Exhausted
    if (monthlyPocketMoney > 0 && totalSpent > monthlyPocketMoney * 0.85) {
        return {
            type: 'Finance',
            message: `💰 Budget Warning: You have spent $${totalSpent.toFixed(2)} out of your $${monthlyPocketMoney.toFixed(2)} pocket money. Slow down your spending to make it to the end of the month.`
        };
    }

    // Rule 5: Generally Stressed
    if (stress > 6) {
        return {
            type: 'Wellness',
            message: "🧘 Your stress level is elevated today. Try the Pomodoro technique (25 min study, 5 min stretch break) and get outside for fresh air."
        };
    }

    // Default Good State
    return {
        type: 'Wellness',
        message: "🌟 Great job! Your sleep, budget, and stress levels look stable. Keep maintaining these healthy habits to avoid burnout."
    };
}

/**
 * Generate a personalized recommendation using Gemini API (with local rule-based fallback)
 */
async function generateRecommendation(context) {
    if (!genAI) {
        return generateRuleBasedRecommendation(context);
    }

    const prompt = `
You are PocketBuddy, a helpful student financial and wellness companion.
Analyze this student's data and write a single, punchy, actionable recommendation (max 2 sentences).
Data:
- Sleep Last Night: ${context.sleep_hours} hours
- Stress Level Today (1-10): ${context.stress_level}
- Mood: ${context.mood}
- Monthly Pocket Money: $${context.monthly_pocket_money}
- Total Spent this week: $${context.total_spent}
- Food spending percentage of total: ${context.food_percent}%

Recommendations Types to choose from: 'Finance', 'Wellness', or 'Burnout'.

Provide a JSON response in this exact format:
{
  "type": "Finance" | "Wellness" | "Burnout",
  "message": "Write recommendation here..."
}
`;

    try {
        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        const result = await model.generateContent(prompt);
        const responseText = result.response.text().trim();
        
        // Clean JSON formatting if enclosed in code blocks
        const jsonStr = responseText.replace(/```json/g, '').replace(/```/g, '').trim();
        const data = JSON.parse(jsonStr);
        if (data.type && data.message) return data;
        
        throw new Error('Invalid JSON structure returned by Gemini');
    } catch (err) {
        console.warn('Gemini recommendation query failed, using rule-based fallback:', err.message);
        return generateRuleBasedRecommendation(context);
    }
}

/**
 * Generate Purchase Advice using Gemini (with math-based fallback)
 */
async function generatePurchaseAdvice(context, itemName, itemCost) {
    const remainingBalance = context.remaining_balance;
    const dailyLimit = context.safe_daily_spending;
    const affordable = itemCost <= remainingBalance;

    const summary = affordable
        ? `You can afford this purchase. It leaves you with $${(remainingBalance - itemCost).toFixed(2)} for the month.`
        : `This purchase may impact your monthly budget. It exceeds your remaining balance of $${remainingBalance.toFixed(2)} by $${(itemCost - remainingBalance).toFixed(2)}.`;

    if (!genAI) {
        return {
            affordable,
            message: `${summary} (Tip: Save up or wait until your pocket money is refreshed next month.)`
        };
    }

    const prompt = `
User wants to buy: "${itemName}" for $${itemCost}.
Budget Context:
- Remaining Monthly Pocket Money: $${remainingBalance}
- Safe Daily Spending Limit: $${dailyLimit}/day
- Current spent this week: $${context.total_spent}

The purchase is ${affordable ? 'AFFORDABLE' : 'UNAFFORDABLE'} under their current remaining pocket money.
Provide a quick, realistic student-focused financial advice (max 2 sentences) telling them if they should buy it and why.
`;

    try {
        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        const result = await model.generateContent(prompt);
        const advice = result.response.text().trim();
        return {
            affordable,
            message: advice
        };
    } catch (err) {
        console.warn('Gemini purchase advisor query failed, using math-based fallback:', err.message);
        return {
            affordable,
            message: `${summary} Try to avoid non-essential expenses to keep your daily spending limit at a healthy $${dailyLimit.toFixed(2)}/day.`
        };
    }
}

module.exports = {
    generateRecommendation,
    generatePurchaseAdvice
};
