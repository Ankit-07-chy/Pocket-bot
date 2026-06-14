import React, { useState, useEffect } from 'react';
import { auth, support } from '../api';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [form, setForm] = useState({});
    const [emergency, setEmergency] = useState(null);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    useEffect(() => { loadProfile(); }, []);

    async function loadProfile() {
        try {
            const data = await auth.getProfile();
            setProfile(data);
            setForm({
                name: data.name || '',
                major: data.major || '',
                year: data.year || 1,
                monthly_income: data.monthly_income || '',
                daily_budget: data.daily_budget || '',
                dietary_preferences: data.dietary_preferences || '[]',
                emergency_contact: data.emergency_contact || ''
            });
        } catch (err) {
            console.error(err);
        }
    }

    async function handleSave(e) {
        e.preventDefault();
        setSuccess('');
        setError('');
        try {
            await auth.updateProfile({
                ...form,
                year: parseInt(form.year),
                monthly_income: parseFloat(form.monthly_income) || 0,
                daily_budget: parseFloat(form.daily_budget) || 0
            });
            setSuccess('Profile updated!');
        } catch (err) {
            setError(err.message);
        }
    }

    async function showEmergencyResources() {
        try {
            const data = await support.emergency();
            setEmergency(data);
        } catch (err) {
            console.error(err);
        }
    }

    if (!profile) return <div className="loading">Loading profile...</div>;

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>⚙️ Profile Settings</h1>

            <div className="card">
                <div className="card-header"><h2>Your Information</h2></div>

                {success && <div className="alert alert-success">{success}</div>}
                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleSave}>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="prof-name">Name</label>
                            <input id="prof-name" type="text" value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="prof-email">Email</label>
                            <input id="prof-email" type="email" value={profile.email} disabled style={{ opacity: 0.6 }} />
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="prof-major">Major</label>
                            <input id="prof-major" type="text" value={form.major}
                                onChange={(e) => setForm({ ...form, major: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="prof-year">Year</label>
                            <select id="prof-year" value={form.year}
                                onChange={(e) => setForm({ ...form, year: e.target.value })}>
                                <option value={1}>1st Year</option>
                                <option value={2}>2nd Year</option>
                                <option value={3}>3rd Year</option>
                                <option value={4}>4th Year</option>
                                <option value={5}>Graduate</option>
                            </select>
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="prof-income">Monthly Income/Budget (₹)</label>
                            <input id="prof-income" type="number" min="0" step="50" value={form.monthly_income}
                                onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="prof-daily">Daily Budget (₹)</label>
                            <input id="prof-daily" type="number" min="0" step="1" value={form.daily_budget}
                                onChange={(e) => setForm({ ...form, daily_budget: e.target.value })} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label htmlFor="prof-diet">Dietary Preferences (comma separated)</label>
                        <input id="prof-diet" type="text" value={form.dietary_preferences === '[]' ? '' : form.dietary_preferences}
                            onChange={(e) => setForm({ ...form, dietary_preferences: e.target.value })}
                            placeholder="e.g. vegetarian, no dairy" />
                    </div>
                    <div className="form-group">
                        <label htmlFor="prof-emergency">Emergency Contact</label>
                        <input id="prof-emergency" type="text" value={form.emergency_contact}
                            onChange={(e) => setForm({ ...form, emergency_contact: e.target.value })}
                            placeholder="Name - Phone Number" />
                    </div>
                    <button type="submit" className="btn btn-primary">Save Changes</button>
                </form>
            </div>

            {/* Account Info */}
            <div className="card">
                <div className="card-header"><h2>Account</h2></div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-light)' }}>
                    Member since: {new Date(profile.created_at).toLocaleDateString()}
                </p>
            </div>

            {/* Emergency Resources */}
            <div className="card">
                <div className="card-header">
                    <h2>🆘 Crisis Resources</h2>
                    <button className="btn btn-secondary btn-small" onClick={showEmergencyResources}>
                        Show Resources
                    </button>
                </div>
                {emergency && (
                    <div>
                        <p style={{ marginBottom: '12px', fontWeight: '500' }}>{emergency.message}</p>
                        {emergency.resources.map((r, i) => (
                            <div key={i} className="meal-card">
                                <strong>{r.name}</strong>
                                <p style={{ fontSize: '0.85rem' }}>{r.phone}</p>
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>{r.description}</p>
                            </div>
                        ))}
                        <p style={{ marginTop: '12px', fontStyle: 'italic', fontSize: '0.9rem' }}>{emergency.reminder}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Profile;
