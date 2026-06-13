// ============================================================
// FEATURE 1: EXPENSE MANAGEMENT
// Track spending, categorize, show trends, alert overspending
// ============================================================
const express = require('express');
const router = express.Router();

module.exports = function (db, authenticateToken) {

    // POST /api/expenses - Add a new expense
    router.post('/', authenticateToken, (req, res) => {
        try {
            const { amount, category, description, date } = req.body;

            if (!amount || !category) {
                return res.status(400).json({ error: 'Amount and category are required.' });
            }

            // Valid categories for student expenses
            const validCategories = ['food', 'transport', 'entertainment', 'utilities', 'education', 'health', 'other'];
            if (!validCategories.includes(category.toLowerCase())) {
                return res.status(400).json({
                    error: `Invalid category. Use one of: ${validCategories.join(', ')}`
                });
            }

            const expenseDate = date || new Date().toISOString().split('T')[0];

            const result = db.prepare(`
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
      `).run(req.user.id, amount, category.toLowerCase(), description || '', expenseDate);

            // Check if today's spending exceeds daily average * 1.5
            const alert = checkSpendingAlert(db, req.user.id, expenseDate);

            res.status(201).json({
                message: 'Expense added!',
                expense: { id: result.lastInsertRowid, amount, category, description, date: expenseDate },
                alert // Will be null if no alert needed
            });
        } catch (err) {
            console.error('Add expense error:', err);
            res.status(500).json({ error: 'Failed to add expense.' });
        }
    });

    // GET /api/expenses - List all expenses (with optional date filter)
    router.get('/', authenticateToken, (req, res) => {
        try {
            const { start_date, end_date, category, limit } = req.query;
            let query = 'SELECT * FROM expenses WHERE user_id = ?';
            const params = [req.user.id];

            if (start_date) {
                query += ' AND date >= ?';
                params.push(start_date);
            }
            if (end_date) {
                query += ' AND date <= ?';
                params.push(end_date);
            }
            if (category) {
                query += ' AND category = ?';
                params.push(category.toLowerCase());
            }

            query += ' ORDER BY date DESC';

            if (limit) {
                query += ' LIMIT ?';
                params.push(parseInt(limit));
            }

            const expenses = db.prepare(query).all(...params);
            res.json(expenses);
        } catch (err) {
            console.error('List expenses error:', err);
            res.status(500).json({ error: 'Failed to fetch expenses.' });
        }
    });

    // GET /api/expenses/summary - Total spending + breakdown by category
    router.get('/summary', authenticateToken, (req, res) => {
        try {
            const { days } = req.query;
            const lookbackDays = parseInt(days) || 30;

            // Total spending in period
            const total = db.prepare(`
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE user_id = ? AND date >= date('now', ?)
      `).get(req.user.id, `-${lookbackDays} days`);

            // Breakdown by category
            const byCategory = db.prepare(`
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE user_id = ? AND date >= date('now', ?)
        GROUP BY category
        ORDER BY total DESC
      `).all(req.user.id, `-${lookbackDays} days`);

            // Daily average
            const dailyAvg = total.total / lookbackDays;

            // Get user's daily budget for comparison
            const user = db.prepare('SELECT daily_budget FROM users WHERE id = ?').get(req.user.id);

            res.json({
                period_days: lookbackDays,
                total_spent: Math.round(total.total * 100) / 100,
                daily_average: Math.round(dailyAvg * 100) / 100,
                daily_budget: user.daily_budget,
                over_budget: dailyAvg > user.daily_budget && user.daily_budget > 0,
                by_category: byCategory
            });
        } catch (err) {
            console.error('Expense summary error:', err);
            res.status(500).json({ error: 'Failed to get summary.' });
        }
    });

    // GET /api/expenses/trends - 7-day and 30-day spending trends
    router.get('/trends', authenticateToken, (req, res) => {
        try {
            // Last 7 days - daily totals
            const last7Days = db.prepare(`
        SELECT date, SUM(amount) as daily_total
        FROM expenses
        WHERE user_id = ? AND date >= date('now', '-7 days')
        GROUP BY date
        ORDER BY date ASC
      `).all(req.user.id);

            // Last 30 days - weekly totals
            const last30Days = db.prepare(`
        SELECT
          strftime('%W', date) as week_number,
          MIN(date) as week_start,
          SUM(amount) as weekly_total
        FROM expenses
        WHERE user_id = ? AND date >= date('now', '-30 days')
        GROUP BY week_number
        ORDER BY week_start ASC
      `).all(req.user.id);

            // Compare this week vs last week
            const thisWeek = db.prepare(`
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE user_id = ? AND date >= date('now', '-7 days')
      `).get(req.user.id);

            const lastWeek = db.prepare(`
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE user_id = ? AND date >= date('now', '-14 days') AND date < date('now', '-7 days')
      `).get(req.user.id);

            // Calculate trend percentage
            let trendPercent = 0;
            if (lastWeek.total > 0) {
                trendPercent = Math.round(((thisWeek.total - lastWeek.total) / lastWeek.total) * 100);
            }

            res.json({
                daily: last7Days,
                weekly: last30Days,
                this_week_total: Math.round(thisWeek.total * 100) / 100,
                last_week_total: Math.round(lastWeek.total * 100) / 100,
                trend_percent: trendPercent,
                trend_direction: trendPercent > 0 ? 'up' : trendPercent < 0 ? 'down' : 'stable'
            });
        } catch (err) {
            console.error('Expense trends error:', err);
            res.status(500).json({ error: 'Failed to get trends.' });
        }
    });

    // DELETE /api/expenses/:id - Delete an expense
    router.delete('/:id', authenticateToken, (req, res) => {
        try {
            const result = db.prepare('DELETE FROM expenses WHERE id = ? AND user_id = ?')
                .run(req.params.id, req.user.id);

            if (result.changes === 0) {
                return res.status(404).json({ error: 'Expense not found.' });
            }
            res.json({ message: 'Expense deleted.' });
        } catch (err) {
            console.error('Delete expense error:', err);
            res.status(500).json({ error: 'Failed to delete expense.' });
        }
    });

    return router;
};

// ---- HELPER: Check if today's spending is abnormally high ----
function checkSpendingAlert(db, userId, date) {
    // Get 7-day average
    const avgResult = db.prepare(`
    SELECT COALESCE(AVG(daily_total), 0) as avg_daily
    FROM (
      SELECT SUM(amount) as daily_total
      FROM expenses
      WHERE user_id = ? AND date >= date(?, '-7 days') AND date < ?
      GROUP BY date
    )
  `).get(userId, date, date);

    // Get today's total
    const todayResult = db.prepare(`
    SELECT COALESCE(SUM(amount), 0) as today_total
    FROM expenses
    WHERE user_id = ? AND date = ?
  `).get(userId, date);

    const avgDaily = avgResult.avg_daily;
    const todayTotal = todayResult.today_total;

    // Alert if spending 50% more than average
    if (avgDaily > 0 && todayTotal > avgDaily * 1.5) {
        return {
            type: 'overspending',
            message: `You've spent $${todayTotal.toFixed(2)} today, which is ${Math.round((todayTotal / avgDaily - 1) * 100)}% above your daily average of $${avgDaily.toFixed(2)}.`
        };
    }

    return null;
}
