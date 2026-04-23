import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { examsAPI, attemptsAPI } from '../services/api'
import ProctoringOverlay from '../components/ProctoringOverlay'
import Timer from '../components/Timer'
import CodeEditor from '../components/CodeEditor'

export default function ExamAttempt() {
  const { examId } = useParams()
  const navigate   = useNavigate()

  const [exam,        setExam]        = useState(null)
  const [attempt,     setAttempt]     = useState(null)
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState('')
  const [terminated,  setTerminated]  = useState(false)
  const [termReason,  setTermReason]  = useState('')
  const [submitted,   setSubmitted]   = useState(false)
  const [violCount,   setViolCount]   = useState(0)

  // Navigation state
  const [sectionIdx,  setSectionIdx]  = useState(0)
  const [questionIdx, setQuestionIdx] = useState(0)
  const [answers,     setAnswers]     = useState({}) // key: `${sIdx}-${qIdx}` ? selected_option | code
  const [sectionDone, setSectionDone] = useState({}) // sIdx ? true

  const [submittingSection, setSubmittingSection] = useState(false)
  const [submittingExam,    setSubmittingExam]    = useState(false)
  const [showSubmitModal,   setShowSubmitModal]   = useState(false)
  const [showSectionModal,  setShowSectionModal]  = useState(false)

  const qTimerKey = useRef(0) // reset timer when question changes

  useEffect(() => { init() }, [])

  const init = async () => {
    try {
      const [examRes, attemptRes] = await Promise.all([
        examsAPI.getForStudent(examId),
        attemptsAPI.start({ exam_id: examId }),
      ])
      setExam(examRes.data)
      setAttempt(attemptRes.data)
      setViolCount(attemptRes.data.violation_count || 0)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Failed to load exam')
    } finally { setLoading(false) }
  }

  const currentSection  = exam?.sections?.[sectionIdx]
  const currentQuestion = currentSection?.questions?.[questionIdx]
  const procCfg         = currentSection?.proctoring || {}
  const answerKey       = `${sectionIdx}-${questionIdx}`

  // Save answer
  const saveAnswer = useCallback(async (selectedOption, code) => {
    if (!attempt) return
    const key = `${sectionIdx}-${questionIdx}`
    setAnswers(prev => ({ ...prev, [key]: selectedOption ?? code }))
    try {
      await attemptsAPI.saveAnswer({
        exam_id:         examId,
        section_index:   sectionIdx,
        question_index:  questionIdx,
        selected_option: selectedOption ?? null,
        code_submission: code ?? null,
        time_spent_seconds: 0,
      })
    } catch {}
  }, [attempt, examId, sectionIdx, questionIdx])

  // Per-question timer expiry
  const onQuestionExpire = useCallback(async () => {
    const qs = currentSection?.questions || []
    if (questionIdx < qs.length - 1) {
      setQuestionIdx(qi => qi + 1)
      qTimerKey.current += 1
    } else {
      setShowSectionModal(true)
    }
  }, [currentSection, questionIdx])

  // Submit section
  const submitSection = async () => {
    setSubmittingSection(true)
    try {
      await attemptsAPI.submitSection({ 
        exam_id: examId,
        section_index: sectionIdx 
      })
      setSectionDone(prev => ({ ...prev, [sectionIdx]: true }))
      const nextIdx = sectionIdx + 1
      if (nextIdx < exam.sections.length) {
        setSectionIdx(nextIdx)
        setQuestionIdx(0)
        qTimerKey.current += 1
      } else {
        setShowSubmitModal(true)
      }
    } catch (e) { 
      console.error(e)
      alert("Submission Error: " + (e.response?.data?.detail || "Check your internet connection."))
    }
    finally { setSubmittingSection(false); setShowSectionModal(false) }
  }

  // Submit exam
  const submitExam = async () => {
    if (!attempt?.id) return
    setSubmittingExam(true)
    try {
      await attemptsAPI.submitExam({ attempt_id: attempt.id })
      setSubmitted(true)
      navigate(`/results/${attempt.id}`)
    } catch (e) { 
      console.error(e)
      alert("Submission Error: " + (e.response?.data?.detail || "Check your internet connection."))
    }
    finally { setSubmittingExam(false); setShowSubmitModal(false) }
  }

  const handleTerminate = (reason) => {
    setTerminated(true)
    setTermReason(reason || 'Exam terminated due to proctoring violations.')
  }

  if (loading) return (
    <div style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',gap:16}}>
      <span className="spinner spinner-lg" />
      <p>Initializing secure exam environment...</p>
    </div>
  )

  if (error) return (
    <div style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',padding:32}}>
      <div className="card" style={{maxWidth:480,textAlign:'center'}}>
        <div style={{fontSize:'3rem',marginBottom:12}}>❌</div>
        <h2 style={{marginBottom:8}}>Cannot Load Exam</h2>
        <p style={{marginBottom:24}}>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/student')}>Back to Dashboard</button>
      </div>
    </div>
  )

  if (terminated) return (
    <div style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',padding:32,background:'var(--bg-base)'}}>
      <div className="card" style={{maxWidth:520,textAlign:'center',borderColor:'var(--danger)'}}>
        <div style={{fontSize:'3.5rem',marginBottom:12}}>🚨</div>
        <h2 style={{marginBottom:8,color:'var(--danger)'}}>Exam Terminated</h2>
        <p style={{marginBottom:24}}>{termReason}</p>
        <div className="alert alert-danger" style={{marginBottom:24,textAlign:'left'}}>
          Your exam has been submitted with the answers provided so far. Your faculty will review the proctoring log.
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/student')}>Return to Dashboard</button>
      </div>
    </div>
  )

  if (!exam) return null;

  if (!currentSection || !currentQuestion) {
    return (
      <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",padding:32}}>
        <div className="card" style={{maxWidth:480,textAlign:"center"}}>
          <div style={{fontSize:"3rem",marginBottom:12}}>⚠️</div>
          <h2 style={{marginBottom:8}}>Invalid Exam Configuration</h2>
          <p style={{marginBottom:24}}>This exam has no sections or questions configured. Please contact your faculty.</p>
          <button className="btn btn-primary" onClick={() => navigate("/student")}>Back to Dashboard</button>
        </div>
      </div>
    );
  }

  const totalQ    = currentSection.questions.length
  const answered  = currentSection.questions.filter((_,i) => answers[`${sectionIdx}-${i}`] !== undefined).length
  const isCoding  = currentQuestion.question_type === 'coding'

  return (
    <div style={{height:'100vh', background:'var(--bg-base)', userSelect:'none', overflow:'hidden'}}>
      {/* AI Proctor */}
      <ProctoringOverlay
        attemptId={attempt?.id}
        sectionIndex={sectionIdx}
        questionIndex={questionIdx}
        proctoringConfig={procCfg}
        onViolation={setViolCount}
        onTerminate={handleTerminate}
      />

      {/* Top bar */}
      <div style={{
        position:'fixed',top:0,left:0,right:0,height:60,zIndex:500,
        display:'flex',alignItems:'center',justifyContent:'space-between',
        padding:'0 24px',
        background:'rgba(8,8,18,0.95)',
        borderBottom:'1px solid var(--border)',
        backdropFilter:'blur(16px)',
      }}>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <div style={{display:'flex',alignItems:'center',gap:8}}>
            <div style={{width:28,height:28,background:'linear-gradient(135deg,var(--primary),var(--accent))',borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'0.9rem'}}>🛡️</div>
            <span style={{fontWeight:800,fontSize:'1rem',background:'linear-gradient(135deg,var(--primary-light),var(--accent))',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>ProXM</span>
          </div>
          <span style={{fontSize:'0.875rem',fontWeight:600,color:'var(--text-secondary)'}}>{exam.title}</span>
          <span className="badge badge-primary">{currentSection.title}</span>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:18}}>
          {procCfg.face_detection && (
            <div className="violation-counter" style={{
              background: violCount > 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.1)',
              borderColor: violCount > 0 ? 'var(--danger)' : 'var(--success)',
              color: violCount > 0 ? 'var(--danger)' : 'var(--success)',
              fontSize: '0.75rem',
              height: 28
            }}>
              {violCount > 0 ? '⚠️' : '✅'} {violCount} / {procCfg.max_warnings || 3}
            </div>
          )}
          <Timer
            key={`${sectionIdx}-${questionIdx}-${qTimerKey.current}`}
            totalSeconds={currentQuestion.time_limit_seconds || currentSection.time_per_question_seconds || 60}
            onExpire={onQuestionExpire}
            warningAt={30} criticalAt={15}
          />
          <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>Q {questionIdx+1}/{totalQ}</span>
          <button className="btn btn-danger btn-sm" onClick={() => setShowSubmitModal(true)}>Submit Exam</button>
        </div>
      </div>

      {/* Main layout */}
      <div style={{display:'flex',paddingTop:60, height:'100%'}}>

        {/* Sidebar */}
        <div style={{
          width:240,flexShrink:0,
          background:'var(--bg-surface)',
          borderRight:'1px solid var(--border)',
          padding:'20px 14px',
          height:'calc(100vh - 60px)',
          overflowY:'auto',display:'flex',flexDirection:'column',gap:20,
        }}>
          {/* Section stepper */}
          <div>
            <div style={{fontSize:'0.75rem',fontWeight:600,color:'var(--text-muted)',marginBottom:10,textTransform:'uppercase',letterSpacing:'0.06em'}}>Sections</div>
            <div style={{display:'flex',flexDirection:'column',gap:6}}>
              {exam.sections.map((sec, si) => (
                <div key={si} style={{
                  padding:'8px 12px',borderRadius:'var(--radius-sm)',
                  background: si===sectionIdx ? 'var(--primary-glow)' : 'var(--bg-elevated)',
                  border: `1px solid ${si===sectionIdx ? 'var(--primary)' : 'var(--border)'}`,
                  fontSize:'0.8rem',fontWeight:500,
                  color: si===sectionIdx ? 'var(--primary-light)' : sectionDone[si] ? 'var(--success)' : 'var(--text-muted)',
                }}>
                  {sectionDone[si] ? '✅ ' : si===sectionIdx ? '✍️ ' : '🔒 '}{sec.title}
                </div>
              ))}
            </div>
          </div>

          {/* Question navigator */}
          <div>
            <div style={{fontSize:'0.75rem',fontWeight:600,color:'var(--text-muted)',marginBottom:10,textTransform:'uppercase',letterSpacing:'0.06em'}}>Questions</div>
            <div className="q-nav">
              {currentSection.questions.map((_, qi) => (
                <div key={qi} className={`q-dot ${qi===questionIdx?'current':answers[`${sectionIdx}-${qi}`]!==undefined?'answered':''}`}
                  onClick={() => { setQuestionIdx(qi); qTimerKey.current+=1 }}>
                  {qi+1}
                </div>
              ))}
            </div>
          </div>

          {/* Progress */}
          <div>
            <div style={{fontSize:'0.75rem',fontWeight:600,color:'var(--text-muted)',marginBottom:6}}>Answered: {answered}/{totalQ}</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{width:`${(answered/totalQ)*100}%`}} />
            </div>
          </div>

          {/* Submit section button */}
          <button className="btn btn-accent" style={{marginTop:'auto', width:'100%'}} onClick={() => setShowSectionModal(true)} disabled={submittingSection}>
            {submittingSection ? <span className="spinner"/> : 'Submit Section ▶'}
          </button>
        </div>

        {/* Content */}
        <div style={{flex:1, height:'calc(100vh - 60px)', overflow: isCoding ? 'hidden' : 'auto', padding: isCoding ? 0 : '32px 40px'}}>
          {isCoding ? (
            <div style={{display:'flex',flexDirection:'column',height:'100%'}}>
              <div style={{padding:'16px 24px',borderBottom:'1px solid var(--border)', flexShrink: 0}}>
                <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:8}}>
                  <span className="badge badge-accent">💻 Coding</span>
                  <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>{currentQuestion.marks} mark{currentQuestion.marks!==1?'s':''}</span>
                </div>
                <h3 style={{lineHeight:1.4,marginBottom:0, fontSize:'1.1rem'}}>{currentQuestion.question_text}</h3>
              </div>
              <div style={{flex:1, minHeight:0}}>
                <CodeEditor
                  question={currentQuestion}
                  attemptId={attempt?.id}
                  sectionIndex={sectionIdx}
                  questionIndex={questionIdx}
                  onAnswer={(code) => saveAnswer(null, code)}
                />
              </div>
            </div>
          ) : (
            <div className="exam-question-card animate-in" style={{margin:'0 auto', maxWidth: 900}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:24}}>
                <div style={{display:'flex',gap:10,alignItems:'center'}}>
                  <span style={{
                    width:36,height:36,borderRadius:'50%',
                    background:'var(--primary-glow)',border:'1.5px solid var(--primary)',
                    display:'flex',alignItems:'center',justifyContent:'center',
                    fontWeight:800,fontSize:'0.9rem',color:'var(--primary-light)',flexShrink:0,
                  }}>{questionIdx+1}</span>
                  <span className="badge badge-primary">MCQ</span>
                  <span style={{fontSize:'0.8rem',color:'var(--text-muted)'}}>{currentQuestion.marks} mark{currentQuestion.marks!==1?'s':''}</span>
                </div>
                <div style={{fontSize:'0.8rem',color:'var(--text-muted)',background:'var(--bg-elevated)',padding:'4px 12px',borderRadius:'var(--radius-sm)'}}>
                  Q {questionIdx+1} of {totalQ}
                </div>
              </div>

              <h3 style={{lineHeight:1.6,marginBottom:28,fontSize:'1.1rem'}}>{currentQuestion.question_text}</h3>

              <div style={{display:'flex',flexDirection:'column',gap:12}}>
                {currentQuestion.options.map((opt, oi) => (
                  <div key={oi}
                    className={`mcq-option ${answers[answerKey]===oi?'selected':''}`}
                    onClick={() => saveAnswer(oi, null)}>
                    <div className="option-circle" />
                    <span style={{fontWeight: answers[answerKey]===oi ? 600 : 400}}>
                      <strong style={{color:'var(--text-muted)',marginRight:8}}>{String.fromCharCode(65+oi)}.</strong>
                      {opt.text}
                    </span>
                  </div>
                ))}
              </div>

              {/* Navigation */}
              <div style={{display:'flex',justifyContent:'space-between',marginTop:32}}>
                <button className="btn btn-secondary"
                  disabled={questionIdx===0}
                  onClick={() => { setQuestionIdx(qi=>qi-1); qTimerKey.current+=1 }}>
                  ← Previous
                </button>
                {questionIdx < totalQ-1 ? (
                  <button className="btn btn-primary"
                    onClick={() => { setQuestionIdx(qi=>qi+1); qTimerKey.current+=1 }}>
                    Next ▶
                  </button>
                ) : (
                  <button className="btn btn-accent" onClick={() => setShowSectionModal(true)}>
                    Submit Section ▶
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Submit Section Modal */}
      {showSectionModal && (
        <div className="modal-backdrop" onClick={() => setShowSectionModal(false)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Submit Section "{currentSection.title}"?</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowSectionModal(false)}>✕</button>
            </div>
            <p style={{marginBottom:8}}>You've answered <strong>{answered}</strong> of <strong>{totalQ}</strong> questions.</p>
            {answered < totalQ && (
              <div className="alert alert-warning" style={{marginBottom:16}}>
                ⚠️ {totalQ-answered} question{totalQ-answered>1?'s are':' is'} unanswered. You cannot return after submitting this section.
              </div>
            )}
            {sectionIdx < exam.sections.length-1
              ? <p style={{marginBottom:24,fontSize:'0.875rem'}}>After submitting, you'll move to the next section: <strong>{exam.sections[sectionIdx+1]?.title}</strong></p>
              : <p style={{marginBottom:24,fontSize:'0.875rem'}}>This is the last section. After submitting, you can finalize your exam.</p>
            }
            <div style={{display:'flex',gap:12,justifyContent:'flex-end'}}>
              <button className="btn btn-secondary" onClick={() => setShowSectionModal(false)}>Keep Answering</button>
              <button className="btn btn-primary" onClick={submitSection} disabled={submittingSection}>
                {submittingSection ? <><span className="spinner"/>Submitting...</> : 'Submit Section'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Submit Exam Modal */}
      {showSubmitModal && (
        <div className="modal-backdrop" onClick={() => setShowSubmitModal(false)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">🏁 Submit Exam?</h3>
              <button className="btn btn-ghost btn-icon" onClick={() => setShowSubmitModal(false)}>✕</button>
            </div>
            <div className="alert alert-warning" style={{marginBottom:20}}>
              ⚠️ This action is <strong>irreversible</strong>. Your exam will be graded and submitted.
            </div>
            <p style={{marginBottom:24,fontSize:'0.875rem'}}>
              Make sure you've answered all questions before proceeding. Unanswered questions will receive 0 marks.
            </p>
            <div style={{display:'flex',gap:12,justifyContent:'flex-end'}}>
              <button className="btn btn-secondary" onClick={() => setShowSubmitModal(false)}>Review Answers</button>
              <button className="btn btn-danger" onClick={submitExam} disabled={submittingExam}>
                {submittingExam ? <><span className="spinner"/>Submitting...</> : 'Submit Exam'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


