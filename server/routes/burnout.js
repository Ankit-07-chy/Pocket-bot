// ============================================================
// FEATURE 4: BURNOUT DETECTION (Most Important Feature)
// Daily check-ins, baseline comparison, early warning system
// ============================================================
const express = require('express');
const router = express.Router();

module.exports = function (db, authenticateToken) {

    // POST /api/health/checkin - Daily wellness check-in
    router.post('/checkin', authenticateToken, (req, res) => {
        try {
            const { sleep_hours, stress_level, mood, study_hours, exercise_minutes, social_activity, energy_level, notes, date } = req.body;

            // Validate inputs
            if (sleep_hours === undefined || stress_level === undefined || !mood) {
                return res.status(400).json({ error: 'Sleep hours, stress level, and mood are required.' });
            }

            const validMoods = ['happy', 'neutral', 'anxious', 'sad', 'overwhelmed'];
            if (!validMoods.includes(mood.toLowerCase())) {
                return res.status(400).json({
                    error: `Invalid mood. Use: ${validMoods.join(', ')}`
                });
            }

            if (stress_level < 1 || stress_level > 10) {
                return res.status(400).json({ error: 'Stress level must be between 1 and 10.' });
            }

            const checkinDate = date || new Date().toISOString().split('T')[0];

            // Insert or update today's check-in (one per day)
            db.prepare(`
        INSERT INTO health_logs (user_id, date, sleep_hours, stress_level, mood, study_hours, exercise_minutes, social_activity, energy_level, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, date) DO UPDATE SET
          sleep_hours = excluded.sleep_hours,
          stress_level = excluded.stress_level,
          mood = excluded.mood,
          study_hours = excluded.study_hours,
          exercise_minutes = excluded.exercise_minutes,
          social_activity = excluded.social_activity,
          energy_level = excluded.energy_level,
          notes = excluded.notes
      `).run(
                req.user.id, checkinDate,
                sleep_hours, stress_level, mood.toLowerCase(),
                study_hours || 0, exercise_minutes || 0,
                social_activity || 0, energy_level || 5,
                notes || ''
            );

            // Calculate and store burnout score
            const burnoutResult = calculateBurnoutScore(db, req.user.id, checkinDate);

            res.status(201).json({
                message: 'Check-in recorded!',
                date: checkinDate,
                burnout: burnoutResult
            });
        } catch (err) {
            console.error('Health checkin error:', err);
            res.status(500).json({ error: 'Failed to record check-in.' });
        }
    });

    // GET /api/burnout/score - Get current burnout score
    router.get('/score', authenticateToken, (req, res) => {
        try {
            // Get most recent burnout score
            const latest = db.prepare(`
        SELECT * FROM burnout_scores
        WHERE user_id = ?
        ORDER BY date DESC LIMIT 1
      `).get(req.user.id);

            // Count total check-in days
            const checkinCount = db.prepare(`
        SELECT COUNT(*) as days FROM health_logs WHERE user_id = ?
      `).get(req.user.id);

            // Get most recent daily check-in log
            const latestCheckin = db.prepare(`
        SELECT * FROM health_logs WHERE user_id = ? ORDER BY date DESC LIMIT 1
      `).get(req.user.id);

            if (!latest) {
                return res.json({
                    score: null,
                    alert_level: 'unknown',
                    message: 'No burnout data yet. Complete daily check-ins for at least 7 days to get your score.',
                    days_logged: checkinCount.days,
                    days_needed: Math.max(0, 7 - checkinCount.days),
                    latest_checkin: latestCheckin
                });
            }

            // Interpretation of the score
            const interpretation = getAlertInterpretation(latest.score);

            res.json({
                score: latest.score,
                alert_level: latest.alert_level,
                date: latest.date,
                baseline: {
                    sleep: latest.baseline_sleep,
                    stress: latest.baseline_stress,
                    exercise: latest.baseline_exercise
                },
                current: {
                    sleep: latest.current_sleep,
                    stress: latest.current_stress,
                    exercise: latest.current_exercise
                },
                interpretation,
                days_logged: checkinCount.days,
                latest_checkin: latestCheckin
            });
        } catch (err) {
            console.error('Burnout score error:', err);
            res.status(500).json({ error: 'Failed to get burnout score.' });
        }
    });

    // GET /api/burnout/alert - Get burnout warnings
    router.get('/alert', authenticateToken, (req, res) => {
        try {
            const latest = db.prepare(`
        SELECT * FROM burnout_scores
        WHERE user_id = ?
        ORDER BY date DESC LIMIT 1
      `).get(req.user.id);

            if (!latest || latest.score <= 3) {
                return res.json({ has_alert: false, message: 'You\'re doing well! Keep it up.' });
            }

            // Get recent health data for context
            const recentHealth = db.prepare(`
        SELECT * FROM health_logs
        WHERE user_id = ?
        ORDER BY date DESC LIMIT 3
      `).all(req.user.id);

            // Build specific warnings based on what's declining
            const warnings = [];

            if (latest.current_sleep < latest.baseline_sleep - 1) {
                warnings.push({
                    type: 'sleep',
                    message: `Your sleep dropped to ${latest.current_sleep.toFixed(1)}hrs (baseline: ${latest.baseline_sleep.toFixed(1)}hrs). Try to get more rest.`
                });
            }

            if (latest.current_stress > latest.baseline_stress + 1.5) {
                warnings.push({
                    type: 'stress',
                    message: `Your stress level is ${latest.current_stress.toFixed(1)}/10 (baseline: ${latest.baseline_stress.toFixed(1)}/10). Consider taking breaks.`
                });
            }

            if (latest.current_exercise < 10) {
                warnings.push({
                    type: 'exercise',
                    message: 'You haven\'t been exercising much. Even a 5-minute walk helps!'
                });
            }

            // Check for overwhelmed mood streak
            const overwhelmedDays = recentHealth.filter(h => h.mood === 'overwhelmed').length;
            if (overwhelmedDays >= 2) {
                warnings.push({
                    type: 'mood',
                    message: 'You\'ve been feeling overwhelmed for multiple days. Please consider talking to someone.'
                });
            }

            res.json({
                has_alert: true,
                score: latest.score,
                alert_level: latest.alert_level,
                warnings,
                recommendations: getRecoveryRecommendations(latest.score, warnings)
            });
        } catch (err) {
            console.error('Burnout alert error:', err);
            res.status(500).json({ error: 'Failed to get alert.' });
        }
    });

    // GET /api/burnout/trends - 30-day burnout trends
    router.get('/trends', authenticateToken, (req, res) => {
        try {
            const { days } = req.query;
            const lookback = parseInt(days) || 30;

            // Burnout scores over time
            const scores = db.prepare(`
        SELECT date, score, alert_level, current_sleep, current_stress, current_exercise
        FROM burnout_scores
        WHERE user_id = ? AND date >= date('now', ?)
        ORDER BY date ASC
      `).all(req.user.id, `-${lookback} days`);

            // Health log trends
            const healthTrends = db.prepare(`
        SELECT date, sleep_hours, stress_level, mood, exercise_minutes, energy_level
        FROM health_logs
        WHERE user_id = ? AND date >= date('now', ?)
        ORDER BY date ASC
      `).all(req.user.id, `-${lookback} days`);

            // Calculate averages for the period
            const avgSleep = healthTrends.reduce((sum, h) => sum + h.sleep_hours, 0) / (healthTrends.length || 1);
            const avgStress = healthTrends.reduce((sum, h) => sum + h.stress_level, 0) / (healthTrends.length || 1);
            const avgExercise = healthTrends.reduce((sum, h) => sum + h.exercise_minutes, 0) / (healthTrends.length || 1);

            // Mood distribution
            const moodCounts = {};
            healthTrends.forEach(h => {
                moodCounts[h.mood] = (moodCounts[h.mood] || 0) + 1;
            });

            res.json({
                burnout_scores: scores,
                health_trends: healthTrends,
                averages: {
                    sleep: Math.round(avgSleep * 10) / 10,
                    stress: Math.round(avgStress * 10) / 10,
                    exercise_minutes: Math.round(avgExercise)
                },
                mood_distribution: moodCounts,
                period_days: lookback,
                total_checkins: healthTrends.length
            });
        } catch (err) {
            console.error('Burnout trends error:', err);
            res.status(500).json({ error: 'Failed to get trends.' });
        }
    });

    // GET /api/burnout/recommendations - What to do about burnout
    router.get('/recommendations', authenticateToken, (req, res) => {
        try {
            const latest = db.prepare(`
        SELECT * FROM burnout_scores WHERE user_id = ? ORDER BY date DESC LIMIT 1
      `).get(req.user.id);

            const recentHealth = db.prepare(`
        SELECT * FROM health_logs WHERE user_id = ? ORDER BY date DESC LIMIT 7
      `).all(req.user.id);

            if (!latest) {
                return res.json({
                    recommendations: ['Start with daily check-ins to build your baseline!'],
                    priority: 'low'
                });
            }

            const recs = getRecoveryRecommendations(latest.score, []);

            // Add personalized tips based on specific data
            if (recentHealth.length > 0) {
                const avgStudy = recentHealth.reduce((s, h) => s + h.study_hours, 0) / recentHealth.length;
                if (avgStudy > 8) {
                    recs.push('You\'re studying ' + avgStudy.toFixed(1) + ' hours/day on average. Schedule breaks every 45 minutes.');
                }
            }

            res.json({
                score: latest.score,
                alert_level: latest.alert_level,
                recommendations: recs,
                priority: latest.score >= 7 ? 'high' : latest.score >= 4 ? 'medium' : 'low'
            });
        } catch (err) {
            console.error('Burnout recommendations error:', err);
            res.status(500).json({ error: 'Failed to get recommendations.' });
        }
    });

    return router;
};

