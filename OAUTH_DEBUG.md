# OAuth Debugging Guide

## How to Debug OAuth Login Issue

### Step 1: Open Browser Console
1. Open http://localhost:5173/login in your browser
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Go to the "Console" tab

### Step 2: Attempt OAuth Login
1. Click "Continue with Google"
2. Authorize with your Google account
3. Watch the console for debug messages

### Expected Console Output

When the OAuth callback loads, you should see:
```
OAuth callback - Full URL: http://localhost:5173/auth/callback#access_token=...
OAuth callback - Hash: #access_token=...&token_type=bearer
OAuth callback - Search: (empty or query params)
Parsing hash: access_token=...&token_type=bearer
Token from hash: eyJhbGciOiJIUzI1NiI...
✅ Token received, storing in localStorage
✅ Redirecting to dashboard
```

### Common Issues and Solutions

#### Issue 1: "No access token found in URL"
**Symptoms:**
```
❌ No access token found in URL
Hash: (empty)
Search: (empty)
```

**Solution:** Check backend logs to see if redirect URL is correct:
```bash
docker-compose logs backend | grep "OAuth"
```

You should see:
```
[OAuth] Redirecting to: http://localhost:5173/auth/callback#access_token=...
[OAuth] User: your-email@gmail.com (ID: xxx-xxx-xxx)
```

#### Issue 2: Token present but redirect to login happens
**Symptoms:**
- Console shows token was received
- Page redirects back to login immediately

**Cause:** Dashboard component redirects to /login before token is set

**Solution:** The callback now uses `navigate('/', { replace: true })` which should fix this

#### Issue 3: Error message appears
**Check console for:**
- "OAuth error:" - Backend returned an error
- "Authentication failed:" - Exception occurred

### Manual Testing Steps

1. **Clear localStorage:**
   ```javascript
   // In browser console:
   localStorage.clear()
   ```

2. **Try login again**

3. **Check if token is stored:**
   ```javascript
   // In browser console:
   localStorage.getItem('access_token')
   ```
   Should return a JWT token starting with `eyJ...`

4. **Test the token:**
   ```javascript
   // In browser console:
   fetch('http://localhost:8000/api/auth/me', {
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('access_token')}`
     }
   }).then(r => r.json()).then(console.log)
   ```
   Should return your user information

### Backend Logs

Check what the backend is doing:
```bash
# Watch backend logs in real-time
docker-compose logs -f backend

# Or check recent OAuth-related logs
docker-compose logs backend | grep -A 5 "google/callback"
```

### Quick Fix Test

Try this in the browser console when on the callback page:
```javascript
// Manually extract and set token
const hash = window.location.hash.substring(1);
const params = new URLSearchParams(hash);
const token = params.get('access_token');
console.log('Token:', token);
if (token) {
  localStorage.setItem('access_token', token);
  console.log('Token saved!');
  window.location.href = '/';
} else {
  console.log('No token found');
}
```

### Verification

After successful OAuth login, verify:

1. **Token in localStorage:**
   ```javascript
   localStorage.getItem('access_token')
   ```

2. **User can access dashboard:**
   - Navigate to http://localhost:5173/
   - Should see welcome message with your name

3. **API calls work:**
   - Dashboard should load user info
   - No redirect to login

## Still Having Issues?

Run this comprehensive diagnostic:

```javascript
// Paste in browser console
console.log('=== OAuth Diagnostic ===');
console.log('Full URL:', window.location.href);
console.log('Hash:', window.location.hash);
console.log('Search:', window.location.search);
console.log('Token in localStorage:', localStorage.getItem('access_token'));
console.log('Token length:', localStorage.getItem('access_token')?.length);

// Try to parse token
const token = localStorage.getItem('access_token');
if (token) {
  try {
    const parts = token.split('.');
    const payload = JSON.parse(atob(parts[1]));
    console.log('Token payload:', payload);
    console.log('Token expires:', new Date(payload.exp * 1000));
  } catch (e) {
    console.error('Invalid token format:', e);
  }
}
```

Share the output of this diagnostic for further troubleshooting.
