import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { auth } from '../api';
import { loginWithEmail, loginWithGoogle, getIdToken } from '../firebase';

function Login({ onJWTLogin, onFirebaseLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Firebase Email/Password Login
    const handleFirebaseLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const firebaseUser = await loginWithEmail(email, password);

            // Sync with our backend database
            const idToken = await getIdToken();
            await auth.firebaseSync({
                idToken,
                name: firebaseUser.displayName,
                email: firebaseUser.email,
                uid: firebaseUser.uid
            });

            onFirebaseLogin(firebaseUser);
        } catch (err) {
            // If Firebase fails, try fallback JWT login
            try {
                const data = await auth.login({ email, password });
                onJWTLogin(data.user, data.token);
            } catch (jwtErr) {
                setError(err.message || 'Login failed. Check your credentials.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Google Sign-In
    const handleGoogleLogin = async () => {
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
                uid: firebaseUser.uid
            });

            onFirebaseLogin(firebaseUser);
        } catch (err) {
            if (err.code === 'auth/popup-closed-by-user') {
                // User closed the popup - not an error
            } else {
                setError(err.message || 'Google sign-in failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h1>🎒 PocketBuddy</h1>
                <p>Your student wellness companion</p>

                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleFirebaseLogin}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="your@email.com"
                            required
                            autoComplete="email"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Your password"
                            required
                            autoComplete="current-password"
                        />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                {/* Divider */}
                <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', gap: '10px' }}>
                    <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
                    <span style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>or</span>
                    <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
                </div>

                {/* Google Sign-In Button */}
                <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
                    onClick={handleGoogleLogin}
                    disabled={loading}
                >
                    <svg width="18" height="18" viewBox="0 0 48 48">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
                    </svg>
                    Continue with Google
                </button>

                <div className="auth-switch">
                    Don't have an account? <Link to="/register">Sign up</Link>
                </div>
            </div>
        </div>
    );
}

export default Login;
