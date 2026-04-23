import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { examsAPI, attemptsAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function ExamJoinPage() {
  const [searchParams] = useSearchParams()
  const examId = searchParams.get('id')
  const navigate = useNavigate()
  const user = useAuthStore(s => s.user)
  
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!examId) {
      navigate('/')
      return
    }
    loadExam()
  }, [examId])

  const loadExam = async () => {
    try {
      const { data } = await examsAPI.getForStudent(examId)
      setExam(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Exam not found or inactive')
    } finally {
      setLoading(false)
    }
  }

  const handleJoin = async (e) => {
    e.preventDefault()
    if (!user) {
      navigate('/login', { state: { from: `/join-exam?id=${examId}` } })
      return
    }
    
    setSubmitting(true)
    setError('')
    try {
      await attemptsAPI.start({ exam_id: examId, entry_password: answer })
      navigate(`/exam/${examId}`)
    } catch (e) {
      setError(e.response?.data?.detail || 'Incorrect answer to security question')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="page flex items-center justify-center"><span className="spinner spinner-lg"></span></div>

  return (
    <div className="page flex items-center justify-center" style={{ padding: 24 }}>
      <div className="card-glass" style={{ maxWidth: 480, width: '100%', padding: 40, textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', marginBottom: 20 }}>🛡️</div>
        <h2 style={{ marginBottom: 8 }}>Secure Exam Access</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
          You are joining: <strong>{exam?.title || 'Unknown Exam'}</strong>
        </p>

        {error && <div className="alert alert-danger" style={{ marginBottom: 24 }}>{error}</div>}

        <form onSubmit={handleJoin} style={{ textAlign: 'left' }}>
          <div className="form-group" style={{ marginBottom: 24 }}>
            <label className="form-label" style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--primary-light)' }}>
              {exam?.entry_question || 'Entry Authorization Question'}
            </label>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 12 }}>
              Your faculty has set a security question to verify your identity before starting.
            </p>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Enter your answer..." 
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              required
              autoFocus
            />
          </div>

          <button className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
            {submitting ? <><span className="spinner"></span> Verifying...</> : 'Continue to Exam →'}
          </button>
        </form>

        <p style={{ marginTop: 24, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          By continuing, you agree to the AI-proctored examination terms. Your camera, screen, and keyboard activity will be monitored.
        </p>
      </div>
    </div>
  )
}