// ============================================================
// BURNOUT SCORE ALGORITHM
// Compares current metrics to user's personal baseline
// ============================================================
function calculateBurnoutScore(db, userId, date) {
    // Count how many days of data we have
    const dayCount = db.prepare(`
    SELECT COUNT(*) as days FROM health_logs WHERE user_id = ?
  `).get(userId);

    // Need at least 7 days for a baseline
    if (dayCount.days < 7) {
        return {
            score: null,
            message: `Need ${7 - dayCount.days} more days of data to calculate burnout score.`,
            days_until_baseline: 7 - dayCount.days
        };
    }

    // STEP 1: Get baseline (first 7 days of data)
    const baseline = db.prepare(`
    SELECT
      AVG(sleep_hours) as avg_sleep,
      AVG(stress_level) as avg_stress,
      AVG(exercise_minutes) as avg_exercise
    FROM (
      SELECT sleep_hours, stress_level, exercise_minutes
      FROM health_logs
      WHERE user_id = ?
      ORDER BY date ASC
      LIMIT 7
    )
  `).get(userId);

    // STEP 2: Get current averages (last 7 days)
    const current = db.prepare(`
    SELECT
      AVG(sleep_hours) as avg_sleep,
      AVG(stress_level) as avg_stress,
      AVG(exercise_minutes) as avg_exercise
    FROM health_logs
    WHERE user_id = ? AND date >= date(?, '-7 days')
  `).get(userId, date);

    // Get today's mood
    const todayMood = db.prepare(`
    SELECT mood FROM health_logs WHERE user_id = ? AND date = ?
  `).get(userId, date);

    // Count days with no exercise in last 7 days
    const noExerciseDays = db.prepare(`
    SELECT COUNT(*) as days
    FROM health_logs
    WHERE user_id = ? AND date >= date(?, '-7 days') AND exercise_minutes < 5
  `).get(userId, date);

    // STEP 3: Calculate penalties
    let score = 0;

    // Sleep penalty: +2 if sleeping 1.5+ hours less than baseline
    const sleepDrop = baseline.avg_sleep - (current.avg_sleep || 0);
    if (sleepDrop > 1.5) score += 2;

    // Stress penalty: +2 if stress is 2+ points above baseline
    const stressRise = (current.avg_stress || 0) - baseline.avg_stress;
    if (stressRise > 2) score += 2;

    // Exercise penalty: +1 if less than 2 days of exercise in last 7
    if (noExerciseDays.days >= 5) score += 1;

    // Mood penalty: +2 if currently overwhelmed
    if (todayMood && todayMood.mood === 'overwhelmed') score += 2;

    // Additional: +1 if mood is anxious or sad
    if (todayMood && (todayMood.mood === 'anxious' || todayMood.mood === 'sad')) score += 1;

    // STEP 4: Determine alert level
    let alertLevel = 'good';
    if (score >= 10) alertLevel = 'crisis';
    else if (score >= 7) alertLevel = 'high';
    else if (score >= 4) alertLevel = 'moderate';
    else alertLevel = 'good';

    // STEP 5: Store the score
    db.prepare(`
    INSERT INTO burnout_scores (user_id, date, baseline_sleep, baseline_stress, baseline_exercise, current_sleep, current_stress, current_exercise, score, alert_level)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, date) DO UPDATE SET
      baseline_sleep = excluded.baseline_sleep,
      baseline_stress = excluded.baseline_stress,
      baseline_exercise = excluded.baseline_exercise,
      current_sleep = excluded.current_sleep,
      current_stress = excluded.current_stress,
      current_exercise = excluded.current_exercise,
      score = excluded.score,
      alert_level = excluded.alert_level
  `).run(
        userId, date,
        baseline.avg_sleep, baseline.avg_stress, baseline.avg_exercise,
        current.avg_sleep || 0, current.avg_stress || 0, current.avg_exercise || 0,
        score, alertLevel
    );

    return {
        score,
        alert_level: alertLevel,
        interpretation: getAlertInterpretation(score),
        baseline: { sleep: baseline.avg_sleep, stress: baseline.avg_stress },
        current: { sleep: current.avg_sleep, stress: current.avg_stress }
    };
}

