import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { examsAPI, attemptsAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function StudentDashboard() {
  const user     = useAuthStore(s => s.user)
  const navigate = useNavigate()
  const [exams, setExams]     = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab]         = useState('available')

  useEffect(() => { loadExams() }, [])

  const loadExams = async () => {
    try {
      const { data } = await examsAPI.available()
      setExams(data)
    } catch(e) { console.error(e) } finally { setLoading(false) }
  }

  const startExam = (examId) => navigate(`/exam/${examId}`)

  const statusBadge = (e) => {
    const now = new Date()
    if (e.start_time && new Date(e.start_time) > now)
      return <span className="badge badge-warning">⏳ Upcoming</span>
    if (e.end_time && new Date(e.end_time) < now)
      return <span className="badge badge-danger">⛔ Expired</span>
    return <span className="badge badge-success">✅ Live</span>
  }

  const isLive = (e) => {
    const now = new Date()
    if (e.start_time && new Date(e.start_time) > now) return false
    if (e.end_time   && new Date(e.end_time)   < now) return false
    return true
  }

  return (
    <div className="page" style={{padding:'80px 32px 32px'}}>
      <div style={{maxWidth:1100,margin:'0 auto'}}>
        {/* Header */}
        <div style={{marginBottom:32}}>
          <h1>👋 Hello, {user?.name?.split(' ')[0]}!</h1>
          <p>Your assigned exams appear below. All exams are AI-proctored.</p>
        </div>

        {/* Stats */}
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16,marginBottom:32}}>
          <div className="stat-card">
            <span className="stat-label">Available Exams</span>
            <span className="stat-value">{exams.filter(isLive).length}</span>
            <span className="stat-sub">Ready to attempt</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Exams</span>
            <span className="stat-value">{exams.length}</span>
            <span className="stat-sub">Assigned to you</span>
          </div>
          <div className="stat-card" style={{borderColor:'rgba(139,92,246,0.35)'}}>
            <span className="stat-label">Proctoring</span>
            <span className="stat-value" style={{color:'var(--primary)',fontSize:'1.4rem'}}>AI Active</span>
            <span className="stat-sub">Face detection enabled</span>
          </div>
        </div>

        {/* Alert */}
        <div className="alert alert-warning" style={{marginBottom:28}}>
          <span>⚠️ </span>
          <div>
            <strong>Exam Rules:</strong> Camera and mic will be active. Do not switch windows, use keyboard shortcuts (Ctrl/Alt/F-keys), or allow others in the room. Violations will be logged and may terminate your exam.
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs" style={{marginBottom:24}}>
          <button className={`tab ${tab==='available'?'active':''}`} onClick={()=>setTab('available')}>Available Exams</button>
          <button className={`tab ${tab==='instructions'?'active':''}`} onClick={()=>setTab('instructions')}>Instructions</button>
        </div>

        {tab === 'available' && (
          <>
            {loading && (
              <div style={{display:'flex',justifyContent:'center',padding:'64px'}}>
                <span className="spinner spinner-lg"></span>
              </div>
            )}
            {!loading && exams.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <h3>No exams available</h3>
                <p>Your faculty hasn't published any exams yet.</p>
              </div>
            )}
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(340px,1fr))',gap:20}}>
              {exams.map(exam => (
                <div key={exam.id} className="card" style={{display:'flex',flexDirection:'column',gap:16}}>
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                    <h3 style={{flex:1}}>{exam.title}</h3>
                    {statusBadge(exam)}
                  </div>
                  {exam.description && <p style={{fontSize:'0.875rem'}}>{exam.description}</p>}
                  <div style={{display:'flex',gap:12,flexWrap:'wrap'}}>
                    <span className="badge badge-primary">📁 {exam.section_count} Section{exam.section_count!==1?'s':''}</span>
                    {exam.start_time && <span className="badge badge-accent">🕒 {new Date(exam.start_time).toLocaleString()}</span>}
                    {exam.end_time   && <span className="badge badge-warning">⏳ Due {new Date(exam.end_time).toLocaleString()}</span>}
                  </div>
                  <div style={{display:'flex',alignItems:'center',gap:8,padding:'8px 12px',background:'rgba(139,92,246,0.06)',borderRadius:'var(--radius-sm)',fontSize:'0.8rem',color:'var(--text-muted)'}}>
                    🛡️ AI-Proctored · 📷 Camera Required · ⌨️ Keyboard Restricted
                  </div>
                  <button className={`btn ${(isLive(exam) && exam.section_count > 0) ? "btn-primary" : "btn-secondary"}`}
                    disabled={!isLive(exam) || exam.section_count === 0} 
                    onClick={() => startExam(exam.id)}>
                    {exam.section_count === 0 ? "No Sections" : isLive(exam) ? "▶ Start Exam" : "Not Available"}
                  </button>
                </div>
              ))}
            </div>
          </>
        )}

        {tab === 'instructions' && (
          <div className="card" style={{maxWidth:720}}>
            <h3 style={{marginBottom:16}}>📋 Exam Instructions</h3>
            <div style={{display:'flex',flexDirection:'column',gap:14}}>
              {[
                ['🎥','Camera Access','Allow camera access when prompted. Your face must be visible at all times.'],
                ['👁️','Face Detection','Only you should be in the room. Multiple faces = immediate warning.'],
                ['🪟','Window Focus','Do NOT switch tabs or windows. Each switch is a violation.'],
                ['⌨️','Keyboard Shortcuts','Ctrl, Alt, F1-F12, and Print Screen are blocked during exam.'],
                ['⌛','Per-Question Timer','Each question has its own countdown. Unanswered questions auto-advance.'],
                ['📝','MCQ Format','All questions are multiple choice. Select one option per question.'],
                ['💻','Coding Section','Some sections may have coding questions with an in-built code editor.'],
                ['📊','Results','Results are available immediately after submission (if enabled by faculty).'],
                ['🚨','Violations','3 violations may auto-terminate your exam. Take this seriously.'],
              ].map(([icon, title, desc]) => (
                <div key={title} style={{display:'flex',gap:14,padding:'12px 16px',background:'var(--bg-elevated)',borderRadius:'var(--radius-md)'}}>
                  <span style={{fontSize:'1.3rem',flexShrink:0}}>{icon}</span>
                  <div>
                    <div style={{fontWeight:600,marginBottom:2}}>{title}</div>
                    <div style={{fontSize:'0.85rem',color:'var(--text-muted)'}}>{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
