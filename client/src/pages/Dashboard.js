import React, { useState, useEffect } from 'react';
import { expenses, burnout, routine, auth, support, v1 } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, Tooltip, AreaChart, Area, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

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
    const [pythonDashboard, setPythonDashboard] = useState(null);
    const [burnoutTrends, setBurnoutTrends] = useState(null);
    const [tips, setTips] = useState([]);
    const [loading, setLoading] = useState(true);

    // AI Rec State
    const [activeRecTab, setActiveRecTab] = useState('financial');

    // Peer Support Connect State
    const [peerConnecting, setPeerConnecting] = useState(false);
    const [peerConnection, setPeerConnection] = useState(null);

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
            const profileData = await auth.getProfile().catch(() => null);
            setProfile(profileData);

            if (profileData && profileData.id) {
                const pId = profileData.id;
                const [dashData, burnoutHistory, expSummary7, routineTips] = await Promise.all([
                    v1.dashboard(pId).catch(() => null),
                    burnout.trends(30).catch(() => null),
                    expenses.summary(7).catch(() => null),
                    routine.tips().catch(() => null)
                ]);

                setPythonDashboard(dashData);
                setBurnoutTrends(burnoutHistory);
                setSummary7(expSummary7);
                setTips(routineTips?.tips || []);
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

    async function handleConnectPeer() {
        if (!profile || peerConnecting) return;
        setPeerConnecting(true);
        try {
            const conn = await support.peerConnect({ issue_category: 'burnout' });
            setPeerConnection(conn);
        } catch (err) {
            console.error('Peer connection error:', err);
            alert('Unable to connect with a peer mentor right now. Please try again later.');
        } finally {
            setPeerConnecting(false);
        }
    }

    if (loading) return <div className="loading">Loading dashboard...</div>;

    const showOnboarding = profile && (!profile.student_type || profile.monthly_income <= 0);

    // Python Wellness Metrics Fallbacks
    const wellnessScore = pythonDashboard?.wellness_score ?? 80;
    const wellnessCategory = pythonDashboard?.wellness_category ?? 'Good';
    const burnoutRisk = pythonDashboard?.burnout_risk ?? 'low';
    const burnoutScore = pythonDashboard?.burnout_score ?? 20;
    const financialHealthScore = pythonDashboard?.financial_health ?? 75;
    const finDetails = pythonDashboard?.financial_health_details ?? { budget_adherence: 80, savings_score: 75, forecast_score: 70 };
    const rawRecommendations = pythonDashboard?.recommendations ?? { financial: [], wellness: [], productivity: [] };

    // Standard Math Fallbacks
    const monthlyIncome = profile?.monthly_income || 0;
    const spentThisMonth = pythonDashboard?.current_month_summary?.total_spent_so_far || 0;
    const remainingBalance = pythonDashboard?.remaining_budget?.total_remaining ?? Math.max(0, monthlyIncome - spentThisMonth);
    const safeDailySpendingLimit = pythonDashboard?.remaining_budget?.safe_daily_limit ?? 0;

    const getWellnessColor = (score) => {
        if (score >= 80) return '#10b981'; // Mint Green
        if (score >= 50) return '#f59e0b'; // Gold
        return '#ff4a5a'; // Coral Red
    };

    const getBurnoutRiskColor = (risk) => {
        const r = risk.toLowerCase();
        if (r === 'high' || r === 'crisis') return '#ff4a5a';
        if (r === 'medium' || r === 'moderate') return '#f59e0b';
        return '#10b981';
    };

    // Category Donut Chart
    const donutData = summary7?.by_category?.map(cat => ({
        name: cat.category.charAt(0).toUpperCase() + cat.category.slice(1),
        value: cat.total,
        color: CATEGORY_COLORS[cat.category.toLowerCase()] || '#94a3b8'
    })) || [];

    // Monthly Spending Trend
    const monthlyTrendData = summary7?.daily?.map(d => {
        const dateObj = new Date(d.date);
        return {
            date: dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' }),
            amount: d.daily_total
        };
    }) || [];

    // Burnout Trend Data
    const burnoutTrendData = burnoutTrends?.burnout_scores?.map(item => ({
        date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: item.score * 10
    })) || [];

    // Forecast Chart data comparing actual vs budget vs projected spend
    const projectedSpend = pythonDashboard?.forecast?.projected_spend ?? spentThisMonth;
    const totalBudget = pythonDashboard?.budget_plan?.total_budget ?? monthlyIncome;

    const forecastChartData = [
        { name: 'Spent So Far', value: Math.round(spentThisMonth), color: '#6366f1' },
        { name: 'Monthly Budget', value: Math.round(totalBudget), color: '#10b981' },
        { name: 'Projected Spend', value: Math.round(projectedSpend), color: projectedSpend > totalBudget ? '#ff4a5a' : '#f59e0b' }
    ];

    const currentTabRecommendations = rawRecommendations[activeRecTab] || [];

    return (
        <div style={{ position: 'relative' }}>
            
            {/* Top Notification Banner if burnout risk is high */}
            {(burnoutRisk === 'high' || burnoutRisk === 'crisis') && !peerConnection && (
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="alert alert-danger" 
                    style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '12px' }}
                >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '1.5rem' }}>🧠</span>
                        <div>
                            <strong>Wellness Warning:</strong> Your burnout risk has been predicted as <strong>{burnoutRisk.toUpperCase()}</strong>. It is highly recommended to take some rest.
                        </div>
                    </div>
                    <button 
                        className="btn btn-secondary btn-small" 
                        onClick={handleConnectPeer} 
                        disabled={peerConnecting}
                        style={{ background: 'white', color: '#991b1b', border: '1px solid #ff8383', padding: '6px 14px' }}
                    >
                        {peerConnecting ? 'Finding Mentor...' : '🤝 Connect with Student Peer Mentor'}
                    </button>
                </motion.div>
            )}

            {/* Peer Connection Success Modal */}
            <AnimatePresence>
                {peerConnection && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="alert alert-success" 
                        style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '1.5rem' }}>🎉</span>
                            <div>
                                <strong>Peer Supporter Connected!</strong> You've been connected to <strong>Mentor #{peerConnection.peer_id}</strong>.
                            </div>
                        </div>
                        <p style={{ fontSize: '0.82rem', marginLeft: '28px', opacity: 0.9 }}>
                            Expertise: {peerConnection.peer_expertise?.join(', ')} | Reputation: {peerConnection.peer_reputation}/100. Feel free to contact them for stress and financial wellness support.
                        </p>
                        <button className="btn btn-secondary btn-small" onClick={() => setPeerConnection(null)} style={{ marginLeft: '28px', background: 'white' }}>
                            Acknowledge
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            <h1 style={{ marginBottom: '24px' }}>📊 Student Wellness Dashboard</h1>

            {/* Premium Stats Grid */}
            <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '24px' }}>
                
                {/* 1. Wellness Score Circular Card */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between', padding: '24px', margin: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-light)', letterSpacing: '0.05em' }}>WELLNESS SCORE</span>
                        <span className={`badge badge-${wellnessCategory.toLowerCase()}`}>{wellnessCategory}</span>
                    </div>
                    <div style={{ margin: '16px 0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <div style={{
                            width: '100px', height: '100px', borderRadius: '50%',
                            border: `8px solid ${getWellnessColor(wellnessScore)}`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: `0 0 16px ${getWellnessColor(wellnessScore)}25`
                        }}>
                            <span style={{ fontSize: '2.2rem', fontWeight: 800, color: getWellnessColor(wellnessScore) }}>{wellnessScore}</span>
                        </div>
                    </div>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-light)', textAlign: 'center' }}>
                        Weighted wellness status
                    </span>
                </div>

                {/* 2. Burnout Risk Level Card */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '24px', margin: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-light)', letterSpacing: '0.05em' }}>BURNOUT RISK</span>
                        <span style={{ fontSize: '1.2rem' }}>🧠</span>
                    </div>
                    <div style={{ margin: '12px 0' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 800, color: getBurnoutRiskColor(burnoutRisk) }}>
                            {burnoutRisk.toUpperCase()}
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-light)', marginTop: '4px' }}>
                            Burnout Score: {burnoutScore}/100
                        </div>
                    </div>
                    <div className="progress-bar" style={{ height: '6px', margin: '4px 0' }}>
                        <div className="progress-bar-fill" style={{
                            width: `${burnoutScore}%`,
                            backgroundColor: getBurnoutRiskColor(burnoutRisk)
                        }} />
                    </div>
                </div>

                {/* 3. Financial Health Circular Index Card */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '24px', margin: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-light)', letterSpacing: '0.05em' }}>FINANCIAL HEALTH</span>
                        <span style={{ fontSize: '1.2rem' }}>💰</span>
                    </div>
                    <div style={{ margin: '12px 0' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 800, color: getWellnessColor(financialHealthScore) }}>
                            {financialHealthScore}/100
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-light)', marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>Adherence:</span> <strong>{finDetails.budget_adherence}%</strong>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>Savings Score:</span> <strong>{finDetails.savings_score}%</strong>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>Forecast Score:</span> <strong>{finDetails.forecast_score}%</strong>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 4. Remaining Budget & Daily Spending Card */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '24px', margin: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-light)', letterSpacing: '0.05em' }}>REMAINING BUDGET</span>
                        <span style={{ fontSize: '1.2rem' }}>💳</span>
                    </div>
                    <div style={{ margin: '12px 0' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 800, color: remainingBalance > 0 ? 'var(--success)' : 'var(--danger)' }}>
                            ₹{remainingBalance.toFixed(0)}
                        </div>
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-light)', marginTop: '4px' }}>
                            Safe daily limit: ₹{safeDailySpendingLimit.toFixed(0)}/day
                        </div>
                    </div>
                    <div className="progress-bar" style={{ height: '6px', margin: '4px 0' }}>
                        <div className="progress-bar-fill good" style={{
                            width: `${totalBudget > 0 ? Math.min(100, (spentThisMonth / totalBudget) * 100) : 0}%`,
                            background: spentThisMonth > totalBudget ? 'var(--danger)' : 'linear-gradient(90deg, #6366f1, #818cf8)'
                        }} />
                    </div>
                </div>

            </div>

            {/* Active System Alerts */}
            {pythonDashboard?.alerts?.length > 0 && (
                <div className="card" style={{ padding: '20px 24px', borderLeft: '5px solid var(--danger)' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>🚨</span> Active Stress & Overspending Alerts
                    </h3>
                    <ul style={{ listStyleType: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {pythonDashboard.alerts.map((alert, i) => (
                            <li key={i} style={{ fontSize: '0.88rem', color: 'var(--text-light)', display: 'flex', gap: '6px' }}>
                                <strong>•</strong> {alert.message || alert}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Quick Action Hub */}
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '24px' }}>
                <a href="/expenses" className="btn btn-primary">➕ Log Expense</a>
                <a href="/burnout" className="btn btn-secondary">🧘 Wellness Check-in</a>
                <a href="/food" className="btn btn-secondary">🍕 Feed Companion</a>
            </div>

            {/* Premium Interactive Charts Panel */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                
                {/* Chart 1: Daily Spending Trends */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '320px' }}>
                    <div className="card-header">
                        <h2>Monthly Spending Trend</h2>
                    </div>
                    {monthlyTrendData.length > 0 ? (
                        <div style={{ flex: 1, width: '100%', height: '200px', marginTop: '16px' }}>
                            <ResponsiveContainer width="100%" height={200}>
                                <AreaChart data={monthlyTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorSpent" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.4}/>
                                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                                    <XAxis dataKey="date" stroke="var(--text-light)" fontSize="0.75rem" />
                                    <YAxis stroke="var(--text-light)" fontSize="0.75rem" />
                                    <Tooltip formatter={(value) => `₹${value.toFixed(2)}`} />
                                    <Area type="monotone" dataKey="amount" stroke="var(--primary)" fillOpacity={1} fill="url(#colorSpent)" strokeWidth={2.5} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <p>Not enough spending records. Log expenses to view daily spending trend!</p>
                        </div>
                    )}
                </div>

                {/* Chart 2: Burnout Score History */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '320px' }}>
                    <div className="card-header">
                        <h2>Burnout Trend History (30 Days)</h2>
                    </div>
                    {burnoutTrendData.length > 0 ? (
                        <div style={{ flex: 1, width: '100%', height: '200px', marginTop: '16px' }}>
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={burnoutTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                                    <XAxis dataKey="date" stroke="var(--text-light)" fontSize="0.75rem" />
                                    <YAxis stroke="var(--text-light)" fontSize="0.75rem" />
                                    <Tooltip formatter={(value) => `${value}/100`} />
                                    <Line type="monotone" dataKey="score" stroke="#ff8e53" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <p>Perform daily wellness check-ins to view burnout score trend!</p>
                        </div>
                    )}
                </div>

                {/* Chart 3: Forecast comparisons (Budget vs Spent vs Projection) */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '320px' }}>
                    <div className="card-header">
                        <h2>Budget Forecast Analysis</h2>
                    </div>
                    <div style={{ flex: 1, width: '100%', height: '200px', marginTop: '16px' }}>
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={forecastChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
                                <XAxis dataKey="name" stroke="var(--text-light)" fontSize="0.75rem" />
                                <YAxis stroke="var(--text-light)" fontSize="0.75rem" />
                                <Tooltip formatter={(value) => `₹${value}`} />
                                <Bar dataKey="value" fill="var(--primary)" radius={[8, 8, 0, 0]}>
                                    {forecastChartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>

            {/* Bottom Panels: AI Recommendations & Gemini Purchase Advisor */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                
                {/* 1. Dynamic Categorized Recommendation Panel */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: '320px' }}>
                    <div className="card-header" style={{ marginBottom: '12px' }}>
                        <h2>💡 Wellness & Budget Recommendations</h2>
                    </div>
                    {/* Tab Navigation */}
                    <div style={{ display: 'flex', gap: '6px', marginBottom: '16px', background: 'rgba(0,0,0,0.03)', padding: '4px', borderRadius: '10px' }}>
                        {[
                            { key: 'financial', label: '💰 Financial' },
                            { key: 'wellness', label: '🧘 Wellness' },
                            { key: 'productivity', label: '🚀 Productivity' }
                        ].map(tab => (
                            <button 
                                key={tab.key}
                                className="btn"
                                onClick={() => setActiveRecTab(tab.key)}
                                style={{
                                    flex: 1, padding: '8px 12px', fontSize: '0.8rem', borderRadius: '8px',
                                    background: activeRecTab === tab.key ? 'white' : 'transparent',
                                    color: activeRecTab === tab.key ? 'var(--text)' : 'var(--text-light)',
                                    boxShadow: activeRecTab === tab.key ? '0 2px 6px rgba(0,0,0,0.05)' : 'none'
                                }}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                    {currentTabRecommendations.length > 0 ? (
                        <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
                            {currentTabRecommendations.map((rec, i) => (
                                <li key={i} style={{ fontSize: '0.9rem', lineHeight: '1.5', color: 'var(--text-light)' }}>
                                    {rec}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className="empty-state" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <p>No suggestions in this category. Perform check-ins or log expenses to generate advice!</p>
                        </div>
                    )}
                </div>

                {/* 2. Purchase Advisor Box */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div className="card-header">
                        <h2>🛒 AI Purchase Advisor</h2>
                    </div>
                    <form onSubmit={handleGetAdvice} style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div className="form-row" style={{ display: 'flex', gap: '12px' }}>
                            <div className="form-group" style={{ flex: 2 }}>
                                <label htmlFor="item-name">Item Name</label>
                                <input
                                    id="item-name"
                                    type="text"
                                    placeholder="e.g. Noise Cancelling Headset"
                                    value={itemName}
                                    onChange={(e) => setItemName(e.target.value)}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>
                            <div className="form-group" style={{ flex: 1 }}>
                                <label htmlFor="item-cost">Cost (₹)</label>
                                <input
                                    id="item-cost"
                                    type="number"
                                    placeholder="3500"
                                    value={itemCost}
                                    onChange={(e) => setItemCost(e.target.value)}
                                    required
                                    style={{ width: '100%' }}
                                />
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary" disabled={adviceLoading} style={{ alignSelf: 'flex-start' }}>
                            {adviceLoading ? 'Consulting Gemini...' : 'Consult Gemini Advisor'}
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
                                        {adviceResult.affordable ? '✓ AFFORDABLE' : '⚠ BUDGET OVERRUN'}
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

            {/* Static tips fallback */}
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
                                <label htmlFor="onboarding-budget">Monthly Pocket Money (₹)</label>
                                <input
                                    id="onboarding-budget"
                                    type="number"
                                    min="1"
                                    placeholder="e.g. 15000"
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

export default Dashboard;
