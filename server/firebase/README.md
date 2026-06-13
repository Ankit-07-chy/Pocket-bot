# Firebase Setup Instructions

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Name it `pocketbuddy` (or any name)
4. Disable Google Analytics (optional, not needed)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to **Build → Authentication**
2. Click "Get started"
3. Enable **Email/Password** sign-in method
4. Enable **Google** sign-in method (enter your project's support email)
5. Click Save

## Step 3: Get Web App Config (for client)

1. Go to **Project Settings** (gear icon) → **General**
2. Scroll down to "Your apps" → Click **Add app** → Web (</> icon)
3. Register app name: `pocketbuddy-web`
4. Copy the `firebaseConfig` object
5. Paste it into `client/src/firebase.js` replacing the placeholder values:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

## Step 4: Get Service Account Key (for server)

1. Go to **Project Settings** → **Service Accounts**
2. Click "Generate new private key"
3. Save the downloaded JSON file as:
   ```
   server/firebase/serviceAccountKey.json
   ```
4. ⚠️ NEVER commit this file to git (it's in .gitignore)

## Alternative: Use Environment Variables

Instead of the JSON file, you can set these in your `.env`:

```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

## Step 5: Test

1. Start the server: `npm start`
2. Start the client: `cd client && npm start`
3. Try registering a new account
4. Try Google sign-in

## How Auth Works

```
Client (React)                    Server (Express)
     |                                  |
     |-- Firebase login/register -----> |
     |                                  |
     |-- Get Firebase ID Token -------> |
     |                                  |
     |-- POST /api/auth/firebase-sync ->| (creates user in SQLite DB)
     |                                  |
     |-- API calls with Bearer token -->| (verifies with Firebase Admin)
     |                                  | (resolves to DB user id)
     |                                  |
```

If Firebase is not configured, the app falls back to JWT-based auth
(email/password stored in SQLite with bcrypt hashing).
