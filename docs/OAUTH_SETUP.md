# OAuth Setup Guide

This guide explains how to set up Google and GitHub OAuth authentication for the Medication Tracker application.

## Table of Contents

- [Overview](#overview)
- [Google OAuth Setup](#google-oauth-setup)
- [GitHub OAuth Setup](#github-oauth-setup)
- [Environment Configuration](#environment-configuration)
- [Testing OAuth](#testing-oauth)
- [Troubleshooting](#troubleshooting)

## Overview

The Medication Tracker supports three authentication methods:

1. **Traditional email/password** (username + password)
2. **Google OAuth** (Sign in with Google)
3. **GitHub OAuth** (Sign in with GitHub)

OAuth provides a more secure authentication method and allows users to sign in without creating a new password.

### How OAuth Works

1. User clicks "Sign in with Google" or "Sign in with GitHub"
2. User is redirected to the OAuth provider (Google/GitHub)
3. User grants permission to the application
4. Provider redirects back to our callback URL with an authorization code
5. Application exchanges the code for an access token
6. Application retrieves user info and creates/links the account
7. Application issues a JWT token for API access

## Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Medication Tracker")
4. Click "Create"

### Step 2: Enable Google+ API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API" or "Google Identity"
3. Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (unless you have a Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: Medication Tracker
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Add these scopes:
   - `openid`
   - `email`
   - `profile`
8. Click "Save and Continue"
9. On "Test users" page, add your email for testing
10. Click "Save and Continue"

### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Enter name: "Medication Tracker Web Client"
5. Under "Authorized redirect URIs", add:
   - `http://localhost:8000/api/auth/google/callback` (for local development)
   - `https://yourdomain.com/api/auth/google/callback` (for production)
6. Click "Create"
7. **Save the Client ID and Client Secret** - you'll need these for environment variables

### Step 5: Add Environment Variables

Add to your `.env` file:

```env
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

## GitHub OAuth Setup

### Step 1: Create a GitHub OAuth App

1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in the application details:
   - **Application name**: Medication Tracker
   - **Homepage URL**: `http://localhost:8000` (or your domain)
   - **Authorization callback URL**: `http://localhost:8000/api/auth/github/callback`
4. Click "Register application"

### Step 2: Get Client Credentials

1. After creating the app, you'll see your **Client ID**
2. Click "Generate a new client secret"
3. **Save the Client ID and Client Secret** - you'll need these for environment variables

### Step 3: Add Environment Variables

Add to your `.env` file:

```env
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:8000/api/auth/github/callback
```

## Environment Configuration

Your complete `.env` file should include:

```env
# Database
DATABASE_URL=postgresql://medtrack_user:medtrack_dev_pass_2024@postgres:5432/medtrack

# Security
SECRET_KEY=your_secret_key_for_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
DEBUG=True

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/auth/github/callback
```

**Note**: OAuth providers are optional. If credentials are not provided, those OAuth endpoints will return a 501 Not Implemented error.

## Testing OAuth

### Test Google OAuth

1. Start your application:

   ```bash
   docker-compose up -d
   ```

2. Navigate to:

   ```
   http://localhost:8000/api/auth/google/login
   ```

3. You should be redirected to Google's login page
4. Sign in with your Google account
5. Grant permissions to the application
6. You'll be redirected back with an access token

### Test GitHub OAuth

1. Navigate to:

   ```
   http://localhost:8000/api/auth/github/login
   ```

2. You should be redirected to GitHub's authorization page
3. Click "Authorize"
4. You'll be redirected back with an access token

### Using the Access Token

Once you receive the access token from the callback, use it to make authenticated requests:

```bash
# Example: Get current user info
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/auth/me
```

## Production Deployment

### Update Redirect URIs

When deploying to production:

1. **Google Cloud Console**:
   - Go to your OAuth credentials
   - Add production redirect URI: `https://yourdomain.com/api/auth/google/callback`

2. **GitHub OAuth App**:
   - Go to your OAuth app settings
   - Update callback URL: `https://yourdomain.com/api/auth/github/callback`

3. **Update `.env`**:

   ```env
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback
   GITHUB_REDIRECT_URI=https://yourdomain.com/api/auth/github/callback
   ```

### Security Considerations

1. **Never commit `.env` file** to version control
2. **Use HTTPS** in production for all OAuth callbacks
3. **Rotate client secrets** periodically
4. **Monitor OAuth usage** through provider dashboards
5. **Limit OAuth scopes** to only what's necessary

## Troubleshooting

### Google OAuth Issues

**Error: "redirect_uri_mismatch"**

- Ensure the redirect URI in your `.env` matches exactly with Google Cloud Console
- Check for trailing slashes - they must match exactly
- Verify you're using the correct protocol (http vs https)

**Error: "Access blocked: This app's request is invalid"**

- Make sure you've enabled the Google+ API or Google Identity
- Verify your OAuth consent screen is configured
- Add yourself as a test user if the app is in testing mode

**Error: "Failed to get user information"**

- Check that you've requested the correct scopes (openid, email, profile)
- Verify the Google+ API is enabled

### GitHub OAuth Issues

**Error: "No verified email found"**

- Ensure your GitHub account has at least one verified email
- Go to GitHub Settings → Emails
- Click "Verify" on your primary email if not verified

**Error: "The redirect_uri MUST match the registered callback URL"**

- Check that the callback URL in GitHub app settings matches your `.env`
- Verify protocol (http vs https)
- Check for typos in the URL

### General OAuth Issues

**Error: 501 Not Implemented**

- OAuth provider is not configured
- Check that CLIENT_ID and CLIENT_SECRET are set in `.env`
- Restart the application after adding environment variables

**Error: "OAuth authentication failed"**

- Check application logs for detailed error message
- Verify network connectivity to OAuth providers
- Ensure OAuth app credentials are correct

### Debugging

Enable detailed logging:

```python
# In app/main.py or app/config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check container logs:

```bash
docker-compose logs -f backend
```

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [FastAPI OAuth Tutorial](https://fastapi.tiangolo.com/advanced/security/oauth2/)

## Support

For issues or questions:

- Check the [API Documentation](./API.md)
- Review the [Development Guide](./DEVELOPMENT.md)
- Check application logs for error details
