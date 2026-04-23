import { useState, useEffect } from 'react'
import { adminAPI } from '../services/api'

export default function AdminPanel() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [resetModal, setResetModal] = useState(null)
  const [newPassword, setNewPassword] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const { data } = await adminAPI.listUsers()
      setUsers(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const toggleStatus = async (userId) => {
    try {
      await adminAPI.toggleActive(userId)
      loadUsers()
    } catch (e) {
      console.error(e)
    }
  }

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This cannot be undone.')) return
    try {
      await adminAPI.deleteUser(userId)
      loadUsers()
    } catch (e) {
      console.error(e)
    }
  }

  const handleReset = async () => {
    try {
      await adminAPI.resetPw({ user_id: resetModal.id, new_password: newPassword })
      setResetModal(null)
      setNewPassword('')
      alert('Password reset successfully')
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) return <div className="page flex items-center justify-center"><span className="spinner spinner-lg"></span></div>

  return (
    <div className="page" style={{ padding: '80px 32px' }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <h1 style={{ marginBottom: 32 }}>Admin System Control</h1>

        <div className="card">
          <h3 style={{ marginBottom: 20 }}>User Management</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Joined</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{u.name}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.email}</div>
                    </td>
                    <td><span className={`badge ${u.role === 'admin' ? 'badge-danger' : u.role === 'faculty' ? 'badge-accent' : 'badge-primary'}`}>{u.role}</span></td>
                    <td style={{ fontSize: '0.85rem' }}>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className={`btn btn-sm ${u.is_active ? 'btn-ghost' : 'btn-danger'}`} onClick={() => toggleStatus(u.id)} style={{ color: u.is_active ? 'var(--success)' : 'var(--danger)' }}>
                        {u.is_active ? '● Active' : '○ Suspended'}
                      </button>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => setResetModal(u)}>Key Reset</button>
                        <button className="btn btn-danger btn-sm" onClick={() => deleteUser(u.id)}>Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {resetModal && (
        <div className="modal-backdrop" onClick={() => setResetModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Admin Password Override</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setResetModal(null)}>✕</button>
            </div>
            <p style={{ marginBottom: 16 }}>Forcing password reset for: <strong>{resetModal.name}</strong></p>
            <div className="form-group" style={{ marginBottom: 20 }}>
              <label className="form-label">New Secure Password</label>
              <input type="password" className="form-input" value={newPassword} onChange={e => setNewPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setResetModal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleReset} disabled={!newPassword}>Confirm Override</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
