import React, { useState, useEffect } from 'react';
import { expenses, burnout, routine, auth, support } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

const CATEGORY_COLORS = {
    food: '#ff6b6b',         // Coral Rose
    transport: '#6366f1',     // Indigo
    entertainment: '#ff8e53', // Peach
    utilities: '#f59e0b',     // Gold
    education: '#10b981',     // Mint
    health: '#a855f7',        // Purple
    other: '#94a3b8'          // Slate
};

function Dashboard() {
    const [profile, setProfile] = useState(null);
    const [summary7, setSummary7] = useState(null);
    const [summary30, setSummary30] = useState(null);
    const [burnoutData, setBurnoutData] = useState(null);
    const [trends, setTrends] = useState(null);
    const [tips, setTips] = useState([]);
    const [loading, setLoading] = useState(true);

    // AI Rec State
    const [aiRec, setAiRec] = useState(null);
    const [aiRecLoading, setAiRecLoading] = useState(false);

    // Purchase Advisor State
    const [itemName, setItemName] = useState('');
    const [itemCost, setItemCost] = useState('');
    const [adviceResult, setAdviceResult] = useState(null);
    const [adviceLoading, setAdviceLoading] = useState(false);

    // Onboarding Form State
    const [onboardingForm, setOnboardingForm] = useState({
        name: '',
        student_type: 'hosteller',
        monthly_income: '',
        major: '',
        year: 1
    });
    const [onboardingError, setOnboardingError] = useState('');

    useEffect(() => {
        loadDashboard();
    }, []);

    useEffect(() => {
        if (profile) {
            setOnboardingForm({
                name: profile.name || '',
                student_type: profile.student_type || 'hosteller',
                monthly_income: profile.monthly_income > 0 ? profile.monthly_income : '',
                major: profile.major || '',
                year: profile.year || 1
            });
        }
    }, [profile]);

    async function loadDashboard() {
        try {
            const [profileData, expSummary7, expSummary30, scoreData, routineTips, trendData] = await Promise.all([
                auth.getProfile().catch(() => null),
                expenses.summary(7).catch(() => null),
                expenses.summary(30).catch(() => null),
                burnout.score().catch(() => null),
                routine.tips().catch(() => null),
                expenses.trends().catch(() => null)
            ]);

            setProfile(profileData);
            setSummary7(expSummary7);
            setSummary30(expSummary30);
            setBurnoutData(scoreData);
            setTips(routineTips?.tips || []);
            setTrends(trendData);

            // Fetch AI recommendation asynchronously after fast loads
            if (profileData && profileData.student_type && profileData.monthly_income > 0) {
                setAiRecLoading(true);
                support.getAIRecommendation()
                    .then(rec => setAiRec(rec))
                    .catch(err => console.error('AI Rec error:', err))
                    .finally(() => setAiRecLoading(false));
            }
        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleOnboardingSubmit(e) {
        e.preventDefault();
        setOnboardingError('');
        try {
            const income = parseFloat(onboardingForm.monthly_income) || 0;
            const dailyBudget = income > 0 ? Math.round((income / 30) * 100) / 100 : 0;
            await auth.updateProfile({
                name: onboardingForm.name,
                student_type: onboardingForm.student_type,
                monthly_income: income,
                daily_budget: dailyBudget,
                major: onboardingForm.major,
                year: parseInt(onboardingForm.year)
            });
            loadDashboard();
        } catch (err) {
            console.error('Onboarding save error:', err);
            setOnboardingError(err.message || 'Failed to save onboarding settings. Please try again.');
        }
    }

    async function handleGetAdvice(e) {
        e.preventDefault();
        if (!itemName || !itemCost) return;
        setAdviceLoading(true);
        setAdviceResult(null);
        try {
            const data = await support.getPurchaseAdvice({
                name: itemName,
                cost: parseFloat(itemCost)
            });
            setAdviceResult(data);
        } catch (err) {
            console.error('Purchase advice error:', err);
        } finally {
            setAdviceLoading(false);
        }
    }

    if (loading) return <div className="loading">Loading dashboard...</div>;

    const showOnboarding = profile && (!profile.student_type || profile.monthly_income <= 0);

    // Date calculations
    const getRemainingDaysInMonth = () => {
        const today = new Date();
        const totalDays = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
        return Math.max(1, totalDays - today.getDate() + 1);
    };

    const monthlyIncome = profile?.monthly_income || 0;
    const spentThisMonth = summary30?.total_spent || 0;
    const remainingBalance = Math.max(0, monthlyIncome - spentThisMonth);
    const remainingDays = getRemainingDaysInMonth();
    const safeDailySpendingLimit = remainingDays > 0 ? (remainingBalance / remainingDays) : 0;

    // Burnout Risk
    const latestCheckin = burnoutData?.latest_checkin;
    const getBurnoutRisk = () => {
        if (!latestCheckin) return 'No check-in';
        const sleep = latestCheckin.sleep_hours;
        const stress = latestCheckin.stress_level;
        if (sleep < 6 && stress > 7) return 'High';
        if (sleep < 7 && stress > 5) return 'Medium';
        return 'Low';
    };

    const burnoutRisk = getBurnoutRisk();

    const getBurnoutRiskColor = (risk) => {
        if (risk === 'High') return 'var(--danger)';
        if (risk === 'Medium') return 'var(--warning)';
        if (risk === 'Low') return 'var(--success)';
        return 'var(--text-light)';
    };

    const getMoodEmoji = (mood) => {
        const moods = {
            happy: '😀',
            neutral: '😐',
            sad: '😔',
            stressed: '😫',
            anxious: '😟',
            overwhelmed: '😫'
        };
        return moods[mood?.toLowerCase()] || '—';
    };

    // Chart Data mapping
    const donutData = summary7?.by_category?.map(cat => ({
        name: cat.category.charAt(0).toUpperCase() + cat.category.slice(1),
        value: cat.total,
        color: CATEGORY_COLORS[cat.category.toLowerCase()] || '#94a3b8'
    })) || [];

    const trendChartData = trends?.daily?.map(d => {
        const dateObj = new Date(d.date);
        const formattedDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
        return {
            date: formattedDate,
            amount: d.daily_total
        };
    }) || [];

    return (
        <div style={{ position: 'relative' }}>
            <h1 style={{ marginBottom: '24px' }}>📊 Student Dashboard</h1>

            {/* Stats Overview */}
            <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <div className="stat-card">
                    <div className="stat-value">${monthlyIncome.toFixed(2)}</div>
                    <div className="stat-label">Monthly Pocket Money</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">${spentThisMonth.toFixed(2)}</div>
                    <div className="stat-label">Spent This Month</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: remainingBalance > 0 ? 'var(--success)' : 'var(--danger)' }}>
                        ${remainingBalance.toFixed(2)}
                    </div>
                    <div className="stat-label">Remaining Balance</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: safeDailySpendingLimit > 0 ? 'var(--primary)' : 'var(--danger)' }}>
                        ${safeDailySpendingLimit.toFixed(2)}
                    </div>
                    <div className="stat-label">Safe Daily Limit</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: getBurnoutRiskColor(burnoutRisk) }}>
                        {burnoutRisk}
                    </div>
                    <div className="stat-label">Burnout Risk</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ fontSize: '2.5rem' }}>
                        {latestCheckin ? getMoodEmoji(latestCheckin.mood) : '—'}
                    </div>
                    <div className="stat-label">Today's Mood</div>
                </div>
            </div>

            {/* Alerts & Notifications */}
            {burnoutData?.score >= 4 && (
                <div className={`alert ${burnoutData.score >= 7 ? 'alert-danger' : 'alert-warning'}`} style={{ marginBottom: '16px' }}>
                    <strong>⚠️ Burnout Alert:</strong> {burnoutData.interpretation}
                </div>
            )}

            {summary7?.over_budget && (
                <div className="alert alert-warning" style={{ marginBottom: '24px' }}>
                    <strong>💰 Budget Alert:</strong> Your average daily spending (${summary7.daily_average.toFixed(2)}) is exceeding your budgeted daily limit (${summary7.daily_budget.toFixed(2)}).
                </div>
            )}

            {/* Quick Actions (if user is fresh or wants quick access) */}
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '24px' }}>
                <a href="/expenses" className="btn btn-primary">💰 Add Expense</a>
                <a href="/burnout" className="btn btn-secondary">🧠 Daily Check-in</a>
                <a href="/food" className="btn btn-secondary">🍕 Log Meal</a>
            </div>

            {/* Charts Section */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                {/* Donut Chart (Spending Category) */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '380px' }}>
                    <div className="card-header">
                        <h2>Spending by Category (7 days)</h2>
                    </div>
                    {donutData.length > 0 ? (
                        <div style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', gap: '16px' }}>
                            <div style={{ width: '200px', height: '200px' }}>
                                <PieChart width={200} height={200}>
                                    <Pie
                                        data={donutData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={4}
                                        dataKey="value"
                                    >
                                        {donutData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                                </PieChart>
                            </div>
                            <div style={{ flex: 1, minWidth: '150px' }}>
                                {donutData.map((d, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '3px', backgroundColor: d.color }}></span>
                                            <span style={{ textTransform: 'capitalize' }}>{getCategoryEmoji(d.name.toLowerCase())} {d.name}</span>
                                        </div>
                                        <strong style={{ color: 'var(--text-light)' }}>${d.value.toFixed(2)}</strong>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <p>No recent expenses found. Start adding expenses to view category analysis!</p>
                        </div>
                    )}
                </div>

                {/* Area Chart (Trend) */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '380px' }}>
                    <div className="card-header">
                        <h2>Monthly Expense Trend</h2>
                    </div>
                    {trendChartData.length > 0 ? (
                        <div style={{ flex: 1, width: '100%', height: '220px', marginTop: '16px' }}>
                            <ResponsiveContainer width="100%" height={260}>
                                <AreaChart data={trendChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorSpent" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                                    <XAxis dataKey="date" stroke="var(--text-light)" fontSize="0.75rem" />
                                    <YAxis stroke="var(--text-light)" fontSize="0.75rem" />
                                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                                    <Area type="monotone" dataKey="amount" stroke="var(--primary)" fillOpacity={1} fill="url(#colorSpent)" strokeWidth={2.5} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <p>Not enough data to calculate daily trends. Log daily spending to update chart!</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Bottom Section: AI Recommendations & Purchase Advisor */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                {/* AI Recommendation Box */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="card-header">
                        <h2>🤖 Gemini AI Recommendation</h2>
                    </div>
                    {aiRecLoading ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '24px 0' }}>
                            <div className="loading-bar" style={{ width: '80%', height: '14px', borderRadius: '4px', background: 'rgba(255,255,255,0.4)', animation: 'pulse 1.5s infinite' }}></div>
                            <div className="loading-bar" style={{ width: '95%', height: '14px', borderRadius: '4px', background: 'rgba(255,255,255,0.4)', animation: 'pulse 1.5s infinite' }}></div>
                            <div className="loading-bar" style={{ width: '60%', height: '14px', borderRadius: '4px', background: 'rgba(255,255,255,0.4)', animation: 'pulse 1.5s infinite' }}></div>
                        </div>
                    ) : aiRec ? (
                        <div style={{ marginTop: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                                <span className={`badge badge-${aiRec.type === 'burnout' || aiRec.type === 'alert' ? 'danger' : aiRec.type === 'finance' ? 'warning' : 'good'}`}>
                                    {aiRec.type?.toUpperCase() || 'INSIGHT'}
                                </span>
                                <span style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>
                                    Generated {new Date(aiRec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                            <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text)' }}>
                                {aiRec.message}
                            </p>
                        </div>
                    ) : (
                        <div className="empty-state" style={{ padding: '24px 0' }}>
                            <p>No recommendations yet. Complete onboarding and log wellness data to trigger AI advice!</p>
                        </div>
                    )}
                </div>

                {/* Purchase Advisor Card */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="card-header">
                        <h2>🛍️ AI Purchase Advisor</h2>
                    </div>
                    <form onSubmit={handleGetAdvice} style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div className="form-row" style={{ display: 'flex', gap: '12px' }}>
                            <div className="form-group" style={{ flex: 2 }}>
                                <label htmlFor="item-name">Item Name</label>
                                <input
                                    id="item-name"
                                    type="text"
                                    placeholder="e.g. Mechanical Keyboard"
                                    value={itemName}
                                    onChange={(e) => setItemName(e.target.value)}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>
                            <div className="form-group" style={{ flex: 1 }}>
                                <label htmlFor="item-cost">Cost ($)</label>
                                <input
                                    id="item-cost"
                                    type="number"
                                    placeholder="75"
                                    value={itemCost}
                                    onChange={(e) => setItemCost(e.target.value)}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary" disabled={adviceLoading} style={{ alignSelf: 'flex-start' }}>
                            {adviceLoading ? 'Consulting Gemini...' : 'Should I Buy This?'}
                        </button>
                    </form>

                    <AnimatePresence>
                        {adviceResult && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                style={{
                                    marginTop: '16px',
                                    padding: '16px',
                                    borderRadius: '12px',
                                    border: `1.5px solid ${adviceResult.affordable ? 'var(--success)' : 'var(--danger)'}`,
                                    background: 'rgba(255, 255, 255, 0.4)'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                    <span className={`badge ${adviceResult.affordable ? 'badge-good' : 'badge-danger'}`} style={{ color: adviceResult.affordable ? 'var(--success)' : 'var(--danger)' }}>
                                        {adviceResult.affordable ? '✓ AFFORDABLE' : '⚠ BUDGET IMPACT'}
                                    </span>
                                </div>
                                <p style={{ fontSize: '0.9rem', lineHeight: '1.5', margin: 0 }}>
                                    {adviceResult.message}
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Tips for Today */}
            {tips.length > 0 && (
                <div className="card" style={{ marginBottom: '24px' }}>
                    <div className="card-header">
                        <h2>💡 Tips for Today</h2>
                    </div>
                    <ul style={{ paddingLeft: '20px', marginTop: '8px' }}>
                        {tips.map((tip, i) => (
                            <li key={i} style={{ marginBottom: '8px', fontSize: '0.9rem' }}>{tip}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* ONBOARDING OVERLAY MODAL */}
            {showOnboarding && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    background: 'rgba(15, 23, 42, 0.45)',
                    backdropFilter: 'blur(16px)',
                    WebkitBackdropFilter: 'blur(16px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 9999,
                    overflowY: 'auto',
                    padding: '40px 10px'
                }}>
                    <div className="card" style={{
                        maxWidth: '480px',
                        width: '90%',
                        padding: '32px 28px',
                        border: '1px solid rgba(255, 255, 255, 0.7)',
                        boxShadow: 'var(--shadow-md)',
                        margin: 'auto'
                    }}>
                        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '8px' }}>🎒</div>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Welcome to PocketBuddy!</h2>
                            <p style={{ color: 'var(--text-light)', fontSize: '0.9rem', marginTop: '4px' }}>
                                Let's configure your academic budget and lifestyle profile.
                            </p>
                        </div>

                        {onboardingError && (
                            <div className="alert alert-danger" style={{ marginBottom: '16px', fontSize: '0.85rem', padding: '10px 14px' }}>
                                <strong>⚠️ Error:</strong> {onboardingError}
                            </div>
                        )}

                        <form onSubmit={handleOnboardingSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div className="form-group">
                                <label htmlFor="onboarding-name">Full Name</label>
                                <input
                                    id="onboarding-name"
                                    type="text"
                                    value={onboardingForm.name}
                                    onChange={(e) => setOnboardingForm({ ...onboardingForm, name: e.target.value })}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="onboarding-student-type">Student Type</label>
                                <select
                                    id="onboarding-student-type"
                                    value={onboardingForm.student_type}
                                    onChange={(e) => setOnboardingForm({ ...onboardingForm, student_type: e.target.value })}
                                    required
                                    style={{ width: '100%' }}
                                >
                                    <option value="hosteller">Hosteller 🏠</option>
                                    <option value="day_scholar">Day Scholar 🚌</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="onboarding-budget">Monthly Pocket Money ($)</label>
                                <input
                                    id="onboarding-budget"
                                    type="number"
                                    min="1"
                                    placeholder="e.g. 500"
                                    value={onboardingForm.monthly_income}
                                    onChange={(e) => setOnboardingForm({ ...onboardingForm, monthly_income: e.target.value })}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>

                            <div className="form-row" style={{ display: 'flex', gap: '12px' }}>
                                <div className="form-group" style={{ flex: 1 }}>
                                    <label htmlFor="onboarding-major">Major</label>
                                    <input
                                        id="onboarding-major"
                                        type="text"
                                        placeholder="e.g. CS"
                                        value={onboardingForm.major}
                                        onChange={(e) => setOnboardingForm({ ...onboardingForm, major: e.target.value })}
                                        style={{ width: '100%' }}
                                    />
                                </div>
                                <div className="form-group" style={{ flex: 1 }}>
                                    <label htmlFor="onboarding-year">Academic Year</label>
                                    <select
                                        id="onboarding-year"
                                        value={onboardingForm.year}
                                        onChange={(e) => setOnboardingForm({ ...onboardingForm, year: parseInt(e.target.value) })}
                                        style={{ width: '100%' }}
                                    >
                                        <option value={1}>1st Year</option>
                                        <option value={2}>2nd Year</option>
                                        <option value={3}>3rd Year</option>
                                        <option value={4}>4th Year</option>
                                        <option value={5}>Graduate</option>
                                    </select>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '8px', padding: '12px' }}>
                                Complete Setup & Enter 🚀
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

function getCategoryEmoji(category) {
    const emojis = { food: '🍕', transport: '🚌', entertainment: '🎬', utilities: '💡', education: '📚', health: '💊', other: '📦' };
    return emojis[category] || '📦';
}

export default Dashboard;
