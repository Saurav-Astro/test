import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Navbar() {
  const user = useAuthStore(s => s.user)
  const logout = useAuthStore(s => s.logout)
  const isFaculty = useAuthStore(s => s.isFaculty)
  const isAdmin = useAuthStore(s => s.isAdmin)
  const navigate = useNavigate()
  const initials = user?.name?.split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2) || '?'

  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">
        <div className="nav-logo-icon">🛡️</div>
        <span className="nav-logo-text">ProXM</span>
      </Link>

      <div className="nav-actions">
        {isFaculty() && (
          <>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/faculty')}>Dashboard</button>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/faculty/exam/new')}>+ New Exam</button>
            {isAdmin() && <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin')}>Admin</button>}
          </>
        )}
        {!isFaculty() && (
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/student')}>My Exams</button>
        )}

        <div className="nav-user">
          <div className="nav-avatar">{initials}</div>
          <span style={{color:'var(--text-secondary)', fontSize:'0.8rem'}}>{user?.name}</span>
          <span className="badge badge-primary" style={{fontSize:'0.7rem'}}>{user?.role}</span>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={logout}>Sign Out</button>
      </div>
    </nav>
  )
}
