import React, { useState, useEffect } from 'react';
import { burnout } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';

const cardVariants = {
    enter: { scale: 0.95, y: 30, opacity: 0 },
    center: { scale: 1, y: 0, opacity: 1, transition: { duration: 0.3 } },
    exit: { y: -300, opacity: 0, transition: { duration: 0.3 } }
};

function BurnoutPage() {
    const [score, setScore] = useState(null);
    const [alertData, setAlertData] = useState(null);
    const [form, setForm] = useState({
        sleep_hours: 7,
        stress_level: 5,
        mood: 'neutral',
        study_hours: 4,
        exercise_minutes: 30,
        energy_level: 5,
        notes: ''
    });
    const [currentCard, setCurrentCard] = useState(0); // 0 = sleep, 1 = stress, 2 = mood/habits
    const [success, setSuccess] = useState('');
    const [tab, setTab] = useState('checkin');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

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

    const triggerConfetti = () => {
        const duration = 2 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

        const randomInRange = (min, max) => Math.random() * (max - min) + min;

        const interval = setInterval(function() {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } });
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } });
        }, 250);
    };

    async function submitCheckin() {
        if (isSubmitting) return;
        setIsSubmitting(true);
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
            
            triggerConfetti();
            setSuccess('Check-in recorded successfully!');
            setTimeout(() => {
                setTab('status');
                loadData();
                setCurrentCard(0); // Reset for next check-in
                setIsSubmitting(false);
                setSuccess('');
            }, 1500);
        } catch (err) {
            console.error('Check-in failed:', err);
            setIsSubmitting(false);
        }
    }

    const nextCard = () => {
        if (currentCard < 2) {
            setCurrentCard(currentCard + 1);
        } else {
            submitCheckin();
        }
    };

    const prevCard = () => {
        if (currentCard > 0) {
            setCurrentCard(currentCard - 1);
        }
    };

    const handleDragEnd = (event, info) => {
        if (info.offset.y < -100) {
            nextCard();
        }
    };

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>🧠 Burnout & Wellness Check-in</h1>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
                <button className={`btn ${tab === 'checkin' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('checkin')}>Daily Check-in</button>
                <button className={`btn ${tab === 'status' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('status')}>Wellness Status</button>
            </div>

            {/* Daily Check-in */}
            {tab === 'checkin' && (
                <div style={{ position: 'relative', width: '100%', maxWidth: '480px', margin: '0 auto', height: '480px' }}>
                    {success && <div className="alert alert-success" style={{ marginBottom: '16px', textAlign: 'center' }}>{success}</div>}

                    <AnimatePresence mode="wait">
                        {currentCard === 0 && (
                            <motion.div
                                key="card-sleep"
                                className="card"
                                drag="y"
                                dragConstraints={{ top: 0, bottom: 0 }}
                                dragElastic={{ top: 0.6, bottom: 0.1 }}
                                onDragEnd={handleDragEnd}
                                variants={cardVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    cursor: 'grab',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'space-between',
                                    border: '1px solid rgba(255,255,255,0.6)',
                                    boxShadow: 'var(--shadow-md)',
                                    zIndex: 10
                                }}
                            >
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-light)', fontWeight: 600 }}>STEP 1 OF 3</span>
                                        <span style={{ fontSize: '1.5rem' }}>😴</span>
                                    </div>
                                    <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '8px' }}>Sleep Quality</h2>
                                    <p style={{ color: 'var(--text-light)', fontSize: '0.9rem', marginBottom: '24px' }}>
                                        How many hours of restful sleep did you get last night?
                                    </p>

                                    <div style={{ textAlign: 'center', margin: '24px 0' }}>
                                        <div style={{ fontSize: '3.5rem', fontWeight: 800, color: 'var(--primary)' }}>
                                            {form.sleep_hours} hrs
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <input
                                            type="range"
                                            min="3"
                                            max="12"
                                            step="0.5"
                                            value={form.sleep_hours}
                                            onChange={(e) => setForm({ ...form, sleep_hours: parseFloat(e.target.value) })}
                                            style={{ width: '100%', cursor: 'pointer' }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-light)', marginTop: '6px' }}>
                                            <span>3 hrs</span>
                                            <span>7-8 hrs (Target)</span>
                                            <span>12 hrs</span>
                                        </div>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'center' }}>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>Swipe up or click Next to advance</span>
                                    <button className="btn btn-primary" style={{ width: '100%' }} onClick={nextCard}>
                                        Next step →
                                    </button>
                                </div>
                            </motion.div>
                        )}

                        {currentCard === 1 && (
                            <motion.div
                                key="card-stress"
                                className="card"
                                drag="y"
                                dragConstraints={{ top: 0, bottom: 0 }}
                                dragElastic={{ top: 0.6, bottom: 0.1 }}
                                onDragEnd={handleDragEnd}
                                variants={cardVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    cursor: 'grab',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'space-between',
                                    border: '1px solid rgba(255,255,255,0.6)',
                                    boxShadow: 'var(--shadow-md)',
                                    zIndex: 10
                                }}
                            >
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-light)', fontWeight: 600 }}>STEP 2 OF 3</span>
                                        <span style={{ fontSize: '1.5rem' }}>⚡</span>
                                    </div>
                                    <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '8px' }}>Stress Level</h2>
                                    <p style={{ color: 'var(--text-light)', fontSize: '0.9rem', marginBottom: '24px' }}>
                                        Rate your current academic stress/anxiety level today.
                                    </p>

                                    <div style={{ textAlign: 'center', margin: '24px 0' }}>
                                        <div style={{ fontSize: '3.5rem', fontWeight: 800, color: form.stress_level >= 8 ? 'var(--danger)' : form.stress_level >= 5 ? 'var(--warning)' : 'var(--success)' }}>
                                            {form.stress_level}/10
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <input
                                            type="range"
                                            min="1"
                                            max="10"
                                            step="1"
                                            value={form.stress_level}
                                            onChange={(e) => setForm({ ...form, stress_level: parseInt(e.target.value) })}
                                            style={{ width: '100%', cursor: 'pointer' }}
                                        />
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-light)', marginTop: '6px' }}>
                                            <span>Calm 😊</span>
                                            <span>Moderate 😐</span>
                                            <span>Extreme 😰</span>
                                        </div>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                                    <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
                                        <button className="btn btn-secondary" style={{ flex: 1 }} onClick={prevCard}>
                                            ← Back
                                        </button>
                                        <button className="btn btn-primary" style={{ flex: 2 }} onClick={nextCard}>
                                            Next step →
                                        </button>
                                    </div>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-light)', textAlign: 'center', marginTop: '4px' }}>Swipe up to advance</span>
                                </div>
                            </motion.div>
                        )}

                        {currentCard === 2 && (
                            <motion.div
                                key="card-mood"
                                className="card"
                                drag="y"
                                dragConstraints={{ top: 0, bottom: 0 }}
                                dragElastic={{ top: 0.6, bottom: 0.1 }}
                                onDragEnd={handleDragEnd}
                                variants={cardVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    width: '100%',
                                    height: '100%',
                                    cursor: 'grab',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    justifyContent: 'space-between',
                                    border: '1px solid rgba(255,255,255,0.6)',
                                    boxShadow: 'var(--shadow-md)',
                                    overflowY: 'auto',
                                    zIndex: 10
                                }}
                            >
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                        <span style={{ fontSize: '0.85rem', color: 'var(--text-light)', fontWeight: 600 }}>STEP 3 OF 3</span>
                                        <span style={{ fontSize: '1.5rem' }}>🎭</span>
                                    </div>
                                    <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '8px' }}>Mood & Habits</h2>
                                    <p style={{ color: 'var(--text-light)', fontSize: '0.9rem', marginBottom: '16px' }}>
                                        How are you feeling mentally right now?
                                    </p>

                                    {/* Mood Buttons */}
                                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                                        {[
                                            { m: 'happy', label: '😊 Happy' },
                                            { m: 'neutral', label: '😐 Neutral' },
                                            { m: 'sad', label: '😢 Sad' },
                                            { m: 'anxious', label: '😟 Anxious' },
                                            { m: 'overwhelmed', label: '😫 Stressed' }
                                        ].map(item => (
                                            <button
                                                key={item.m}
                                                type="button"
                                                className={`btn ${form.mood === item.m ? 'btn-primary' : 'btn-secondary'} btn-small`}
                                                onClick={() => setForm({ ...form, mood: item.m })}
                                                style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                                            >
                                                {item.label}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Extra Details */}
                                    <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
                                        <div className="form-group" style={{ flex: 1 }}>
                                            <label htmlFor="study" style={{ fontSize: '0.8rem' }}>Study Hours</label>
                                            <input
                                                id="study"
                                                type="number"
                                                step="0.5"
                                                min="0"
                                                value={form.study_hours}
                                                onChange={(e) => setForm({ ...form, study_hours: e.target.value })}
                                                style={{ padding: '8px', fontSize: '0.85rem' }}
                                            />
                                        </div>
                                        <div className="form-group" style={{ flex: 1 }}>
                                            <label htmlFor="exercise" style={{ fontSize: '0.8rem' }}>Exercise (min)</label>
                                            <input
                                                id="exercise"
                                                type="number"
                                                min="0"
                                                value={form.exercise_minutes}
                                                onChange={(e) => setForm({ ...form, exercise_minutes: e.target.value })}
                                                style={{ padding: '8px', fontSize: '0.85rem' }}
                                            />
                                        </div>
                                    </div>

                                    <div className="form-group" style={{ marginBottom: '16px' }}>
                                        <label htmlFor="notes" style={{ fontSize: '0.8rem' }}>Notes (optional)</label>
                                        <textarea
                                            id="notes"
                                            rows="2"
                                            placeholder="Write down any thoughts..."
                                            value={form.notes}
                                            onChange={(e) => setForm({ ...form, notes: e.target.value })}
                                            style={{ padding: '8px', fontSize: '0.85rem', width: '100%', resize: 'none' }}
                                        />
                                    </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                                    <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
                                        <button className="btn btn-secondary" style={{ flex: 1 }} onClick={prevCard}>
                                            ← Back
                                        </button>
                                        <button className="btn btn-primary" style={{ flex: 2 }} onClick={submitCheckin} disabled={isSubmitting}>
                                            {isSubmitting ? 'Recording...' : 'Submit Check-in ✓'}
                                        </button>
                                    </div>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-light)', textAlign: 'center', marginTop: '4px' }}>Swipe up to submit check-in</span>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
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
