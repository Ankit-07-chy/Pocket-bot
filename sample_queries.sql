-- ============================================================================
-- POCKETBUDDY DATABASE - SAMPLE QUERIES
-- Use these queries to explore and analyze the populated dummy data
-- ============================================================================

-- 1. USER MANAGEMENT QUERIES
-- ============================================================================

-- View all users with their basic info
SELECT id, name, email, major, year, monthly_income, daily_budget
FROM users
ORDER BY monthly_income DESC;

-- Find user by email
SELECT * FROM users WHERE email = 'alice@email.com';

-- Users earning above $70K
SELECT name, monthly_income, daily_budget
FROM users
WHERE monthly_income > 70000;

-- Count users by major
SELECT major, COUNT(*) as count
FROM users
GROUP BY major;


-- 2. EXPENSE TRACKING QUERIES
-- ============================================================================

-- All expenses for a specific user (User 915 - Alice)
SELECT id, date, category, amount, description
FROM expenses
WHERE user_id = 915
ORDER BY date DESC;

-- Total expenses by category
SELECT category,
       COUNT(*) as transaction_count,
       SUM(amount) as total_spent,
       AVG(amount) as avg_amount,
       MIN(amount) as min_amount,
       MAX(amount) as max_amount
FROM expenses
GROUP BY category
ORDER BY total_spent DESC;

-- Monthly expense trend
SELECT strftime('%Y-%m', date) as month,
       COUNT(*) as transaction_count,
       SUM(amount) as monthly_total,
       AVG(amount) as avg_transaction
FROM expenses
GROUP BY month
ORDER BY month;

-- Top spenders
SELECT u.name,
       COUNT(e.id) as expense_count,
       SUM(e.amount) as total_spent,
       AVG(e.amount) as avg_spent
FROM users u
JOIN expenses e ON u.id = e.user_id
GROUP BY u.id
ORDER BY total_spent DESC;

-- Expenses above $2000
SELECT u.name, e.date, e.category, e.amount, e.description
FROM expenses e
JOIN users u ON e.user_id = u.id
WHERE e.amount > 2000
ORDER BY e.amount DESC;

-- Average monthly spending by user
SELECT u.name,
       ROUND(SUM(e.amount) / COUNT(DISTINCT strftime('%Y-%m', e.date)), 2) as avg_monthly
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
GROUP BY u.id
ORDER BY avg_monthly DESC;

-- Spending distribution (quartiles)
SELECT
  category,
  COUNT(*) as count,
  ROUND(AVG(amount), 2) as avg_amount,
  ROUND(MIN(amount), 2) as min,
  ROUND(MAX(amount), 2) as max
FROM expenses
GROUP BY category;


-- 3. HEALTH & WELLNESS QUERIES
-- ============================================================================

-- Overall health metrics
SELECT
  ROUND(AVG(sleep_hours), 1) as avg_sleep,
  ROUND(AVG(stress_level), 1) as avg_stress,
  ROUND(AVG(exercise_minutes), 1) as avg_exercise,
  ROUND(AVG(energy_level), 1) as avg_energy
FROM health_logs;

-- Health by user
SELECT u.name,
       COUNT(h.id) as log_count,
       ROUND(AVG(h.sleep_hours), 1) as avg_sleep,
       ROUND(AVG(h.stress_level), 1) as avg_stress,
       ROUND(AVG(h.exercise_minutes), 1) as avg_exercise
FROM users u
LEFT JOIN health_logs h ON u.id = h.user_id
GROUP BY u.id;

-- Recent health check-ins (last 7 entries)
SELECT u.name, h.date, h.sleep_hours, h.stress_level, h.mood, h.exercise_minutes
FROM health_logs h
JOIN users u ON h.user_id = u.id
ORDER BY h.date DESC
LIMIT 7;

-- Users with low sleep (under 6 hours average)
SELECT u.name,
       COUNT(h.id) as entries,
       ROUND(AVG(h.sleep_hours), 1) as avg_sleep,
       ROUND(AVG(h.stress_level), 1) as avg_stress
FROM users u
JOIN health_logs h ON u.id = h.user_id
GROUP BY u.id
HAVING AVG(h.sleep_hours) < 6;

-- Mood distribution
SELECT mood, COUNT(*) as count
FROM health_logs
WHERE mood IS NOT NULL
GROUP BY mood;


-- 4. FOOD & NUTRITION QUERIES
-- ============================================================================

-- All food entries with user names
SELECT u.name, f.date, f.meal_type, f.food_name, f.cost, f.calories
FROM food_logs f
JOIN users u ON f.user_id = u.id
ORDER BY f.date DESC;

-- Food spending by meal type
SELECT meal_type,
       COUNT(*) as meal_count,
       ROUND(SUM(cost), 2) as total_cost,
       ROUND(AVG(cost), 2) as avg_cost,
       ROUND(AVG(calories), 0) as avg_calories
