from authlib.integrations.starlette_client import OAuth
from app.config import settings

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Register GitHub OAuth
if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


def get_oauth_client(provider: str):
    """
    Get OAuth client for a specific provider.

    Args:
        provider: OAuth provider name ('google' or 'github')

    Returns:
        OAuth client instance

    Raises:
        ValueError: If provider is not supported or not configured
    """
    if provider == 'google':
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
        return oauth.google
    elif provider == 'github':
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise ValueError("GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.")
        return oauth.github
    else:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
