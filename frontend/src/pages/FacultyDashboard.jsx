import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { examsAPI, attemptsAPI, proctorAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function FacultyDashboard() {
  const user     = useAuthStore(s => s.user)
  const navigate = useNavigate()
  const [exams, setExams]     = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab]         = useState('exams')
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [toggling, setToggling] = useState(null)

  useEffect(() => { loadExams() }, [])

  const loadExams = async () => {
    try { const { data } = await examsAPI.list(); setExams(data) }
    catch(e) { console.error(e) } finally { setLoading(false) }
  }

  const handleToggle = async (id) => {
    setToggling(id)
    try { await examsAPI.togglePublish(id); await loadExams() }
    catch(e) { console.error(e) } finally { setToggling(null) }
  }

  const handleDelete = async (id) => {
    try { await examsAPI.delete(id); setConfirmDelete(null); await loadExams() }
    catch(e) { console.error(e) }
  }

  const stats = {
    total: exams.length,
    published: exams.filter(e => e.is_published).length,
    draft: exams.filter(e => !e.is_published).length,
    questions: exams.reduce((a,e) => a + (e.sections||[]).reduce((b,s)=>b+(s.questions||[]).length,0), 0),
  }

  return (
    <div className="page" style={{padding:'80px 32px 32px'}}>
      <div style={{maxWidth:1200,margin:'0 auto'}}>

        {/* Header */}
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:32,flexWrap:'wrap',gap:16}}>
          <div>
            <h1>Faculty Dashboard</h1>
            <p>Manage your exams and monitor students, {user?.name}.</p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/faculty/exam/new')}>
            ✚ Create New Exam
          </button>
        </div>

        {/* Stats */}
        <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:16,marginBottom:32}}>
          {[
            {label:'Total Exams', value:stats.total, sub:'created by you'},
            {label:'Published',   value:stats.published, sub:'live exams', color:'var(--success)'},
            {label:'Drafts',      value:stats.draft, sub:'unpublished'},
            {label:'Questions',   value:stats.questions, sub:'across all exams', color:'var(--primary-light)'},
          ].map(s => (
            <div key={s.label} className="stat-card" style={s.color ? {borderColor:'rgba(139,92,246,0.3)'}:{}}>
              <span className="stat-label">{s.label}</span>
              <span className="stat-value" style={s.color ? {color:s.color}:{}}>{s.value}</span>
              <span className="stat-sub">{s.sub}</span>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="tabs" style={{marginBottom:24}}>
          <button className={`tab ${tab==='exams'?'active':''}`}    onClick={()=>setTab('exams')}>My Exams</button>
          <button className={`tab ${tab==='students'?'active':''}`} onClick={()=>setTab('students')}>Students</button>
        </div>

        {tab === 'exams' && (
          <>
            {loading && <div style={{display:'flex',justifyContent:'center',padding:64}}><span className="spinner spinner-lg"/></div>}
            {!loading && exams.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <h3>No exams yet</h3>
                <p>Create your first exam to get started.</p>
                <button className="btn btn-primary" onClick={() => navigate('/faculty/exam/new')}>+ Create Exam</button>
              </div>
            )}
            <div style={{display:'flex',flexDirection:'column',gap:12}}>
              {exams.map(exam => (
                <div key={exam.id} className="card" style={{display:'flex',alignItems:'center',gap:20,flexWrap:'wrap'}}>
                  <div style={{flex:1,minWidth:200}}>
                    <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:4}}>
                      <h4>{exam.title}</h4>
                      <span className={`badge ${exam.is_published?'badge-success':'badge-warning'}`}>
                        {exam.is_published ? '● Live' : '○ Draft'}
                      </span>
                    </div>
                    <div style={{display:'flex',gap:12,flexWrap:'wrap'}}>
                      <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>
                        📂 {exam.sections?.length||0} sections
                      </span>
                      <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>
                        ❓ {(exam.sections||[]).reduce((a,s)=>a+(s.questions||[]).length,0)} questions
                      </span>
                      {exam.start_time && <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>🕐 {new Date(exam.start_time).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
                    <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/faculty/exam/${exam.id}/edit`)}>✏️ Edit</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/faculty/exam/${exam.id}/report`)}>📊 Report</button>
                    <button className={`btn btn-sm ${exam.is_published ? 'btn-warning' : 'btn-accent'}`}
                      disabled={toggling === exam.id}
                      onClick={() => handleToggle(exam.id)}
                      style={exam.is_published ? {background:'rgba(245,158,11,0.15)',color:'var(--warning)',border:'1px solid rgba(245,158,11,0.3)'}:{}}>
                      {toggling===exam.id ? <span className="spinner"/> : (exam.is_published ? '⏸ Unpublish' : '▶ Publish')}
                    </button>
                    <button className="btn btn-danger btn-sm" onClick={() => setConfirmDelete(exam.id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {tab === 'students' && <StudentsTab />}
      </div>

      {/* Delete confirm modal */}
      {confirmDelete && (
        <div className="modal-backdrop" onClick={() => setConfirmDelete(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Delete Exam?</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setConfirmDelete(null)}>✕</button>
            </div>
            <p style={{marginBottom:24}}>This action is permanent and will delete all associated attempts and data.</p>
            <div style={{display:'flex',gap:12,justifyContent:'flex-end'}}>
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancel</button>
              <button className="btn btn-danger" onClick={() => handleDelete(confirmDelete)}>Delete Exam</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function StudentsTab() {
  const [students, setStudents] = useState([])
  const [loading, setLoading]   = useState(true)
  useEffect(() => {
    examsAPI.allStudents().then(r => setStudents(r.data)).catch(console.error).finally(() => setLoading(false))
  }, [])
  if (loading) return <div style={{display:'flex',justifyContent:'center',padding:64}}><span className="spinner spinner-lg"/></div>
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead>
        <tbody>
          {students.map(s => (
            <tr key={s.id}>
              <td style={{fontWeight:500}}>{s.name}</td>
              <td style={{color:'var(--text-muted)'}}>{s.email}</td>
              <td><span className="badge badge-primary">{s.role}</span></td>
            </tr>
          ))}
          {students.length === 0 && <tr><td colSpan={3} style={{textAlign:'center',color:'var(--text-muted)',padding:40}}>No students registered yet</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