FROM food_logs
GROUP BY meal_type;

-- Total food spending per user
SELECT u.name,
       COUNT(f.id) as meal_count,
       ROUND(SUM(f.cost), 2) as total_cost,
       ROUND(AVG(f.cost), 2) as avg_cost
FROM users u
LEFT JOIN food_logs f ON u.id = f.user_id
GROUP BY u.id;

-- High calorie meals
SELECT u.name, f.date, f.food_name, f.calories, f.cost
FROM food_logs f
JOIN users u ON f.user_id = u.id
WHERE f.calories > 800
ORDER BY f.calories DESC;

-- Homemade vs external food
SELECT CASE WHEN is_homemade = 1 THEN 'Homemade' ELSE 'External' END as type,
       COUNT(*) as count,
       ROUND(AVG(cost), 2) as avg_cost,
       ROUND(AVG(calories), 0) as avg_calories
FROM food_logs
GROUP BY is_homemade;


-- 5. TRAVEL & TRANSPORTATION QUERIES
-- ============================================================================

-- All travel records with user info
SELECT u.name, t.date, t.origin, t.destination, t.mode, t.cost, t.duration_minutes
FROM travel_logs t
JOIN users u ON t.user_id = u.id
ORDER BY t.date DESC;

-- Travel spending by mode
SELECT mode,
       COUNT(*) as trip_count,
       ROUND(SUM(cost), 2) as total_cost,
       ROUND(AVG(cost), 2) as avg_cost,
       ROUND(AVG(duration_minutes), 1) as avg_duration
FROM travel_logs
GROUP BY mode
ORDER BY total_cost DESC;

-- Most frequently traveled routes
SELECT origin, destination, COUNT(*) as trip_count
FROM travel_logs
GROUP BY origin, destination
ORDER BY trip_count DESC
LIMIT 10;

-- Travel cost per user
SELECT u.name,
       COUNT(t.id) as trip_count,
       ROUND(SUM(t.cost), 2) as total_cost,
       ROUND(AVG(t.cost), 2) as avg_cost
FROM users u
LEFT JOIN travel_logs t ON u.id = t.user_id
GROUP BY u.id;


-- 6. ROUTINE GOALS QUERIES
-- ============================================================================

-- All active goals
SELECT u.name, rg.goal_type, rg.current_value, rg.target_value, rg.status
FROM routine_goals rg
JOIN users u ON rg.user_id = u.id
WHERE rg.status = 'active'
ORDER BY u.name, rg.goal_type;

-- Goal progress percentage
SELECT u.name,
       rg.goal_type,
       ROUND((rg.current_value / NULLIF(rg.target_value, 0)) * 100, 1) as progress_percent,
       rg.status
FROM routine_goals rg
JOIN users u ON rg.user_id = u.id
ORDER BY progress_percent DESC;

-- Goals by status
SELECT goal_type, status, COUNT(*) as count
FROM routine_goals
GROUP BY goal_type, status;

-- User goal summary
SELECT u.name,
       COUNT(*) as total_goals,
       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
       ROUND(AVG(current_value), 1) as avg_progress
FROM routine_goals rg
JOIN users u ON rg.user_id = u.id
GROUP BY u.id;


-- 7. BURNOUT ASSESSMENT QUERIES
-- ============================================================================

-- Latest burnout scores
SELECT u.name, b.date, b.score, b.alert_level,
       b.current_sleep, b.current_stress, b.current_exercise
FROM burnout_scores b
JOIN users u ON b.user_id = u.id
ORDER BY b.date DESC
LIMIT 10;

-- Burnout score distribution
SELECT alert_level,
       COUNT(*) as assessment_count,
       ROUND(AVG(score), 1) as avg_score,
       MIN(score) as min_score,
       MAX(score) as max_score
FROM burnout_scores
GROUP BY alert_level;

-- Users at risk (critical burnout)
SELECT u.name,
       b.date,
       b.score,
       b.alert_level,
       ROUND(AVG(h.stress_level), 1) as stress_level,
       ROUND(AVG(h.sleep_hours), 1) as sleep_hours
FROM burnout_scores b
JOIN users u ON b.user_id = u.id
LEFT JOIN health_logs h ON b.user_id = h.user_id
WHERE b.alert_level = 'critical'
GROUP BY u.id
ORDER BY b.score ASC;

-- Burnout trend per user
SELECT u.name,
       COUNT(b.id) as assessment_count,
       ROUND(AVG(b.score), 1) as avg_score,
       b.alert_level
FROM burnout_scores b
JOIN users u ON b.user_id = u.id
GROUP BY u.id, b.alert_level;


-- 8. RECOMMENDATIONS & AI SUGGESTIONS
-- ============================================================================