// ---- Interpret alert levels ----
function getAlertInterpretation(score) {
    if (score >= 10) return 'Crisis mode - Please reach out to a counselor or trusted person immediately.';
    if (score >= 7) return 'High burnout risk - Take a break today. Consider seeking support.';
    if (score >= 4) return 'Getting stressed - Schedule breaks, prioritize sleep, and reduce workload if possible.';
    return 'You\'re doing well! Keep maintaining your current habits.';
}

// ---- Recovery recommendations based on score ----
function getRecoveryRecommendations(score, warnings) {
    const recs = [];

    if (score >= 7) {
        recs.push('Talk to someone you trust - a friend, family member, or counselor.');
        recs.push('Take today off from studying if possible. Rest is productive.');
        recs.push('Try a 10-minute walk outside. Fresh air helps reset your mind.');
    }

    if (score >= 4) {
        recs.push('Use the Pomodoro technique: 25 min work, 5 min break.');
        recs.push('Set a hard stop time tonight - no studying after 9 PM.');
        recs.push('Do one thing you enjoy today, even if it\'s just 15 minutes.');
    }

    if (score < 4) {
        recs.push('You\'re doing great! Keep your current routine going.');
        recs.push('Consider helping a friend who might be struggling.');
    }

    // Add specific recommendations based on warnings
    const hasNoSleep = warnings.some(w => w.type === 'sleep');
    const hasNoExercise = warnings.some(w => w.type === 'exercise');

    if (hasNoSleep) {
        recs.push('Try to get to bed 30 minutes earlier tonight.');
        recs.push('Avoid screens 1 hour before bed.');
    }

    if (hasNoExercise) {
        recs.push('Even a 5-minute stretch or walk counts as exercise!');
    }

    return recs;
}
