import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './components/landing/LandingPage'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import Dashboard from './components/common/Dashboard'
import ThirdParties from './components/common/ThirdParties'
import LogsPage from './components/logs/LogsPage'
import Regimens from './components/regimens/Regimens'
import TrackingPage from './components/tracking/TrackingPage'
import Navigation from './components/common/Navigation'
import OAuthCallback from './components/auth/OAuthCallback'

// Protected route wrapper
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return (
    <>
      <Navigation />
      {children}
    </>
  )
}

// Public route wrapper (redirects to dashboard if already logged in)
function PublicRoute({ children }) {
  const token = localStorage.getItem('access_token')
  if (token) {
    return <Navigate to="/dashboard" replace />
  }
  return children
}

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/"
            element={
              <PublicRoute>
                <LandingPage />
              </PublicRoute>
            }
          />
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            }
          />
          <Route path="/auth/callback" element={<OAuthCallback />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/third-parties"
            element={
              <ProtectedRoute>
                <ThirdParties />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs"
            element={
              <ProtectedRoute>
                <LogsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/medications"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/regimens"
            element={
              <ProtectedRoute>
                <Regimens />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tracking"
            element={
              <ProtectedRoute>
                <TrackingPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
