import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

function OAuthCallback() {
  const [error, setError] = useState('')
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('OAuth callback - Full URL:', window.location.href)
        console.log('OAuth callback - Hash:', window.location.hash)
        console.log('OAuth callback - Search:', window.location.search)

        // Check for error in query params first
        const errorParam = searchParams.get('error')
        if (errorParam) {
          console.error('OAuth error:', errorParam)
          setError(errorParam)
          setTimeout(() => navigate('/login'), 3000)
          return
        }

        // Try to get token from URL hash (format: #access_token=xxx&token_type=bearer)
        let accessToken = null

        if (window.location.hash) {
          const hash = window.location.hash.substring(1) // Remove the #
          console.log('Parsing hash:', hash)
          const hashParams = new URLSearchParams(hash)
          accessToken = hashParams.get('access_token')
          console.log('Token from hash:', accessToken ? `${accessToken.substring(0, 20)}...` : null)
        }

        // Fallback: try query params
        if (!accessToken && window.location.search) {
          console.log('Trying query params as fallback')
          accessToken = searchParams.get('access_token')
          console.log('Token from query:', accessToken ? `${accessToken.substring(0, 20)}...` : null)
        }

        if (accessToken) {
          console.log('✅ Token received, storing in localStorage')
          localStorage.setItem('access_token', accessToken)

          // Verify token was stored
          const storedToken = localStorage.getItem('access_token')
          console.log('✅ Token verified in storage:', storedToken ? 'YES' : 'NO')

          console.log('✅ Redirecting to dashboard in 200ms...')
          // Wait a bit to ensure localStorage is flushed
          setTimeout(() => {
            navigate('/dashboard', { replace: true })
          }, 200)
        } else {
          console.error('❌ No access token found in URL')
          console.error('Hash:', window.location.hash)
          console.error('Search:', window.location.search)
          setError('No access token received. Please try logging in again.')
          setTimeout(() => navigate('/login', { replace: true }), 3000)
        }
      } catch (err) {
        console.error('OAuth callback error:', err)
        setError('Authentication failed: ' + err.message)
        setTimeout(() => navigate('/login', { replace: true }), 3000)
      }
    }

    handleCallback()
  }, [navigate, searchParams])

  if (error) {
    return (
      <div className="form-container">
        <h2 className="text-center">Authentication Error</h2>
        <div className="error text-center">{error}</div>
        <p className="text-center mt-10">Redirecting to login...</p>
      </div>
    )
  }

  return (
    <div className="form-container">
      <h2 className="text-center">Authenticating...</h2>
      <p className="text-center mt-10">Please wait while we complete your sign-in.</p>
    </div>
  )
}

export default OAuthCallback
