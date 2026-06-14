import React, { useState, useEffect } from 'react';
import { travel } from '../api';

function TravelPage() {
    const [form, setForm] = useState({ origin: '', destination: '', mode: 'bus', cost: '', duration_minutes: '' });
    const [savings, setSavings] = useState(null);
    const [patterns, setPatterns] = useState(null);
    const [success, setSuccess] = useState('');
    const [tab, setTab] = useState('log');

    useEffect(() => { loadData(); }, []);

    async function loadData() {
        try {
            const [savingsData, patternsData] = await Promise.all([
                travel.savings().catch(() => null),
                travel.patterns().catch(() => null)
            ]);
            setSavings(savingsData);
            setPatterns(patternsData);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setSuccess('');
        try {
            await travel.log({
                ...form,
                cost: parseFloat(form.cost) || 0,
                duration_minutes: parseInt(form.duration_minutes) || 0
            });
            setSuccess('Trip logged!');
            setForm({ ...form, origin: '', destination: '', cost: '', duration_minutes: '' });
            loadData();
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>🚌 Travel Options</h1>

            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button className={`btn ${tab === 'log' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('log')}>Log Trip</button>
                <button className={`btn ${tab === 'savings' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('savings')}>Savings</button>
                <button className={`btn ${tab === 'patterns' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('patterns')}>Patterns</button>
            </div>

            {/* Log Trip */}
            {tab === 'log' && (
                <div className="card">
                    <div className="card-header"><h2>Log a Trip</h2></div>
                    {success && <div className="alert alert-success">{success}</div>}
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="origin">From</label>
                                <input id="origin" type="text" value={form.origin}
                                    onChange={(e) => setForm({ ...form, origin: e.target.value })}
                                    placeholder="e.g. Dorm" required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="destination">To</label>
                                <input id="destination" type="text" value={form.destination}
                                    onChange={(e) => setForm({ ...form, destination: e.target.value })}
                                    placeholder="e.g. Campus Library" required />
                            </div>
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="travel-mode">Mode</label>
                                <select id="travel-mode" value={form.mode}
                                    onChange={(e) => setForm({ ...form, mode: e.target.value })}>
                                    <option value="bus">🚌 Bus</option>
                                    <option value="subway">🚇 Subway</option>
                                    <option value="uber">🚗 Uber/Lyft</option>
                                    <option value="taxi">🚕 Taxi</option>
                                    <option value="bike">🚲 Bike</option>
                                    <option value="walk">🚶 Walk</option>
                                    <option value="carpool">🤝 Carpool</option>
                                    <option value="drive">🚙 Drive</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label htmlFor="travel-cost">Cost (₹)</label>
                                <input id="travel-cost" type="number" step="0.01" min="0" value={form.cost}
                                    onChange={(e) => setForm({ ...form, cost: e.target.value })}
                                    placeholder="15" />
                            </div>
                        </div>
                        <div className="form-group">
                            <label htmlFor="duration">Duration (minutes)</label>
                            <input id="duration" type="number" min="0" value={form.duration_minutes}
                                onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
                                placeholder="15" />
                        </div>
                        <button type="submit" className="btn btn-primary">Log Trip</button>
                    </form>
                </div>
            )}

            {/* Savings Tab */}
            {tab === 'savings' && (
                <div>
                    {savings && (
                        <>
                            <div className="stats-grid">
                                <div className="stat-card">
                                    <div className="stat-value">₹{savings.monthly_travel_spend.toFixed(2)}</div>
                                    <div className="stat-label">Monthly travel spend</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value">{savings.total_trips}</div>
                                    <div className="stat-label">Trips this month</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-value" style={{ color: 'var(--success)' }}>
                                        ₹{savings.potential_monthly_savings.toFixed(2)}
                                    </div>
                                    <div className="stat-label">Potential savings</div>
                                </div>
                            </div>

                            {savings.pass_recommendation && (
                                <div className="alert alert-info">💡 {savings.pass_recommendation.message}</div>
                            )}

                            {savings.suggestions.length > 0 && (
                                <div className="card">
                                    <div className="card-header"><h2>Savings Suggestions</h2></div>
                                    <table>
                                        <thead><tr><th>Switch from</th><th>To</th><th>Monthly Save</th></tr></thead>
                                        <tbody>
                                            {savings.suggestions.map((s, i) => (
                                                <tr key={i}>
                                                    <td style={{ textTransform: 'capitalize' }}>{s.current}</td>
                                                    <td style={{ textTransform: 'capitalize' }}>{s.suggested}</td>
                                                    <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>₹{s.monthly_savings.toFixed(2)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </>
                    )}
                    {!savings && <div className="empty-state"><p>Log trips to see savings potential!</p></div>}
                </div>
            )}

            {/* Patterns Tab */}
            {tab === 'patterns' && (
                <div>
                    {patterns && (
                        <>
                            {patterns.insight && <div className="alert alert-info">{patterns.insight}</div>}

                            {patterns.top_destinations?.length > 0 && (
                                <div className="card">
                                    <div className="card-header"><h2>Top Destinations</h2></div>
                                    <table>
                                        <thead><tr><th>Destination</th><th>Visits</th><th>Avg Cost</th></tr></thead>
                                        <tbody>
                                            {patterns.top_destinations.map((d, i) => (
                                                <tr key={i}>
                                                    <td>{d.destination}</td>
                                                    <td>{d.visits}</td>
                                                    <td>₹{d.avg_cost?.toFixed(2)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {patterns.regular_routes?.length > 0 && (
                                <div className="card">
                                    <div className="card-header"><h2>Regular Routes</h2></div>
                                    <table>
                                        <thead><tr><th>Route</th><th>Mode</th><th>Frequency</th><th>Total Cost</th></tr></thead>
                                        <tbody>
                                            {patterns.regular_routes.map((r, i) => (
                                                <tr key={i}>
                                                    <td>{r.origin} → {r.destination}</td>
                                                    <td style={{ textTransform: 'capitalize' }}>{r.mode}</td>
                                                    <td>{r.frequency}x/month</td>
                                                    <td>₹{r.total_cost?.toFixed(2)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </>
                    )}
                    {!patterns && <div className="empty-state"><p>Log more trips to discover patterns!</p></div>}
                </div>
            )}
        </div>
    );
}

export default TravelPage;
