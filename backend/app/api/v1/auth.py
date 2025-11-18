from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils.oauth import get_oauth_client
from app.api.deps import get_current_user
from app.config import settings
import httpx

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get access token.

    Note: OAuth2PasswordRequestForm uses 'username' field but we accept email.

    Args:
        form_data: Login form data (username field contains email)
        db: Database session

    Returns:
        Token: JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email (form_data.username contains email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is OAuth user (no password)
    if user.oauth_provider and not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This account uses {user.oauth_provider} login. Please use the OAuth login button.",
        )

    # Verify password for regular users
    if not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        UserResponse: Current user data
    """
    return current_user


# Google OAuth endpoints
@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.

    Redirects user to Google's authorization page.
    """
    try:
        google = get_oauth_client('google')
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        return await google.authorize_redirect(request, redirect_uri)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.

    Processes the OAuth callback, creates or retrieves user, and redirects to frontend with token.
    """
    try:
        google = get_oauth_client('google')
        token = await google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            # Redirect to frontend with error
            return RedirectResponse(url=f"{settings.CORS_ORIGINS[0]}/auth/callback?error=Failed to get user information")

        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('given_name', 'User')
        oauth_id = user_info.get('sub')

        if not email or not oauth_id:
            return RedirectResponse(url=f"{settings.CORS_ORIGINS[0]}/auth/callback?error=Email and user ID required")

        # Check if user exists by OAuth ID or email
        user = db.query(User).filter(
            or_(
                User.oauth_id == oauth_id,
                User.email == email
            )
        ).first()

        if user:
            # Update OAuth info if user exists but doesn't have it
            if not user.oauth_provider or not user.oauth_id:
                user.oauth_provider = 'google'
                user.oauth_id = oauth_id
                db.commit()
                db.refresh(user)
        else:
            # Create new user
            # Generate unique username from email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                username=username,
                email=email,
                oauth_provider='google',
                oauth_id=oauth_id,
                password_hash=None  # OAuth users don't have passwords
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # Return HTML page that redirects with JavaScript to preserve hash fragment
        frontend_url = settings.CORS_ORIGINS[0]

        # Log for debugging
        print(f"[OAuth] Sending token for user: {user.email} (ID: {user.id})")
        print(f"[OAuth] Frontend URL: {frontend_url}")

        # Return HTML with JavaScript redirect to preserve hash fragment
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting...</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Authentication Successful!</h2>
                <p>Redirecting to your dashboard...</p>
            </div>
            <script>
                console.log('[OAuth Backend] Redirecting with token in hash');
                console.log('[OAuth Backend] Target URL: {frontend_url}/auth/callback#access_token=...');

                // Immediate redirect to frontend with token in hash fragment
                window.location.replace('{frontend_url}/auth/callback#access_token={access_token}&token_type=bearer');
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except ValueError as e:
        return RedirectResponse(url=f"{settings.CORS_ORIGINS[0]}/auth/callback?error=OAuth not configured")
    except Exception as e:
        return RedirectResponse(url=f"{settings.CORS_ORIGINS[0]}/auth/callback?error=Authentication failed")


# GitHub OAuth endpoints
@router.get("/github/login")
async def github_login(request: Request):
    """
    Initiate GitHub OAuth login flow.

    Redirects user to GitHub's authorization page.
    """
    try:
        github = get_oauth_client('github')
        redirect_uri = settings.GITHUB_REDIRECT_URI
        return await github.authorize_redirect(request, redirect_uri)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )


@router.get("/github/callback", response_model=Token)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle GitHub OAuth callback.

    Processes the OAuth callback, creates or retrieves user, and returns access token.
    """
    try:
        github = get_oauth_client('github')
        token = await github.authorize_access_token(request)

        # Get user info from GitHub API
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_resp = await client.get(
                'https://api.github.com/user',
                headers={
                    'Authorization': f"Bearer {token['access_token']}",
                    'Accept': 'application/json'
                }
            )
            user_data = user_resp.json()

            # Get user emails (GitHub may not include email in profile)
            emails_resp = await client.get(
                'https://api.github.com/user/emails',
                headers={
                    'Authorization': f"Bearer {token['access_token']}",
                    'Accept': 'application/json'
                }
            )
            emails_data = emails_resp.json()

        # Find primary verified email
        email = None
        for email_info in emails_data:
            if email_info.get('primary') and email_info.get('verified'):
                email = email_info.get('email')
                break

        # Fallback to first verified email
        if not email:
            for email_info in emails_data:
                if email_info.get('verified'):
                    email = email_info.get('email')
                    break

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verified email found in GitHub account"
            )

        oauth_id = str(user_data.get('id'))
        name = user_data.get('name') or user_data.get('login', 'User')

        # Check if user exists by OAuth ID or email
        user = db.query(User).filter(
            or_(
                User.oauth_id == oauth_id,
                User.email == email
            )
        ).first()

        if user:
            # Update OAuth info if user exists but doesn't have it
            if not user.oauth_provider or not user.oauth_id:
                user.oauth_provider = 'github'
                user.oauth_id = oauth_id
                db.commit()
                db.refresh(user)
        else:
            # Create new user
            # Generate unique username from GitHub login
            username = user_data.get('login', email.split('@')[0])
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                username=username,
                email=email,
                oauth_provider='github',
                oauth_id=oauth_id,
                password_hash=None  # OAuth users don't have passwords
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )
