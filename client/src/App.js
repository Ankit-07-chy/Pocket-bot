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
            <div className="app-container">
                {/* Sidebar Navigation */}
                <aside className="sidebar">
                    <div className="sidebar-header">
                        <h1>🎒 PocketBuddy</h1>
                        <p>Hey, {user?.name?.split(' ')[0]}!</p>
                    </div>
                    <nav>
                        <NavLink to="/" end>📊 <span>Dashboard</span></NavLink>
                        <NavLink to="/expenses">💰 <span>Expenses</span></NavLink>
                        <NavLink to="/food">🍕 <span>Food</span></NavLink>
                        <NavLink to="/travel">🚌 <span>Travel</span></NavLink>
                        <NavLink to="/burnout">🧠 <span>Burnout</span></NavLink>
                        <NavLink to="/routine">🏃 <span>Routine</span></NavLink>
                        <NavLink to="/chat">💬 <span>AI Chat</span></NavLink>
                        <NavLink to="/profile">⚙️ <span>Profile</span></NavLink>
                        <a href="#logout" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                            🚪 <span>Logout</span>
                        </a>
                    </nav>
                </aside>

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
            </div>
        </BrowserRouter>
    );
}

export default App;
