import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { proctorAPI, attemptsAPI, examsAPI } from '../services/api'

export default function ProctoringReport() {
  const { examId } = useParams()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [attempts, setAttempts] = useState([])
  const [summary, setSummary] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeAttempt, setActiveAttempt] = useState(null)
  const [logs, setLogs] = useState([])
  const [loadingLogs, setLoadingLogs] = useState(false)

  useEffect(() => {
    loadData()
  }, [examId])

  const loadData = async () => {
    setLoading(true)
    try {
      const [examRes, attemptsRes, summaryRes] = await Promise.all([
        examsAPI.get(examId),
        attemptsAPI.allForExam(examId),
        proctorAPI.summary(examId),
      ])
      setExam(examRes.data)
      setAttempts(attemptsRes.data)
      setSummary(summaryRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const viewLogs = async (attempt) => {
    setActiveAttempt(attempt)
    setLoadingLogs(true)
    try {
      const { data } = await proctorAPI.logs(attempt.id)
      setLogs(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingLogs(false)
    }
  }

  const terminateExam = async (attemptId) => {
    if (!window.confirm('Are you sure you want to forcibly terminate this student\'s exam?')) return
    try {
      await proctorAPI.terminate({ attempt_id: attemptId, reason: 'Manually terminated by faculty.' })
      loadData()
      setActiveAttempt(null)
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) return <div className="page flex items-center justify-center"><span className="spinner spinner-lg"></span></div>

  return (
    <div className="page" style={{ padding: '80px 32px' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
          <div>
            <h1>Proctoring Report</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Monitoring: <strong>{exam?.title}</strong></p>
          </div>
          <button className="btn btn-secondary" onClick={() => navigate('/faculty')}>Back to Dashboard</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
          <div className="stat-card">
            <span className="stat-label">Total Attempts</span>
            <span className="stat-value">{attempts.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Critical Violations</span>
            <span className="stat-value" style={{ color: 'var(--danger)' }}>
              {summary.reduce((a, b) => a + (b.critical || 0), 0)}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Face Issues</span>
            <span className="stat-value" style={{ color: 'var(--warning)' }}>
              {summary.reduce((a, b) => a + (b.face_events || 0), 0)}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Window Switches</span>
            <span className="stat-value" style={{ color: 'var(--accent)' }}>
              {summary.reduce((a, b) => a + (b.window_switches || 0), 0)}
            </span>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 20 }}>Student Performance & Proctoring</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Violations</th>
                  <th>Last Event</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map(attempt => {
                  const studentSum = summary.find(s => s.student_id === attempt.student_id) || {}
                  return (
                    <tr key={attempt.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{attempt.student_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{attempt.student_email}</div>
                      </td>
                      <td>
                        <span className={`badge ${attempt.status === 'submitted' ? 'badge-success' : attempt.status === 'terminated' ? 'badge-danger' : 'badge-primary'}`}>
                          {attempt.status}
                        </span>
                      </td>
                      <td style={{ fontWeight: 700 }}>
                        {attempt.status === 'in_progress' ? '--' : `${attempt.total_score} / ${attempt.max_score}`}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: 4 }}>
                          {studentSum.critical > 0 && <span className="badge badge-danger">! {studentSum.critical} Critical</span>}
                          {studentSum.warnings > 0 && <span className="badge badge-warning">{studentSum.warnings} Warn</span>}
                          {attempt.violation_count > 0 && <span className="badge badge-primary">{attempt.violation_count} Active</span>}
                          {!studentSum.critical && !studentSum.warnings && !attempt.violation_count && <span style={{ color: 'var(--success)' }}>Clean</span>}
                        </div>
                      </td>
                      <td style={{ fontSize: '0.8rem' }}>
                        {attempt.submitted_at ? new Date(attempt.submitted_at).toLocaleTimeString() : 'Active'}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <button className="btn btn-secondary btn-sm" onClick={() => viewLogs(attempt)}>View Logs</button>
                          {attempt.status === 'in_progress' && (
                            <button className="btn btn-danger btn-sm" onClick={() => terminateExam(attempt.id)}>Terminate</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {activeAttempt && (
        <div className="modal-backdrop" onClick={() => setActiveAttempt(null)}>
          <div className="modal" style={{ maxWidth: 700 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Activity Log: {activeAttempt.student_name}</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setActiveAttempt(null)}>✕</button>
            </div>
            
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
              {loadingLogs ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}><span className="spinner"></span></div>
              ) : logs.length === 0 ? (
                <p style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>No proctoring events recorded.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {logs.map(log => (
                    <div key={log.id} style={{ 
                      padding: 12, background: 'var(--bg-elevated)', borderRadius: 8, 
                      borderLeft: `3px solid ${log.severity === 'critical' ? 'var(--danger)' : log.severity === 'warning' ? 'var(--warning)' : 'var(--primary)'}` 
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase' }}>{log.event_type.replace(/_/g, ' ')}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(log.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{log.detail}</p>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4 }}>
                        Sec {log.section_index + 1} | Q {log.question_index + 1}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div style={{ marginTop: 24, textAlign: 'right' }}>
              <button className="btn btn-primary" onClick={() => setActiveAttempt(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
