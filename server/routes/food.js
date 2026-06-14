// ============================================================
// FEATURE 2: RECOMMENDED FOOD
// Track food spending, suggest budget meals, analyze diet
// ============================================================
const express = require('express');
const router = express.Router();

module.exports = function (db, authenticateToken) {

    // POST /api/food/log - Log a meal
    router.post('/log', authenticateToken, (req, res) => {
        try {
            const { food_name, cost, calories, meal_type, is_homemade, date } = req.body;

            if (!food_name) {
                return res.status(400).json({ error: 'Food name is required.' });
            }

            const mealDate = date || new Date().toISOString().split('T')[0];
            const validMealTypes = ['breakfast', 'lunch', 'dinner', 'snack', 'other'];
            const type = validMealTypes.includes(meal_type) ? meal_type : 'other';

            const result = db.prepare(`
        INSERT INTO food_logs (user_id, date, meal_type, food_name, cost, calories, is_homemade)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(req.user.id, mealDate, type, food_name, cost || 0, calories || 0, is_homemade ? 1 : 0);

            res.status(201).json({
                message: 'Meal logged!',
                food: { id: result.lastInsertRowid, food_name, cost, calories, meal_type: type, date: mealDate }
            });
        } catch (err) {
            console.error('Log food error:', err);
            res.status(500).json({ error: 'Failed to log meal.' });
        }
    });

    // GET /api/food/recommendations - Get personalized meal suggestions
    router.get('/recommendations', authenticateToken, (req, res) => {
        try {
            // Step 1: Calculate user's average daily food spend (last 7 days)
            const spendData = db.prepare(`
        SELECT COALESCE(SUM(cost), 0) as total, COUNT(DISTINCT date) as days
        FROM food_logs
        WHERE user_id = ? AND date >= date('now', '-7 days')
      `).get(req.user.id);

            const daysWithData = spendData.days || 1;
            const dailyFoodSpend = spendData.total / daysWithData;

            // Step 2: Get user dietary preferences
            const user = db.prepare('SELECT dietary_preferences FROM users WHERE id = ?').get(req.user.id);
            let preferences = [];
            try {
                preferences = JSON.parse(user.dietary_preferences || '[]');
            } catch (e) {
                preferences = [];
            }

            // Step 3: Build meal query based on budget and preferences
            let mealQuery = 'SELECT * FROM budget_meals WHERE 1=1';
            const params = [];

            // If user spends > ₹500/day, show budget meals under ₹250
            // If user spends ₹300-₹500/day, show meals matching their range
            // If user spends < ₹300/day, encourage healthy eating
            let maxCost = 250;
            if (dailyFoodSpend <= 300) {
                maxCost = 300;
            } else if (dailyFoodSpend <= 500) {
                maxCost = 350;
            } else {
                maxCost = 200; // Show cheaper options for overspenders
            }

            mealQuery += ' AND cost <= ?';
            params.push(maxCost);

            // Apply dietary filters
            if (preferences.includes('vegetarian')) {
                mealQuery += ' AND is_vegetarian = 1';
            }
            if (preferences.includes('vegan')) {
                mealQuery += ' AND is_vegan = 1';
            }

            mealQuery += ' ORDER BY RANDOM() LIMIT 10';

            const meals = db.prepare(mealQuery).all(...params);

            // Step 4: Build response with context
            let advice = '';
            if (dailyFoodSpend > 500) {
                advice = `You're spending ₹${dailyFoodSpend.toFixed(2)}/day on food. The recommended budget for students is ₹300-500/day. Here are some tasty meals that'll save you money:`;
            } else if (dailyFoodSpend < 300) {
                advice = `Great job! You're spending ₹${dailyFoodSpend.toFixed(2)}/day on food, which is within budget. Make sure you're still eating healthy! Here are some nutritious options:`;
            } else {
                advice = `You're spending ₹${dailyFoodSpend.toFixed(2)}/day on food, which is reasonable. Here are some options to keep it balanced:`;
            }

            res.json({
                daily_food_spend: Math.round(dailyFoodSpend * 100) / 100,
                recommended_budget: { min: 300, max: 500 },
                advice,
                meals,
                savings_potential: dailyFoodSpend > 400 ? Math.round((dailyFoodSpend - 350) * 30 * 100) / 100 : 0
            });
        } catch (err) {
            console.error('Food recommendations error:', err);
            res.status(500).json({ error: 'Failed to get recommendations.' });
        }
    });

    // GET /api/food/budget-analysis - Compare actual spend vs budget
    router.get('/budget-analysis', authenticateToken, (req, res) => {
        try {
            // Daily breakdown for last 7 days
            const dailySpend = db.prepare(`
        SELECT date, SUM(cost) as total, COUNT(*) as meals
        FROM food_logs
        WHERE user_id = ? AND date >= date('now', '-7 days')
        GROUP BY date
        ORDER BY date ASC
      `).all(req.user.id);

            // By meal type
            const byMealType = db.prepare(`
        SELECT meal_type, AVG(cost) as avg_cost, COUNT(*) as count
        FROM food_logs
        WHERE user_id = ? AND date >= date('now', '-7 days')
        GROUP BY meal_type
      `).all(req.user.id);

            // Homemade vs bought
            const homemadeStats = db.prepare(`
        SELECT
          SUM(CASE WHEN is_homemade = 1 THEN 1 ELSE 0 END) as homemade_count,
          SUM(CASE WHEN is_homemade = 0 THEN 1 ELSE 0 END) as bought_count,
          AVG(CASE WHEN is_homemade = 1 THEN cost ELSE NULL END) as avg_homemade_cost,
          AVG(CASE WHEN is_homemade = 0 THEN cost ELSE NULL END) as avg_bought_cost
        FROM food_logs
        WHERE user_id = ? AND date >= date('now', '-7 days')
      `).get(req.user.id);

            const totalSpent = dailySpend.reduce((sum, d) => sum + d.total, 0);
            const avgDaily = dailySpend.length > 0 ? totalSpent / dailySpend.length : 0;

            res.json({
                total_7_days: Math.round(totalSpent * 100) / 100,
                daily_average: Math.round(avgDaily * 100) / 100,
                recommended_daily: 400, // ₹300-500 range, middle = ₹400
                daily_breakdown: dailySpend,
                by_meal_type: byMealType,
                homemade_vs_bought: homemadeStats,
                tip: avgDaily > 500
                    ? 'Try cooking at home more! Homemade meals cost 50-70% less on average.'
                    : avgDaily < 200
                        ? 'You\'re under budget - make sure you\'re eating enough!'
                        : 'You\'re in a good range. Keep it up!'
            });
        } catch (err) {
            console.error('Food budget analysis error:', err);
            res.status(500).json({ error: 'Failed to analyze food budget.' });
        }
    });

    // GET /api/food/log - Get food log history
    router.get('/log', authenticateToken, (req, res) => {
        try {
            const { days } = req.query;
            const lookback = parseInt(days) || 7;

            const logs = db.prepare(`
        SELECT * FROM food_logs
        WHERE user_id = ? AND date >= date('now', ?)
        ORDER BY date DESC, created_at DESC
      `).all(req.user.id, `-${lookback} days`);

            res.json(logs);
        } catch (err) {
            console.error('Food log error:', err);
            res.status(500).json({ error: 'Failed to get food log.' });
        }
    });

    return router;
};
