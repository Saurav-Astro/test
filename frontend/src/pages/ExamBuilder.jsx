import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { examsAPI } from '../services/api'

export default function ExamBuilder() {
  const { examId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [exam, setExam] = useState({
    title: '',
    description: '',
    sections: [
      {
        title: 'Section 1',
        description: '',
        time_limit_minutes: 30,
        time_per_question_seconds: 60,
        proctoring: {
          face_detection: true,
          multi_face_check: true,
          window_switch_ban: true,
          keyboard_restriction: true,
          max_warnings: 3,
          auto_submit_on_max_warnings: true,
          fullscreen_required: true,
        },
        questions: [],
      },
    ],
  })

  useEffect(() => {
    if (examId) {
      loadExam()
    }
  }, [examId])

  const loadExam = async () => {
    setLoading(true)
    try {
      const { data } = await examsAPI.get(examId)
      setExam(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (examId) {
        await examsAPI.update(examId, exam)
      } else {
        await examsAPI.create(exam)
      }
      navigate('/faculty')
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  const addSection = () => {
    setExam({
      ...exam,
      sections: [
        ...exam.sections,
        {
          title: `Section ${exam.sections.length + 1}`,
          description: '',
          time_limit_minutes: 30,
          time_per_question_seconds: 60,
          proctoring: { ...exam.sections[0].proctoring },
          questions: [],
        },
      ],
    })
  }

  const updateSection = (sIdx, field, value) => {
    const newSections = [...exam.sections]
    newSections[sIdx] = { ...newSections[sIdx], [field]: value }
    setExam({ ...exam, sections: newSections })
  }

  const updateProctoring = (sIdx, field, value) => {
    const newSections = [...exam.sections]
    newSections[sIdx].proctoring = { ...newSections[sIdx].proctoring, [field]: value }
    setExam({ ...exam, sections: newSections })
  }

  const addQuestion = (sIdx, type = 'mcq') => {
    const newSections = [...exam.sections]
    const newQuestion = {
      question_text: '',
      question_type: type,
      marks: 1,
      time_limit_seconds: 60,
      options: type === 'mcq' ? [{ text: '', is_correct: false }] : [],
                          starter_code: type === 'coding' ? '' : null,
                          test_wrapper: type === 'coding' ? '' : null,
      starter_code: type === 'coding' ? '' : null,
      test_wrapper: type === 'coding' ? '' : null,
      test_cases: type === 'coding' ? [{ input: '', expected_output: '', is_hidden: false }] : [],
    }
    newSections[sIdx].questions.push(newQuestion)
    setExam({ ...exam, sections: newSections })
  }

  const updateQuestion = (sIdx, qIdx, field, value) => {
    const newSections = [...exam.sections]
    newSections[sIdx].questions[qIdx] = { ...newSections[sIdx].questions[qIdx], [field]: value }
    setExam({ ...exam, sections: newSections })
  }

  const addOption = (sIdx, qIdx) => {
    const newSections = [...exam.sections]
    newSections[sIdx].questions[qIdx].options.push({ text: '', is_correct: false })
    setExam({ ...exam, sections: newSections })
  }

  const updateOption = (sIdx, qIdx, oIdx, field, value) => {
    const newSections = [...exam.sections]
    newSections[sIdx].questions[qIdx].options[oIdx] = { ...newSections[sIdx].questions[qIdx].options[oIdx], [field]: value }
    setExam({ ...exam, sections: newSections })
  }

  const addTestCase = (sIdx, qIdx) => {
    const newSections = [...exam.sections]
    newSections[sIdx].questions[qIdx].test_cases.push({ input: '', expected_output: '', is_hidden: false })
    setExam({ ...exam, sections: newSections })
  }

  const updateTestCase = (sIdx, qIdx, tIdx, field, value) => {
    const newSections = [...exam.sections]
    newSections[sIdx].questions[qIdx].test_cases[tIdx] = { ...newSections[sIdx].questions[qIdx].test_cases[tIdx], [field]: value }
    setExam({ ...exam, sections: newSections })
  }

  if (loading) return <div className="page flex items-center justify-center"><span className="spinner spinner-lg"></span></div>

  return (
    <div className="page" style={{ padding: '80px 32px' }}>
      <div style={{ maxWidth: 1000, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
          <h1>{examId ? 'Edit Exam' : 'Build New Exam'}</h1>
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-secondary" onClick={() => navigate('/faculty')}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? <span className="spinner"></span> : 'Save Exam'}
            </button>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 32 }}>
          <h3 style={{ marginBottom: 16 }}>Exam Configuration</h3>
          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label">Exam Title</label>
              <input type="text" className="form-input" value={exam.title} onChange={e => setExam({ ...exam, title: e.target.value })} placeholder="Final Semester Examination" />
            </div>
            <div className="form-group">
              <label className="form-label">Description (Optional)</label>
              <input type="text" className="form-input" value={exam.description} onChange={e => setExam({ ...exam, description: e.target.value })} placeholder="General instructions for students" />
            </div>
          </div>
          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <div className="form-group">
              <label className="form-label">ðŸ›¡ï¸ Security Question (Student ID / Key / Entry Q)</label>
              <input type="text" className="form-input" value={exam.entry_question} onChange={e => setExam({ ...exam, entry_question: e.target.value })} placeholder="e.g. Please enter your Student ID" />
            </div>
            <div className="form-group">
              <label className="form-label">ðŸ”‘ Answer / Password / Test ID Code</label>
              <input type="text" className="form-input" value={exam.entry_password} onChange={e => setExam({ ...exam, entry_password: e.target.value })} placeholder="The password students must enter" />
            </div>
          </div>
        </div>

        {exam.sections.map((section, sIdx) => (
          <div key={sIdx} className="card" style={{ marginBottom: 32, borderLeft: '4px solid var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
              <h3 style={{ color: 'var(--primary-light)' }}>{section.title}</h3>
              <button className="btn btn-danger btn-sm" onClick={() => {
                const newSections = exam.sections.filter((_, i) => i !== sIdx)
                setExam({ ...exam, sections: newSections })
              }}>Remove Section</button>
            </div>

            <div className="grid" style={{ gridTemplateColumns: '2fr 1fr 1fr', gap: 16, marginBottom: 24 }}>
              <div className="form-group">
                <label className="form-label">Section Title</label>
                <input type="text" className="form-input" value={section.title} onChange={e => updateSection(sIdx, 'title', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Section Limit (Mins)</label>
                <input type="number" className="form-input" value={section.time_limit_minutes} onChange={e => updateSection(sIdx, 'time_limit_minutes', parseInt(e.target.value))} />
              </div>
              <div className="form-group">
                <label className="form-label">Q Timer (Secs)</label>
                <input type="number" className="form-input" value={section.time_per_question_seconds} onChange={e => updateSection(sIdx, 'time_per_question_seconds', parseInt(e.target.value))} />
              </div>
            </div>

            <div className="card-glass" style={{ padding: 20, marginBottom: 24 }}>
              <h4 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>ðŸ›¡ï¸ Proctoring Controls</h4>
              <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                {[
                  { label: 'Face Detection', field: 'face_detection' },
                  { label: 'Multiple Faces Warn', field: 'multi_face_check' },
                  { label: 'Window Switch Ban', field: 'window_switch_ban' },
                  { label: 'Keyboard Restrict', field: 'keyboard_restriction' },
                  { label: 'Fullscreen Required', field: 'fullscreen_required' },
                  { label: 'Auto Submit on Violation', field: 'auto_submit_on_max_warnings' },
                ].map(ctrl => (
                  <div key={ctrl.field} className="toggle-wrap" onClick={() => updateProctoring(sIdx, ctrl.field, !section.proctoring[ctrl.field])}>
                    <div className={`toggle ${section.proctoring[ctrl.field] ? 'on' : ''}`}></div>
                    <span className="toggle-label">{ctrl.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              {section.questions.map((question, qIdx) => (
                <div key={qIdx} style={{ padding: 20, background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                    <h4 style={{ opacity: 0.8 }}>Question {qIdx + 1}</h4>
                    <button className="btn btn-ghost btn-sm" onClick={() => {
                      const newSections = [...exam.sections]
                      newSections[sIdx].questions.splice(qIdx, 1)
                      setExam({ ...exam, sections: newSections })
                    }}>Delete Q</button>
                  </div>

                  <div className="form-group" style={{ marginBottom: 16 }}>
                    <textarea className="form-input form-textarea" placeholder="Question text..." value={question.question_text} onChange={e => updateQuestion(sIdx, qIdx, 'question_text', e.target.value)} />
                  </div>

                  <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 16 }}>
                    <div className="form-group">
                      <label className="form-label">Type</label>
                      <select className="form-input" value={question.question_type} onChange={e => {
                        const type = e.target.value
                        const newSections = [...exam.sections]
                        newSections[sIdx].questions[qIdx] = {
                          ...newSections[sIdx].questions[qIdx],
                          question_type: type,
                          options: type === 'mcq' ? [{ text: '', is_correct: false }] : [],
                          starter_code: type === 'coding' ? '' : null,
                          test_wrapper: type === 'coding' ? '' : null,
                          test_cases: type === 'coding' ? [{ input: '', expected_output: '', is_hidden: false }] : [],
                        }
                        setExam({ ...exam, sections: newSections })
                      }}>
                        <option value="mcq">MCQ Choice</option>
                        <option value="coding">Coding Problem</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Marks</label>
                      <input type="number" className="form-input" value={question.marks} onChange={e => updateQuestion(sIdx, qIdx, 'marks', parseInt(e.target.value))} />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Time Limit (Sec)</label>
                      <input type="number" className="form-input" value={question.time_limit_seconds} onChange={e => updateQuestion(sIdx, qIdx, 'time_limit_seconds', parseInt(e.target.value))} />
                    </div>
                  </div>

                  {question.question_type === 'mcq' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      <label className="form-label">Options (Check the correct one)</label>
                      {question.options.map((opt, oIdx) => (
                        <div key={oIdx} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                          <input type="radio" checked={opt.is_correct} onChange={() => {
                            const newSections = [...exam.sections]
                            newSections[sIdx].questions[qIdx].options.forEach((o, i) => o.is_correct = i === oIdx)
                            setExam({ ...exam, sections: newSections })
                          }} />
                          <input type="text" className="form-input" value={opt.text} placeholder={`Option ${oIdx + 1}`} onChange={e => updateOption(sIdx, qIdx, oIdx, 'text', e.target.value)} />
                          <button className="btn btn-ghost btn-sm" onClick={() => {
                            const newSections = [...exam.sections]
                            newSections[sIdx].questions[qIdx].options.splice(oIdx, 1)
                            setExam({ ...exam, sections: newSections })
                          }}>âœ•</button>
                        </div>
                      ))}
                      <button className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }} onClick={() => addOption(sIdx, qIdx)}>+ Add Option</button>
                    </div>
                  )}

                  {question.question_type === 'coding' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                      <div className="form-group">
                        <label className="form-label">Language</label>
                        <select className="form-input" value={question.language} onChange={e => updateQuestion(sIdx, qIdx, 'language', e.target.value)}>
                          <option value="python">Python</option>
                          <option value="javascript">JavaScript</option>
                          <option value="java">Java</option>
                          <option value="cpp">C++</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Starter Code</label>
                        <textarea className="form-input form-textarea" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }} value={question.starter_code} onChange={e => updateQuestion(sIdx, qIdx, 'starter_code', e.target.value)} placeholder="def solution(n):\n    # return n" />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Hidden Test Wrapper (LeetCode-style)</label>
                        <textarea className="form-input form-textarea" 
                          style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', background: 'rgba(0,0,0,0.2)' }} 
                          value={question.test_wrapper || ''} 
                          onChange={e => updateQuestion(sIdx, qIdx, 'test_wrapper', e.target.value)} 
                          placeholder={`import sys\ndata = sys.stdin.read().split()\nprint(solution(int(data[0])))`} />
                        <p style={{fontSize:'0.7rem', color:'var(--text-muted)', marginTop:4}}>
                          This code is appended to the student's submission. Use it to call their functions and handle I/O.
                        </p>
                      </div>
                      <div>
                        <label className="form-label" style={{ marginBottom: 8, display: 'block' }}>Test Cases</label>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                          {question.test_cases.map((tc, tIdx) => (
                            <div key={tIdx} style={{ padding: 12, background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 8 }}>
                                <div className="form-group">
                                  <label className="form-label">Input</label>
                                  <input type="text" className="form-input" value={tc.input} onChange={e => updateTestCase(sIdx, qIdx, tIdx, 'input', e.target.value)} />
                                </div>
                                <div className="form-group">
                                  <label className="form-label">Expected Output</label>
                                  <input type="text" className="form-input" value={tc.expected_output} onChange={e => updateTestCase(sIdx, qIdx, tIdx, 'expected_output', e.target.value)} />
                                </div>
                              </div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div className="toggle-wrap" onClick={() => updateTestCase(sIdx, qIdx, tIdx, 'is_hidden', !tc.is_hidden)}>
                                  <div className={`toggle ${tc.is_hidden ? 'on' : ''}`}></div>
                                  <span className="toggle-label">Hidden Test Case</span>
                                </div>
                                <button className="btn btn-ghost btn-sm" onClick={() => {
                                  const newSections = [...exam.sections]
                                  newSections[sIdx].questions[qIdx].test_cases.splice(tIdx, 1)
                                  setExam({ ...exam, sections: newSections })
                                }}>Remove TC</button>
                              </div>
                            </div>
                          ))}
                          <button className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }} onClick={() => addTestCase(sIdx, qIdx)}>+ Add Test Case</button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div style={{ display: 'flex', gap: 12 }}>
                <button className="btn btn-secondary btn-sm" onClick={() => addQuestion(sIdx, 'mcq')}>+ Add MCQ</button>
                <button className="btn btn-secondary btn-sm" onClick={() => addQuestion(sIdx, 'coding')}>+ Add Coding Lab</button>
              </div>
            </div>
          </div>
        ))}

        <button className="btn btn-accent btn-lg" style={{ width: '100%', padding: '20px' }} onClick={addSection}>+ Add New Assessment Section</button>
      </div>
    </div>
  )
}

