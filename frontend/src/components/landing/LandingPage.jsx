import { Link } from 'react-router-dom'
import './LandingPage.css'

function LandingPage() {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            Trusted Medication Management
          </div>
          <h1 className="hero-title">
            Take Control of Your <span className="gradient-text">Medication Journey</span>
          </h1>
          <p className="hero-subtitle">
            Track medications, monitor side effects, and manage prescriptions for yourself and your loved ones—all in one secure, easy-to-use platform.
          </p>
          <div className="hero-cta">
            <Link to="/register" className="btn btn-primary btn-lg">
              Get Started Free
            </Link>
            <Link to="/login" className="btn btn-secondary btn-lg">
              Sign In
            </Link>
          </div>
          <p className="hero-note">No credit card required • Free forever plan available</p>
        </div>
        <div className="hero-image">
          <div className="hero-image-card card-1">
            <div className="card-icon">💊</div>
            <div className="card-content">
              <div className="card-label">Active Medications</div>
              <div className="card-value">5</div>
            </div>
          </div>
          <div className="hero-image-card card-2">
            <div className="card-icon">✓</div>
            <div className="card-content">
              <div className="card-label">Doses Today</div>
              <div className="card-value">12</div>
            </div>
          </div>
          <div className="hero-image-card card-3">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <div className="card-label">Adherence Rate</div>
              <div className="card-value">98%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="section-header">
          <h2 className="section-title">Everything You Need to Stay on Track</h2>
          <p className="section-subtitle">Comprehensive medication management tools designed for real people</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">💊</div>
            <h3 className="feature-title">Medication Tracking</h3>
            <p className="feature-description">
              Keep a complete record of all medications, dosages, and schedules in one organized place.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⏰</div>
            <h3 className="feature-title">Smart Reminders</h3>
            <p className="feature-description">
              Never miss a dose with intelligent reminders and customizable medication schedules.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3 className="feature-title">Progress Analytics</h3>
            <p className="feature-description">
              Visualize your medication journey with detailed charts and adherence tracking.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h3 className="feature-title">Side Effect Monitoring</h3>
            <p className="feature-description">
              Track and log side effects to share with your healthcare provider for better care.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">👨‍👩‍👧‍👦</div>
            <h3 className="feature-title">Family Management</h3>
            <p className="feature-description">
              Manage medications for multiple family members from a single account.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3 className="feature-title">Refill Alerts</h3>
            <p className="feature-description">
              Get notified when it's time to refill prescriptions so you never run out.
            </p>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="benefits-section">
        <div className="benefits-content">
          <h2 className="section-title">Why Choose MedTrack?</h2>
          <div className="benefits-list">
            <div className="benefit-item">
              <div className="benefit-icon">🔒</div>
              <div className="benefit-text">
                <h4>Secure & Private</h4>
                <p>Your health data is encrypted and never shared without your permission</p>
              </div>
            </div>
            <div className="benefit-item">
              <div className="benefit-icon">📱</div>
              <div className="benefit-text">
                <h4>Access Anywhere</h4>
                <p>Available on web and mobile devices for tracking on the go</p>
              </div>
            </div>
            <div className="benefit-item">
              <div className="benefit-icon">💡</div>
              <div className="benefit-text">
                <h4>Easy to Use</h4>
                <p>Simple, intuitive interface designed for all ages and tech levels</p>
              </div>
            </div>
            <div className="benefit-item">
              <div className="benefit-icon">🎯</div>
              <div className="benefit-text">
                <h4>Personalized Experience</h4>
                <p>Customizable to fit your unique medication management needs</p>
              </div>
            </div>
          </div>
        </div>
        <div className="benefits-visual">
          <div className="visual-stat">
            <div className="visual-stat-value">10,000+</div>
            <div className="visual-stat-label">Active Users</div>
          </div>
          <div className="visual-stat">
            <div className="visual-stat-value">95%</div>
            <div className="visual-stat-label">Satisfaction Rate</div>
          </div>
          <div className="visual-stat">
            <div className="visual-stat-value">24/7</div>
            <div className="visual-stat-label">Available Support</div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="cta-section">
        <h2 className="cta-title">Ready to Get Started?</h2>
        <p className="cta-subtitle">Join thousands of users managing their medications with confidence</p>
        <div className="cta-buttons">
          <Link to="/register" className="btn btn-primary btn-lg">
            Create Free Account
          </Link>
          <Link to="/login" className="btn btn-secondary btn-lg">
            Sign In
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <h3>MedTrack</h3>
            <p>Your trusted medication management companion</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>Product</h4>
              <Link to="/register">Features</Link>
              <Link to="/register">Pricing</Link>
              <Link to="/register">FAQ</Link>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <Link to="/register">About Us</Link>
              <Link to="/register">Contact</Link>
              <Link to="/register">Privacy</Link>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 MedTrack. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
