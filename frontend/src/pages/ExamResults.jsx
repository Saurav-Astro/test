import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { attemptsAPI } from '../services/api'

export default function ExamResults() {
  const { attemptId } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResults()
  }, [attemptId])

  const loadResults = async () => {
    try {
      const { data } = await attemptsAPI.results(attemptId)
      setResult(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="page flex items-center justify-center"><span className="spinner spinner-lg"></span></div>

  if (!result) return <div className="page flex items-center justify-center"><h2>Result not found</h2></div>

  const percentage = (result.total_score / result.max_score) * 100

  return (
    <div className="page" style={{ padding: '80px 32px' }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <div style={{ 
            width: 120, height: 120, borderRadius: '50%', background: 'var(--primary-glow)', 
            border: '4px solid var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 24px', fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary-light)'
          }}>
            {Math.round(percentage)}%
          </div>
          <h1>Exam Completed!</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>{result.exam_title}</p>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 40 }}>
          <div className="stat-card">
            <span className="stat-label">Total Score</span>
            <span className="stat-value">{result.total_score} / {result.max_score}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Proctor Warnings</span>
            <span className="stat-value" style={{ color: result.violation_count > 0 ? 'var(--warning)' : 'var(--success)' }}>
              {result.violation_count}
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Status</span>
            <span className="stat-value" style={{ fontSize: '1.2rem', textTransform: 'uppercase' }}>{result.status}</span>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 32 }}>
          <h3 style={{ marginBottom: 20 }}>Section wise Breakdown</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Section</th>
                  <th>Questions</th>
                  <th>Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {result.sections.map((sec, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600 }}>Section {idx + 1}</td>
                    <td>{sec.answers.length} answered</td>
                    <td style={{ fontWeight: 700 }}>
                      {sec.answers.reduce((a, b) => a + (b.marks_awarded || 0), 0)} pts
                    </td>
                    <td><span className="badge badge-success">{sec.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
          <button className="btn btn-secondary" onClick={() => navigate('/student')}>Back to Dashboard</button>
          <button className="btn btn-primary" onClick={() => window.print()}>Download Result PDF</button>
        </div>
      </div>
    </div>
  )
}
