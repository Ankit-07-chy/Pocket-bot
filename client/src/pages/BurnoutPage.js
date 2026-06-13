import React, { useState, useEffect } from 'react';
import { burnout } from '../api';

function BurnoutPage() {
    const [score, setScore] = useState(null);
    const [alertData, setAlertData] = useState(null);
    const [form, setForm] = useState({
        sleep_hours: '', stress_level: 5, mood: 'neutral',
        study_hours: '', exercise_minutes: '', energy_level: 5, notes: ''
    });
    const [success, setSuccess] = useState('');
    const [tab, setTab] = useState('checkin');

    useEffect(() => { loadData(); }, []);

    async function loadData() {
        try {
            const [scoreData, alertInfo] = await Promise.all([
                burnout.score().catch(() => null),
                burnout.alert().catch(() => null)
            ]);
            setScore(scoreData);
            setAlertData(alertInfo);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleCheckin(e) {
        e.preventDefault();
        setSuccess('');
        try {
            const result = await burnout.checkin({
                sleep_hours: parseFloat(form.sleep_hours),
                stress_level: parseInt(form.stress_level),
                mood: form.mood,
                study_hours: parseFloat(form.study_hours) || 0,
                exercise_minutes: parseInt(form.exercise_minutes) || 0,
                energy_level: parseInt(form.energy_level),
                notes: form.notes
            });
            setSuccess('Check-in recorded! ' + (result.burnout?.interpretation || ''));
            loadData();
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>🧠 Burnout Detection</h1>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button className={`btn ${tab === 'checkin' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('checkin')}>Daily Check-in</button>
                <button className={`btn ${tab === 'status' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('status')}>Status</button>
            </div>

            {/* Daily Check-in */}
            {tab === 'checkin' && (
                <div className="card">
                    <div className="card-header"><h2>How are you today?</h2></div>
                    {success && <div className="alert alert-success">{success}</div>}

                    <form onSubmit={handleCheckin}>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="sleep">Hours of sleep last night</label>
                                <input id="sleep" type="number" step="0.5" min="0" max="24" value={form.sleep_hours}
                                    onChange={(e) => setForm({ ...form, sleep_hours: e.target.value })}
                                    placeholder="7" required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="stress">Stress level (1 = calm, 10 = extremely stressed)</label>
                                <input id="stress" type="range" min="1" max="10" value={form.stress_level}
                                    onChange={(e) => setForm({ ...form, stress_level: e.target.value })} />
                                <span style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>
                                    {form.stress_level}/10 {form.stress_level >= 8 ? '😰' : form.stress_level >= 5 ? '😐' : '😊'}
                                </span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="mood">How's your mood?</label>
                            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                {['happy', 'neutral', 'anxious', 'sad', 'overwhelmed'].map(m => (
                                    <button key={m} type="button"
                                        className={`btn ${form.mood === m ? 'btn-primary' : 'btn-secondary'} btn-small`}
                                        onClick={() => setForm({ ...form, mood: m })}>
                                        {m === 'happy' ? '😊' : m === 'neutral' ? '😐' : m === 'anxious' ? '😟' : m === 'sad' ? '😢' : '😩'} {m}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="study">Study hours today</label>
                                <input id="study" type="number" step="0.5" min="0" max="24" value={form.study_hours}
                                    onChange={(e) => setForm({ ...form, study_hours: e.target.value })}
                                    placeholder="4" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="exercise">Exercise (minutes)</label>
                                <input id="exercise" type="number" min="0" value={form.exercise_minutes}
                                    onChange={(e) => setForm({ ...form, exercise_minutes: e.target.value })}
                                    placeholder="30" />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="energy">Energy level (1-10)</label>
                            <input id="energy" type="range" min="1" max="10" value={form.energy_level}
                                onChange={(e) => setForm({ ...form, energy_level: e.target.value })} />
                            <span style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>{form.energy_level}/10</span>
                        </div>

                        <div className="form-group">
                            <label htmlFor="notes">Notes (optional)</label>
                            <textarea id="notes" rows="2" value={form.notes}
                                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                                placeholder="Anything else on your mind?" />
                        </div>

                        <button type="submit" className="btn btn-primary">Submit Check-in</button>
                    </form>
                </div>
            )}

            {/* Burnout Status */}
            {tab === 'status' && (
                <div>
                    {/* Score Display */}
                    {score && (
                        <div className="card" style={{ textAlign: 'center' }}>
                            <h2 style={{ marginBottom: '16px' }}>Your Burnout Score</h2>
                            {score.score !== null ? (
                                <>
                                    <div style={{ fontSize: '4rem', fontWeight: '700', color: getBurnoutColor(score.score) }}>
                                        {score.score}
                                    </div>
                                    <span className={`badge badge-${score.alert_level}`} style={{ fontSize: '0.9rem', marginBottom: '12px' }}>
                                        {score.alert_level.toUpperCase()}
                                    </span>
                                    <p style={{ marginTop: '12px', color: 'var(--text-light)' }}>{score.interpretation}</p>

                                    {/* Baseline vs Current */}
                                    <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', textAlign: 'left' }}>
                                        <div>
                                            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Baseline (Week 1)</h4>
                                            <p>Sleep: {score.baseline?.sleep?.toFixed(1)} hrs</p>
                                            <p>Stress: {score.baseline?.stress?.toFixed(1)}/10</p>
                                        </div>
                                        <div>
                                            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Current (Last 7 days)</h4>
                                            <p>Sleep: {score.current?.sleep?.toFixed(1)} hrs</p>
                                            <p>Stress: {score.current?.stress?.toFixed(1)}/10</p>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div>
                                    <p style={{ fontSize: '1.1rem' }}>📊 {score.message}</p>
                                    {score.days_needed > 0 && (
                                        <div className="progress-bar" style={{ marginTop: '16px' }}>
                                            <div className="progress-bar-fill good"
                                                style={{ width: `${((7 - score.days_needed) / 7) * 100}%` }} />
                                        </div>
                                    )}
                                    <p style={{ marginTop: '8px', color: 'var(--text-light)' }}>
                                        {score.days_logged}/7 days logged
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Alerts & Warnings */}
                    {alertData?.has_alert && (
                        <div className="card">
                            <div className="card-header"><h2>⚠️ Warnings</h2></div>
                            {alertData.warnings.map((w, i) => (
                                <div key={i} className="alert alert-warning" style={{ marginBottom: '8px' }}>
                                    {w.message}
                                </div>
                            ))}
                            {alertData.recommendations?.length > 0 && (
                                <div style={{ marginTop: '16px' }}>
                                    <h3 style={{ fontSize: '1rem', marginBottom: '8px' }}>Recommended Actions:</h3>
                                    <ul style={{ paddingLeft: '20px' }}>
                                        {alertData.recommendations.map((r, i) => (
                                            <li key={i} style={{ marginBottom: '6px', fontSize: '0.9rem' }}>{r}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {!score && (
                        <div className="empty-state">
                            <p>Complete your first daily check-in to start tracking burnout!</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function getBurnoutColor(score) {
    if (score >= 7) return 'var(--danger)';
    if (score >= 4) return 'var(--warning)';
    return 'var(--success)';
}

export default BurnoutPage;
