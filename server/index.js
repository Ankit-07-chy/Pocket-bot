// ============================================================
// POCKETBUDDY SERVER - MVP Mode
// Firebase auth handled client-side, no service account needed
// ============================================================
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');

const { initializeDatabase } = require('./database/setup');
const { seedBudgetMeals } = require('./database/seed');
const { createAuthMiddleware } = require('./middleware/auth');

const app = express();
const PORT = process.env.PORT || 5000;

// ---- Database ----
const dbPath = path.resolve(process.env.DB_PATH || './database/pocketbuddy.db');
const db = initializeDatabase(dbPath);
seedBudgetMeals(db);

// Auth middleware (decodes Firebase tokens + our JWT)
const authenticateToken = createAuthMiddleware(db);

// ---- Middleware ----
app.use(cors());
app.use(express.json());

// ---- Routes ----
app.use('/api/auth', require('./routes/auth')(db, authenticateToken));
app.use('/api/expenses', require('./routes/expenses')(db, authenticateToken));
app.use('/api/food', require('./routes/food')(db, authenticateToken));
app.use('/api/travel', require('./routes/travel')(db, authenticateToken));
app.use('/api/health', require('./routes/burnout')(db, authenticateToken));
app.use('/api/burnout', require('./routes/burnout')(db, authenticateToken));
app.use('/api/routine', require('./routes/routine')(db, authenticateToken));
app.use('/api/chat', require('./routes/support')(db, authenticateToken));
app.use('/api/support', require('./routes/support')(db, authenticateToken));

// ---- Static files (production) ----
if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.join(__dirname, '../client/build')));
    app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
    });
}

// ---- Health check ----
app.get('/api/health-check', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ---- Start ----
app.listen(PORT, () => {
    console.log(`\n🚀 PocketBuddy running → http://localhost:${PORT}`);
    console.log(`📊 DB: ${dbPath}`);
    console.log(`🔐 Auth: Firebase (client-side) + JWT fallback`);
    console.log(`   No service account needed for MVP\n`);
});

module.exports = app;
