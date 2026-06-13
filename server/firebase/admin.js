// ============================================================
// FIREBASE - MVP mode (no service account key needed)
// Auth is handled client-side by Firebase SDK
// Server trusts decoded Firebase JWT tokens directly
// ============================================================

// No Firebase Admin SDK needed for MVP
// Client handles auth, server just reads the token payload

module.exports = { admin: null, firebaseApp: null };
