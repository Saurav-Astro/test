import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const login = useAuthStore(s => s.login)

  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'student', secret_key: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showFacultySecret, setShowFacultySecret] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await authAPI.register(form)
      login(data.user, data.access_token)
      const from = location.state?.from || (data.user.role === 'faculty' ? '/faculty' : data.user.role === 'admin' ? '/admin' : '/student')
      navigate(from)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page flex items-center justify-center" style={{ padding: 24, background: 'var(--bg-base)' }}>
      <div className="card" style={{ maxWidth: 440, width: '100%', padding: '40px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Join ProXM</h2>
          <p style={{ color: 'var(--text-muted)' }}>Create your secure student account</p>
        </div>

        {error && <div className="alert alert-danger" style={{ marginBottom: 24 }}>{error}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input 
              type="text" className="form-input" placeholder="John Doe"
              value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required
            />
          </div>
          <div className="form-group">
            <label className="form-label">University Email</label>
            <input 
              type="email" className="form-input" placeholder="john@university.edu"
              value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" className="form-input" placeholder="Create a strong password"
              value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required
            />
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 6 }}>Min. 8 characters with numbers.</p>
          </div>

          {!showFacultySecret ? (
            <div style={{ textAlign: 'right' }}>
              <button 
                type="button" 
                onClick={() => { setShowFacultySecret(true); setForm({ ...form, role: 'faculty' }) }}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '0.75rem', cursor: 'pointer', textDecoration: 'underline' }}>
                Register as Faculty?
              </button>
            </div>
          ) : (
            <div className="form-group animate-in">
              <label className="form-label" style={{ color: 'var(--accent)' }}>Faculty Access Key</label>
              <input 
                type="password" className="form-input" placeholder="Enter registration secret"
                style={{ borderColor: 'var(--accent)' }}
                value={form.secret_key} onChange={e => setForm({ ...form, secret_key: e.target.value })} required
              />
            </div>
          )}

          <button className="btn btn-primary btn-lg" style={{ marginTop: 12 }} disabled={loading}>
            {loading ? <><span className="spinner"></span> Creating Account...</> : 'Create Account'}
          </button>
        </form>

        <div style={{ marginTop: 32, textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--primary-light)', fontWeight: 600, textDecoration: 'none' }}>Sign in</Link>
        </div>
      </div>
    </div>
  )
}
