import React, { useState, useEffect } from 'react';
import { expenses, burnout, routine } from '../api';

function Dashboard() {
    const [summary, setSummary] = useState(null);
    const [burnoutData, setBurnoutData] = useState(null);
    const [tips, setTips] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            const [expSummary, burnoutScore, routineTips] = await Promise.all([
                expenses.summary(7).catch(() => null),
                burnout.score().catch(() => null),
                routine.tips().catch(() => null)
            ]);
            setSummary(expSummary);
            setBurnoutData(burnoutScore);
            setTips(routineTips?.tips || []);
        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    }

    if (loading) return <div className="loading">Loading dashboard...</div>;

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>Dashboard</h1>

            {/* Stats Overview */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">${summary?.total_spent?.toFixed(2) || '0.00'}</div>
                    <div className="stat-label">Spent this week</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">${summary?.daily_average?.toFixed(2) || '0.00'}</div>
                    <div className="stat-label">Daily average</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: getBurnoutColor(burnoutData?.score) }}>
                        {burnoutData?.score !== null && burnoutData?.score !== undefined ? burnoutData.score : '—'}
                    </div>
                    <div className="stat-label">Burnout Score</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{burnoutData?.days_logged || 0}</div>
                    <div className="stat-label">Days tracked</div>
                </div>
            </div>

            {/* Burnout Alert */}
            {burnoutData && burnoutData.score >= 4 && (
                <div className={`alert ${burnoutData.score >= 7 ? 'alert-danger' : 'alert-warning'}`}>
                    <strong>⚠️ Burnout Alert:</strong> {burnoutData.interpretation}
                </div>
            )}

            {/* Spending Alert */}
            {summary?.over_budget && (
                <div className="alert alert-warning">
                    <strong>💰 Budget Alert:</strong> You're spending ${summary.daily_average.toFixed(2)}/day, above your ${summary.daily_budget.toFixed(2)}/day budget.
                </div>
            )}

            {/* Quick Data Entry - no data message */}
            {!summary?.total_spent && !burnoutData?.score && (
                <div className="card">
                    <h2>👋 Welcome! Let's get started</h2>
                    <p style={{ marginTop: '10px', color: 'var(--text-light)' }}>
                        Start tracking your expenses, health, and habits to get personalized insights.
                        The more data you log, the better PocketBuddy can help you!
                    </p>
                    <div style={{ marginTop: '16px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                        <a href="/expenses" className="btn btn-primary">💰 Add Expense</a>
                        <a href="/burnout" className="btn btn-secondary">🧠 Daily Check-in</a>
                        <a href="/food" className="btn btn-secondary">🍕 Log Meal</a>
                    </div>
                </div>
            )}

            {/* Category Breakdown */}
            {summary?.by_category?.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h2>Spending by Category (7 days)</h2>
                    </div>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Total</th>
                                    <th>Transactions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {summary.by_category.map(cat => (
                                    <tr key={cat.category}>
                                        <td style={{ textTransform: 'capitalize' }}>{getCategoryEmoji(cat.category)} {cat.category}</td>
                                        <td>${cat.total.toFixed(2)}</td>
                                        <td>{cat.count}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Daily Tips */}
            {tips.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h2>💡 Tips for Today</h2>
                    </div>
                    <ul style={{ paddingLeft: '20px' }}>
                        {tips.map((tip, i) => (
                            <li key={i} style={{ marginBottom: '8px', fontSize: '0.9rem' }}>{tip}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

function getBurnoutColor(score) {
    if (score === null || score === undefined) return 'var(--text-light)';
    if (score >= 7) return 'var(--danger)';
    if (score >= 4) return 'var(--warning)';
    return 'var(--success)';
}

function getCategoryEmoji(category) {
    const emojis = { food: '🍕', transport: '🚌', entertainment: '🎬', utilities: '💡', education: '📚', health: '💊', other: '📦' };
    return emojis[category] || '📦';
}

export default Dashboard;
