// ============================================================
// AUTH ROUTES - MVP Mode (no service account key)
// Firebase handles auth client-side. This syncs users to our DB.
// ============================================================
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();

module.exports = function (db, authenticateToken) {

    // POST /api/auth/register - Fallback (non-Firebase) registration
    router.post('/register', async (req, res) => {
        try {
            const { email, password, name, major, year, monthly_income } = req.body;

            if (!email || !password || !name) {
                return res.status(400).json({ error: 'Email, password, and name are required.' });
            }

            const existingUser = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
            if (existingUser) {
                return res.status(400).json({ error: 'Email already registered.' });
            }

            const hashedPassword = await bcrypt.hash(password, 10);
            const income = monthly_income || 0;
            const dailyBudget = income > 0 ? Math.round((income / 30) * 100) / 100 : 0;

            const result = db.prepare(`
        INSERT INTO users (email, password, name, major, year, monthly_income, daily_budget)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(email, hashedPassword, name, major || '', year || 1, income, dailyBudget);

            const token = jwt.sign(
                { id: result.lastInsertRowid, email, name },
                process.env.JWT_SECRET,
                { expiresIn: '7d' }
            );

            res.status(201).json({
                message: 'Account created!',
                token,
                user: { id: result.lastInsertRowid, email, name, major, year }
            });
        } catch (err) {
            console.error('Register error:', err);
            res.status(500).json({ error: 'Server error during registration.' });
        }
    });

    // POST /api/auth/login - Fallback (non-Firebase) login
    router.post('/login', async (req, res) => {
        try {
            const { email, password } = req.body;

            if (!email || !password) {
                return res.status(400).json({ error: 'Email and password are required.' });
            }

            const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
            if (!user) {
                return res.status(401).json({ error: 'Invalid email or password.' });
            }

            if (user.password.startsWith('firebase:')) {
                return res.status(401).json({ error: 'This account uses Google sign-in. Use the Google button.' });
            }

            const valid = await bcrypt.compare(password, user.password);
            if (!valid) {
                return res.status(401).json({ error: 'Invalid email or password.' });
            }

            const token = jwt.sign(
                { id: user.id, email: user.email, name: user.name },
                process.env.JWT_SECRET,
                { expiresIn: '7d' }
            );

            res.json({
                message: 'Login successful!',
                token,
                user: { id: user.id, email: user.email, name: user.name, major: user.major, year: user.year, monthly_income: user.monthly_income, daily_budget: user.daily_budget }
            });
        } catch (err) {
            console.error('Login error:', err);
            res.status(500).json({ error: 'Server error during login.' });
        }
    });

    // POST /api/auth/firebase-sync - Create/find user after Firebase login
    // No service account needed — trusts client-side Firebase auth
    router.post('/firebase-sync', (req, res) => {
        try {
            const { name, email, uid, major, student_type, year, monthly_income } = req.body;

            if (!email) {
                return res.status(400).json({ error: 'Email is required.' });
            }

            let user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

            if (!user) {
                // Create new user from Firebase
                const displayName = name || email.split('@')[0];
                const income = monthly_income || 0;
                const dailyBudget = income > 0 ? Math.round((income / 30) * 100) / 100 : 0;

                const result = db.prepare(`
          INSERT INTO users (email, password, name, major, student_type, year, monthly_income, daily_budget)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).run(email, `firebase:${uid || 'user'}`, displayName, major || '', student_type || '', year || 1, income, dailyBudget);

                user = { id: result.lastInsertRowid, email, name: displayName, major: major || '', student_type: student_type || '', year: year || 1, monthly_income: income, daily_budget: dailyBudget };
            } else if (name && name !== user.name) {
                // Update name if changed
                db.prepare('UPDATE users SET name = ? WHERE id = ?').run(name, user.id);
                user.name = name;
            }

            res.json({
                message: 'User synced!',
                user: { id: user.id, email: user.email, name: user.name, major: user.major, student_type: user.student_type, year: user.year, monthly_income: user.monthly_income, daily_budget: user.daily_budget }
            });
        } catch (err) {
            console.error('Firebase sync error:', err);
            res.status(500).json({ error: 'Failed to sync user.' });
        }
    });

    // GET /api/auth/profile
    router.get('/profile', authenticateToken, (req, res) => {
        const user = db.prepare(`
      SELECT id, email, name, major, student_type, year, monthly_income, daily_budget, dietary_preferences, emergency_contact, created_at
      FROM users WHERE id = ?
    `).get(req.user.id);

        if (!user) return res.status(404).json({ error: 'User not found.' });
        res.json(user);
    });

    // PUT /api/auth/profile
    router.put('/profile', authenticateToken, (req, res) => {
        const { name, major, student_type, year, monthly_income, daily_budget, dietary_preferences, emergency_contact } = req.body;

        db.prepare(`
      UPDATE users SET
        name = COALESCE(?, name), major = COALESCE(?, major), student_type = COALESCE(?, student_type), year = COALESCE(?, year),
        monthly_income = COALESCE(?, monthly_income), daily_budget = COALESCE(?, daily_budget),
        dietary_preferences = COALESCE(?, dietary_preferences), emergency_contact = COALESCE(?, emergency_contact)
      WHERE id = ?
    `).run(name, major, student_type, year, monthly_income, daily_budget, dietary_preferences, emergency_contact, req.user.id);

        res.json({ message: 'Profile updated.' });
    });

    return router;
};
