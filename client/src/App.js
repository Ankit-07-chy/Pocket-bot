// ============================================================
// APP - Main router and layout with Firebase Auth
// ============================================================
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { onAuthChange, logout } from './firebase';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import FoodPage from './pages/FoodPage';
import TravelPage from './pages/TravelPage';
import BurnoutPage from './pages/BurnoutPage';
import RoutinePage from './pages/RoutinePage';
import ChatPage from './pages/ChatPage';
import Profile from './pages/Profile';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

    useEffect(() => {
        // Listen to Firebase auth state changes
        const unsubscribe = onAuthChange((firebaseUser) => {
            if (firebaseUser) {
                // User is signed in via Firebase
                setUser({
                    id: firebaseUser.uid,
                    email: firebaseUser.email,
                    name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
                    photoURL: firebaseUser.photoURL,
                    authMethod: 'firebase'
                });
            } else {
                // Check for fallback JWT login
                const savedUser = localStorage.getItem('pocketbuddy_user');
                if (savedUser) {
                    setUser({ ...JSON.parse(savedUser), authMethod: 'jwt' });
                } else {
                    setUser(null);
                }
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    // Called when user logs in via fallback JWT (non-Firebase)
    const handleJWTLogin = (userData, token) => {
        localStorage.setItem('pocketbuddy_token', token);
        localStorage.setItem('pocketbuddy_user', JSON.stringify(userData));
        setUser({ ...userData, authMethod: 'jwt' });
    };

    // Called when Firebase login/register succeeds
    const handleFirebaseLogin = (firebaseUser) => {
        setUser({
            id: firebaseUser.uid,
            email: firebaseUser.email,
            name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
            photoURL: firebaseUser.photoURL,
            authMethod: 'firebase'
        });
    };

    const handleLogout = async () => {
        try {
            await logout(); // Firebase sign out
        } catch (e) {
            // Ignore Firebase errors if not using Firebase
        }
        localStorage.removeItem('pocketbuddy_token');
        localStorage.removeItem('pocketbuddy_user');
        setUser(null);
    };

    // Show loading spinner while checking auth
    if (loading) {
        return (
            <div className="auth-container">
                <div style={{ color: 'white', fontSize: '1.2rem' }}>Loading...</div>
            </div>
        );
    }

    // Show auth pages if not logged in
    if (!user) {
        return (
            <BrowserRouter>
                <div className="bg-blobs">
                    <div className="blob blob-1"></div>
                    <div className="blob blob-2"></div>
                    <div className="blob blob-3"></div>
                </div>
                <Routes>
                    <Route path="/register" element={
                        <Register onJWTLogin={handleJWTLogin} onFirebaseLogin={handleFirebaseLogin} />
                    } />
                    <Route path="*" element={
                        <Login onJWTLogin={handleJWTLogin} onFirebaseLogin={handleFirebaseLogin} />
                    } />
                </Routes>
            </BrowserRouter>
        );
    }

    // Main app with sidebar navigation
    return (
        <BrowserRouter>
            <div className="bg-blobs">
                <div className="blob blob-1"></div>
                <div className="blob blob-2"></div>
                <div className="blob blob-3"></div>
            </div>
            <div className="app-container">
                {/* Mobile Header */}
                <header className="mobile-header">
                    <button className="menu-toggle" onClick={() => setIsMobileMenuOpen(true)} aria-label="Open sidebar">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                    </button>
                    <div className="mobile-logo">🎒 PocketBuddy</div>
                    <div className="mobile-user-avatar">
                        {user?.photoURL ? (
                            <img src={user.photoURL} alt={user.name} />
                        ) : (
                            user?.name?.charAt(0).toUpperCase()
                        )}
                    </div>
                </header>

                {/* Sidebar Navigation */}
                <aside className={`sidebar ${isMobileMenuOpen ? 'open' : ''}`}>
                    <div className="sidebar-header">
                        <div className="header-top">
                            <h1>🎒 PocketBuddy</h1>
                            <button className="sidebar-close" onClick={() => setIsMobileMenuOpen(false)} aria-label="Close sidebar">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                            </button>
                        </div>
                        <p>Hey, {user?.name?.split(' ')[0]}!</p>
                    </div>
                    <nav onClick={() => setIsMobileMenuOpen(false)}>
                        <NavLink to="/" end>📊 <span>Dashboard</span></NavLink>
                        <NavLink to="/expenses">💰 <span>Expenses</span></NavLink>
                        <NavLink to="/food">🍕 <span>Food</span></NavLink>
                        <NavLink to="/travel">🚌 <span>Travel</span></NavLink>
                        <NavLink to="/burnout">🧠 <span>Burnout</span></NavLink>
                        <NavLink to="/routine">🏃 <span>Routine</span></NavLink>
                        <NavLink to="/chat">💬 <span>AI Chat</span></NavLink>
                        <NavLink to="/profile">⚙️ <span>Profile</span></NavLink>
                        <a href="#logout" onClick={(e) => { e.preventDefault(); setShowLogoutConfirm(true); }}>
                            🚪 <span>Logout</span>
                        </a>
                    </nav>
                </aside>

                {/* Mobile Sidebar Overlay */}
                {isMobileMenuOpen && (
                    <div className="sidebar-overlay" onClick={() => setIsMobileMenuOpen(false)}></div>
                )}

                {/* Main Content Area */}
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/expenses" element={<Expenses />} />
                        <Route path="/food" element={<FoodPage />} />
                        <Route path="/travel" element={<TravelPage />} />
                        <Route path="/burnout" element={<BurnoutPage />} />
                        <Route path="/routine" element={<RoutinePage />} />
                        <Route path="/chat" element={<ChatPage />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </main>
            {/* Logout Confirmation Modal Overlay */}
            {showLogoutConfirm && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    background: 'rgba(15, 23, 42, 0.45)',
                    backdropFilter: 'blur(8px)',
                    WebkitBackdropFilter: 'blur(8px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 2000
                }}>
                    <div className="card" style={{
                        maxWidth: '360px',
                        width: '90%',
                        padding: '32px 24px 24px',
                        textAlign: 'center',
                        border: '1px solid rgba(255, 255, 255, 0.6)',
                        boxShadow: 'var(--shadow-md)',
                        margin: 0
                    }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🚪</div>
                        <h2 style={{ marginBottom: '8px', fontSize: '1.3rem', fontWeight: 800 }}>Confirm Logout</h2>
                        <p style={{ color: 'var(--text-light)', marginBottom: '24px', fontSize: '0.9rem', lineHeight: '1.5' }}>
                            Are you sure you want to log out of PocketBuddy?
                        </p>
                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                            <button className="btn btn-secondary btn-small" onClick={() => setShowLogoutConfirm(false)}>
                                Cancel
                            </button>
                            <button className="btn btn-danger btn-small" onClick={() => {
                                handleLogout();
                                setShowLogoutConfirm(false);
                            }}>
                                Log Out
                            </button>
                        </div>
                    </div>
                </div>
            )}
            </div>
        </BrowserRouter>
    );
}

export default App;
