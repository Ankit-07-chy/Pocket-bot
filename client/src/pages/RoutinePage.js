import React, { useState, useEffect } from 'react';
import { routine } from '../api';

function RoutinePage() {
    const [plan, setPlan] = useState(null);
    const [progress, setProgress] = useState(null);
    const [form, setForm] = useState({ goal_type: 'sleep', target_value: '' });
    const [success, setSuccess] = useState('');
    const [tab, setTab] = useState('plan');

    useEffect(() => { loadData(); }, []);

    async function loadData() {
        try {
            const [planData, progressData] = await Promise.all([
                routine.plan().catch(() => null),
                routine.progress().catch(() => null)
            ]);
            setPlan(planData);
            setProgress(progressData);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleSetGoal(e) {
        e.preventDefault();
        setSuccess('');
        try {
            const result = await routine.setGoal({
                goal_type: form.goal_type,
                target_value: parseFloat(form.target_value)
            });
            setSuccess(result.message);
            setForm({ ...form, target_value: '' });
            loadData();
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>🏃 Healthy Routine</h1>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button className={`btn ${tab === 'plan' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('plan')}>My Plan</button>
                <button className={`btn ${tab === 'goals' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('goals')}>Set Goals</button>
                <button className={`btn ${tab === 'progress' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('progress')}>Progress</button>
            </div>

            {/* My Plan */}
            {tab === 'plan' && (
                <div>
                    {plan?.has_plan ? (
                        <>
                            <div className="alert alert-info">{plan.overall_message}</div>
                            {plan.goals.map((goal, i) => (
                                <div className="card" key={i}>
                                    <div className="card-header">
                                        <h2>{getGoalEmoji(goal.goal_type)} {goal.goal_type} - Week {goal.week_number}</h2>
                                        <span className={`badge ${goal.on_track ? 'badge-good' : 'badge-moderate'}`}>
                                            {goal.on_track ? 'On Track' : 'Needs Attention'}
                                        </span>
                                    </div>

                                    <div style={{ marginBottom: '12px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                                            <span>Current: {goal.current_average} {getGoalUnit(goal.goal_type)}</span>
                                            <span>Target: {goal.weekly_target} {getGoalUnit(goal.goal_type)}</span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className={`progress-bar-fill ${goal.progress_percent >= 70 ? 'good' : goal.progress_percent >= 40 ? 'moderate' : 'high'}`}
                                                style={{ width: `${goal.progress_percent}%` }}
                                            />
                                        </div>
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>{goal.progress_percent}% of weekly target</span>
                                    </div>

                                    <p style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>
                                        Final goal: {goal.final_target} {getGoalUnit(goal.goal_type)}
                                    </p>

                                    {goal.daily_tips?.length > 0 && (
                                        <ul style={{ marginTop: '10px', paddingLeft: '20px', fontSize: '0.85rem' }}>
                                            {goal.daily_tips.map((tip, j) => <li key={j}>{tip}</li>)}
                                        </ul>
                                    )}
                                </div>
                            ))}
                        </>
                    ) : (
                        <div className="card">
                            <div className="empty-state">
                                <h3>No active goals yet</h3>
                                <p>Set a goal to get your personalized routine plan!</p>
                            </div>
                            {plan?.suggested_goals && (
                                <div style={{ marginTop: '16px' }}>
                                    <h4 style={{ fontSize: '0.9rem', marginBottom: '8px' }}>Suggested goals:</h4>
                                    {plan.suggested_goals.map((sg, i) => (
                                        <p key={i} style={{ fontSize: '0.85rem', marginBottom: '4px' }}>
                                            {getGoalEmoji(sg.type)} {sg.suggestion}
                                        </p>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Set Goals */}
            {tab === 'goals' && (
                <div className="card">
                    <div className="card-header"><h2>Set a Wellness Goal</h2></div>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-light)', marginBottom: '16px' }}>
                        We'll build up gradually over 4 weeks - small steps lead to lasting habits!
                    </p>

                    {success && <div className="alert alert-success">{success}</div>}

                    <form onSubmit={handleSetGoal}>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="goal-type">Goal Type</label>
                                <select id="goal-type" value={form.goal_type}
                                    onChange={(e) => setForm({ ...form, goal_type: e.target.value })}>
                                    <option value="sleep">😴 Sleep (hours/night)</option>
                                    <option value="exercise">🏃 Exercise (minutes/day)</option>
                                    <option value="stress">🧘 Stress (target max level)</option>
                                    <option value="study">📚 Study (hours/day)</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label htmlFor="target">Target Value</label>
                                <input id="target" type="number" step="0.5" min="0" value={form.target_value}
                                    onChange={(e) => setForm({ ...form, target_value: e.target.value })}
                                    placeholder={getPlaceholder(form.goal_type)} required />
                            </div>
                        </div>
                        <button type="submit" className="btn btn-primary">Set Goal</button>
                    </form>

                    <div style={{ marginTop: '20px', padding: '16px', background: '#f8fafc', borderRadius: '8px' }}>
                        <h4 style={{ fontSize: '0.9rem', marginBottom: '8px' }}>How it works:</h4>
                        <ol style={{ paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--text-light)' }}>
                            <li>We check your current baseline from health data</li>
                            <li>Week 1: Small 25% improvement toward your goal</li>
                            <li>Week 2: 50% of the way there</li>
                            <li>Week 3: 75% - almost there!</li>
                            <li>Week 4: Goal reached! 🎉</li>
                        </ol>
                    </div>
                </div>
            )}

            {/* Progress */}
            {tab === 'progress' && (
                <div>
                    {progress?.goals?.length > 0 ? (
                        <>
                            <div className="stats-grid">
                                <div className="stat-card">
                                    <div className="stat-value">{progress.total_active_goals}</div>
                                    <div className="stat-label">Active Goals</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value">{progress.total_completed}</div>
                                    <div className="stat-label">Completed</div>
                                </div>
                            </div>
                            {progress.goals.map((g, i) => (
                                <div className="card" key={i}>
                                    <h3 style={{ marginBottom: '8px' }}>{getGoalEmoji(g.goal_type)} {g.goal_type} ({g.status})</h3>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                                        <span>Start: {g.start_value}</span>
                                        <span>Current: {g.current_average}</span>
                                        <span>Target: {g.target_value}</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-bar-fill good" style={{ width: `${g.progress_percent}%` }} />
                                    </div>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>
                                        {g.progress_percent}% toward goal (Week {g.week_number})
                                    </span>
                                </div>
                            ))}
                        </>
                    ) : (
                        <div className="empty-state"><p>Set some goals to start tracking progress!</p></div>
                    )}
                </div>
            )}
        </div>
    );
}

function getGoalEmoji(type) {
    const emojis = { sleep: '😴', exercise: '🏃', stress: '🧘', study: '📚', hydration: '💧' };
    return emojis[type] || '🎯';
}

function getGoalUnit(type) {
    const units = { sleep: 'hrs', exercise: 'min', stress: '/10', study: 'hrs' };
    return units[type] || '';
}

function getPlaceholder(type) {
    const placeholders = { sleep: 'e.g. 8', exercise: 'e.g. 30', stress: 'e.g. 4', study: 'e.g. 6' };
    return placeholders[type] || '';
}

export default RoutinePage;