-- All recommendations
SELECT u.name, r.date, r.type, r.feedback, r.was_helpful
FROM recommendations r
JOIN users u ON r.user_id = u.id
ORDER BY r.date DESC;

-- Recommendation feedback summary
SELECT type,
       COUNT(*) as total_recommendations,
       SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) as helpful,
       SUM(CASE WHEN was_helpful = 0 THEN 1 ELSE 0 END) as not_helpful,
       SUM(CASE WHEN was_helpful IS NULL THEN 1 ELSE 0 END) as pending_feedback
FROM recommendations
GROUP BY type;

-- Recent budget plans
SELECT u.name, r.date, r.type
FROM recommendations r
JOIN users u ON r.user_id = u.id
WHERE r.type = 'budget_plan'
ORDER BY r.date DESC
LIMIT 5;


-- 9. CHAT HISTORY QUERIES
-- ============================================================================

-- Recent chat interactions
SELECT u.name, c.date, c.user_message, c.ai_response
FROM chat_history c
JOIN users u ON c.user_id = u.id
ORDER BY c.date DESC
LIMIT 10;

-- User chat activity
SELECT u.name,
       COUNT(c.id) as chat_count,
       MIN(c.date) as first_chat,
       MAX(c.date) as last_chat
FROM chat_history c
JOIN users u ON c.user_id = u.id
GROUP BY u.id
ORDER BY chat_count DESC;

-- Chat frequency by date
SELECT strftime('%Y-%m-%d', date) as chat_date,
       COUNT(*) as chat_count
FROM chat_history
GROUP BY chat_date
ORDER BY chat_date DESC;


-- 10. BUDGET MEAL QUERIES
-- ============================================================================

-- All budget meals sorted by cost
SELECT name, cost, calories, category, prep_time_minutes, is_vegetarian, is_vegan
FROM budget_meals
ORDER BY cost ASC;

-- Budget meals by category
SELECT category,
       COUNT(*) as meal_count,
       ROUND(AVG(cost), 2) as avg_cost,
       ROUND(AVG(calories), 0) as avg_calories
FROM budget_meals
GROUP BY category;

-- Cheapest meals
SELECT name, cost, calories, prep_time_minutes
FROM budget_meals
ORDER BY cost ASC
LIMIT 10;

-- Best calorie-to-cost ratio
SELECT name,
       cost,
       calories,
       ROUND(calories / NULLIF(cost, 0), 2) as cal_per_dollar
FROM budget_meals
ORDER BY cal_per_dollar DESC
LIMIT 10;

-- Vegetarian options
SELECT name, cost, calories, prep_time_minutes
FROM budget_meals
WHERE is_vegetarian = 1
ORDER BY cost ASC;


-- 11. CROSS-TABLE ANALYSIS
-- ============================================================================

-- User expense and health correlation
SELECT u.name,
       COUNT(e.id) as expense_count,
       ROUND(SUM(e.amount), 2) as total_expenses,
       COUNT(DISTINCT strftime('%Y-%m', e.date)) as months,
       ROUND(AVG(h.stress_level), 1) as avg_stress,
       ROUND(AVG(h.sleep_hours), 1) as avg_sleep
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
LEFT JOIN health_logs h ON u.id = h.user_id
GROUP BY u.id
ORDER BY total_expenses DESC;

-- Comprehensive user profile
SELECT
  u.id,
  u.name,
  u.monthly_income,
  COUNT(DISTINCT e.id) as total_expenses,
  ROUND(SUM(e.amount), 2) as total_spent,
  COUNT(DISTINCT h.id) as health_logs,
  COUNT(DISTINCT f.id) as meal_logs,
  COUNT(DISTINCT c.id) as chat_sessions,
  COUNT(DISTINCT r.id) as recommendations
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
LEFT JOIN health_logs h ON u.id = h.user_id
LEFT JOIN food_logs f ON u.id = f.user_id
LEFT JOIN chat_history c ON u.id = c.user_id
LEFT JOIN recommendations r ON u.id = r.user_id
GROUP BY u.id;

-- Spending analysis: Income vs Expenses
SELECT u.name,
       u.monthly_income,
       ROUND(AVG(CASE WHEN strftime('%Y-%m', e.date) = '2026-06' THEN e.amount ELSE 0 END), 2) as june_daily_avg,
       u.daily_budget,
       CASE
         WHEN ROUND(AVG(CASE WHEN strftime('%Y-%m', e.date) = '2026-06' THEN e.amount ELSE 0 END), 2) > u.daily_budget
         THEN 'OVER BUDGET'
         ELSE 'WITHIN BUDGET'
       END as budget_status
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
GROUP BY u.id;

-- ============================================================================
-- END OF SAMPLE QUERIES
-- ============================================================================
