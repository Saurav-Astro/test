import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const login = useAuthStore(s => s.login)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [testId, setTestId] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await authAPI.login({ email, password })
      login(data.user, data.access_token)
      const from = location.state?.from || (data.user.role === 'faculty' ? '/faculty' : data.user.role === 'admin' ? '/admin' : '/student')
      navigate(from)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinExam = (e) => {
    e.preventDefault()
    if (testId) {
      navigate(`/join-exam?id=${testId}`)
    }
  }

  return (
    <div className="page" style={{ padding: 0, minHeight: '100vh', display: 'flex', overflow: 'hidden' }}>
      
      {/* Left Decoration / Hero */}
      <div className="auth-hero" style={{ 
        flex: 1, 
        background: 'linear-gradient(145deg, #0a0a1f 0%, #161a35 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '0 80px',
        position: 'relative',
        color: 'white'
      }}>
        {/* Animated background elements */}
        <div style={{ position: 'absolute', top: '10%', left: '5%', width: 300, height: 300, background: 'var(--primary)', filter: 'blur(150px)', opacity: 0.1, pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: '10%', right: '5%', width: 200, height: 200, background: 'var(--accent)', filter: 'blur(120px)', opacity: 0.1, pointerEvents: 'none' }} />

        <div style={{ maxWidth: 500, position: 'relative', zIndex: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
            <div style={{ width: 44, height: 44, background: 'linear-gradient(135deg, var(--primary), var(--accent))', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem' }}>🛡️</div>
            <span style={{ fontSize: '2rem', fontWeight: 900, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, white, #a5b4fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>ProXM</span>
          </div>

          <h1 style={{ fontSize: '3.5rem', fontWeight: 800, lineHeight: 1.1, marginBottom: 24 }}>
            The Next Generation of <span style={{ color: 'var(--primary-light)' }}>AI Proctoring</span>.
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: 48 }}>
            Secure, reliable, and intelligent examination platform for modern education and recruitment.
          </p>

          {/* Join Exam Quick Access */}
          <div className="card-glass" style={{ padding: 24, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>🚀 Ready for an exam?</h3>
            <form onSubmit={handleJoinExam} style={{ display: 'flex', gap: 12 }}>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Enter Test ID / Exam Code" 
                style={{ background: 'rgba(0,0,0,0.2)', color: 'white' }}
                value={testId}
                onChange={e => setTestId(e.target.value)}
              />
              <button className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>Join Now</button>
            </form>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: 12 }}>
              Instant entry with Test ID and security question validation.
            </p>
          </div>
        </div>

        {/* Floating Stat Info */}
        <div style={{ position: 'absolute', bottom: 40, left: 80, display: 'flex', gap: 40, borderTop: '1px solid rgba(148,163,184,0.1)', paddingTop: 32 }}>
          <div><div style={{ fontSize: '1.2rem', fontWeight: 700 }}>99.9%</div><div style={{ fontSize: '0.75rem', color: '#64748b' }}>Precision</div></div>
          <div><div style={{ fontSize: '1.2rem', fontWeight: 700 }}>Real-time</div><div style={{ fontSize: '0.75rem', color: '#64748b' }}>AI Monitoring</div></div>
          <div><div style={{ fontSize: '1.2rem', fontWeight: 700 }}>Encrypted</div><div style={{ fontSize: '0.75rem', color: '#64748b' }}>Submission</div></div>
        </div>
      </div>

      {/* Right Content / Login */}
      <div className="auth-container" style={{ width: 480, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-base)', padding: 40 }}>
        <div className="card" style={{ width: '100%', padding: '48px 40px', background: 'var(--bg-surface)' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 8 }}>Secure Portal</h2>
            <p style={{ color: 'var(--text-muted)' }}>Sign in to access your dashboard</p>
          </div>

          {error && <div className="alert alert-danger" style={{ marginBottom: 24 }}>{error}</div>}

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input 
                type="email" 
                className="form-input" 
                placeholder="name@university.edu"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <label className="form-label" style={{ marginBottom: 0 }}>Password</label>
                <Link to="/forgot-password" style={{ fontSize: '0.8rem', color: 'var(--primary-light)', textDecoration: 'none' }}>Forgot password?</Link>
              </div>
              <input 
                type="password" 
                className="form-input" 
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>

            <button className="btn btn-primary btn-lg" style={{ marginTop: 8 }} disabled={loading}>
              {loading ? <><span className="spinner"></span> Signing in...</> : 'Sign In'}
            </button>
          </form>

          <div style={{ marginTop: 32, textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Don't have a student account? <Link to="/register" style={{ color: 'var(--primary-light)', fontWeight: 600, textDecoration: 'none' }}>Register here</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
