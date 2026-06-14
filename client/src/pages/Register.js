import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { auth } from '../api';
import { registerWithEmail, loginWithGoogle, getIdToken } from '../firebase';

function Register({ onJWTLogin, onFirebaseLogin }) {
    const [form, setForm] = useState({
        name: '', email: '', password: '', major: '', year: 1, monthly_income: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    // Firebase Email/Password Registration
    const handleFirebaseRegister = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Create user in Firebase
            const firebaseUser = await registerWithEmail(form.email, form.password, form.name);

            // Sync with our backend database (creates the user record)
            const idToken = await getIdToken();
            await auth.firebaseSync({
                idToken,
                name: form.name,
                email: firebaseUser.email,
                uid: firebaseUser.uid,
                major: form.major,
                year: parseInt(form.year),
                monthly_income: parseFloat(form.monthly_income) || 0
            });

            onFirebaseLogin(firebaseUser);
        } catch (err) {
            // If Firebase fails (e.g., not configured), fall back to JWT register
            if (err.code === 'auth/configuration-not-found' || err.message?.includes('Firebase')) {
                try {
                    const data = await auth.register({
                        ...form,
                        year: parseInt(form.year),
                        monthly_income: parseFloat(form.monthly_income) || 0
                    });
                    onJWTLogin(data.user, data.token);
                    return;
                } catch (jwtErr) {
                    setError(jwtErr.message);
                }
            } else {
                setError(err.message || 'Registration failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Google Sign-Up
    const handleGoogleRegister = async () => {
        setError('');
        setLoading(true);

        try {
            const firebaseUser = await loginWithGoogle();

            // Sync with our backend
            const idToken = await getIdToken();
            await auth.firebaseSync({
                idToken,
                name: firebaseUser.displayName,
                email: firebaseUser.email,
                uid: firebaseUser.uid,
                major: form.major,
                year: parseInt(form.year) || 1,
                monthly_income: parseFloat(form.monthly_income) || 0
            });

            onFirebaseLogin(firebaseUser);
        } catch (err) {
            if (err.code !== 'auth/popup-closed-by-user') {
                setError(err.message || 'Google sign-up failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1>🎒 PocketBuddy</h1>
                <p>Create your account</p>

                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleFirebaseRegister}>
                    <div className="form-group">
                        <label htmlFor="name">Full Name</label>
                        <input
                            id="name"
                            name="name"
                            type="text"
                            value={form.name}
                            onChange={handleChange}
                            placeholder="Your name"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-email">Email</label>
                        <input
                            id="reg-email"
                            name="email"
                            type="email"
                            value={form.email}
                            onChange={handleChange}
                            placeholder="your@email.com"
                            required
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="reg-password">Password</label>
                        <input
                            id="reg-password"
                            name="password"
                            type="password"
                            value={form.password}
                            onChange={handleChange}
                            placeholder="Min 6 characters"
                            required
                            minLength={6}
                            autoComplete="new-password"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="major">Major</label>
                            <input
                                id="major"
                                name="major"
                                type="text"
                                value={form.major}
                                onChange={handleChange}
                                placeholder="e.g. Computer Science"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="year">Year</label>
                            <select
                                id="year"
                                name="year"
                                value={form.year}
                                onChange={handleChange}
                            >
                                <option value={1}>1st Year</option>
                                <option value={2}>2nd Year</option>
                                <option value={3}>3rd Year</option>
                                <option value={4}>4th Year</option>
                                <option value={5}>Graduate</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="income">Monthly Budget/Income (₹)</label>
                        <input
                            id="income"
                            name="monthly_income"
                            type="number"
                            value={form.monthly_income}
                            onChange={handleChange}
                            placeholder="e.g. 15000"
                            min="0"
                            step="50"
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading}
                    >
                        {loading ? "Creating account..." : "Create Account"}
                    </button>
                </form>
                {/* Divider */}
                <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', gap: '10px' }}>
                    <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
                    <span style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>or</span>
                    <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
                </div>

                {/* Google Sign-Up */}
                <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
                    onClick={handleGoogleRegister}
                    disabled={loading}
                >
                    <svg width="18" height="18" viewBox="0 0 48 48">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
                    </svg>
                    Sign up with Google
                </button>

                <div className="auth-switch">
                    Already have an account? <Link to="/login">Login</Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
