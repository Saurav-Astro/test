import { useState, useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import { attemptsAPI, codeAPI } from '../services/api'
import { useParams } from 'react-router-dom'

const LANG_MAP = {
  python: 'python', javascript: 'javascript', java: 'java',
  cpp: 'cpp', c: 'c', go: 'go', rust: 'rust',
}

export default function CodeEditor({ question, attemptId, sectionIndex, questionIndex, onAnswer }) {
  const { examId } = useParams()
  const [code,       setCode]       = useState(question.starter_code || getStarter(question.language))
  const [language,   setLanguage]   = useState(question.language || 'python')
  const [stdin,      setStdin]      = useState('')
  const [output,     setOutput]     = useState('')
  const [stderr,     setStderr]     = useState('')
  const [testResults,setTestResults]= useState([])
  const [running,    setRunning]    = useState(false)
  const [testing,    setTesting]    = useState(false)
  const [activeTab,  setActiveTab]  = useState('output')
  const [runtimes,   setRuntimes]   = useState([])
  const saveTimer = useRef(null)

  useEffect(() => {
    codeAPI.runtimes().then(r => setRuntimes(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      if (onAnswer) onAnswer(code)
    }, 1500)
    return () => clearTimeout(saveTimer.current)
  }, [code])

  const runCode = async () => {
    setRunning(true); setOutput(''); setStderr(''); setActiveTab('output')
    try {
      const { data } = await attemptsAPI.runCode({
        attempt_id: attemptId, 
        exam_id: examId,
        section_index: sectionIndex, 
        question_index: questionIndex,
        code, language, stdin, run_tests: false,
      })
      setOutput(data.output || '')
      setStderr(data.stderr || data.compile_output || '')
    } catch (e) { 
        const msg = e.response?.data?.detail || e.message
        setStderr(msg) 
    } finally { setRunning(false) }
  }

  const runTests = async () => {
    setTesting(true); setTestResults([]); setActiveTab('tests')
    try {
      const { data } = await attemptsAPI.runCode({
        attempt_id: attemptId, 
        exam_id: examId,
        section_index: sectionIndex, 
        question_index: questionIndex,
        code, language, stdin, run_tests: true,
      })
      setTestResults(data.test_results || [])
    } catch (e) { 
        const msg = e.response?.data?.detail || e.message
        setOutput(msg) 
    } finally { setTesting(false) }
  }

  const passed = testResults.filter(r => r.passed).length
  const total  = testResults.length

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%', overflow:'hidden'}}>
      {/* Toolbar */}
      <div style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',background:'var(--bg-elevated)',borderBottom:'1px solid var(--border)',flexShrink:0}}>
        <span style={{fontSize:'0.8rem',color:'var(--text-muted)',fontWeight:600}}>Language:</span>
        <select className="form-input form-select" value={language} onChange={e=>setLanguage(e.target.value)}
          style={{width:140,padding:'5px 10px',fontSize:'0.8rem'}}>
          {runtimes.length > 0
            ? runtimes.map(r => <option key={r.language} value={r.language}>{r.language}</option>)
            : Object.keys(LANG_MAP).map(l => <option key={l} value={l}>{l}</option>)
          }
        </select>
        <div style={{flex:1}}/>
        <button className="btn btn-secondary btn-sm" onClick={runCode} disabled={running}>
          {running ? <><span className="spinner"/>Running…</> : '▶ Run'}
        </button>
        {question.test_cases?.length > 0 && (
          <button className="btn btn-accent btn-sm" onClick={runTests} disabled={testing}>
            {testing ? <><span className="spinner"/>Testing…</> : `🧪 Run Tests (${question.test_cases.length})`}
          </button>
        )}
      </div>

      <div style={{flex: '1 1 60%', minHeight: 0}}>
        <Editor
          height="100%"
          language={LANG_MAP[language] || language}
          value={code}
          onChange={val => setCode(val || '')}
          theme="vs-dark"
          options={{
            fontSize: 14,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            lineNumbers: 'on',
            tabSize: 4,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 12 },
            contextmenu: false,
          }}
        />
      </div>

      <div style={{flex: '0 0 40%', minHeight: '200px', borderTop:'1px solid var(--border)', background:'var(--bg-surface)', display:'flex', flexDirection:'column'}}>
        <div className="tabs" style={{padding:'0 12px', flexShrink:0}}>
          <button className={`tab ${activeTab==='stdin'  ?'active':''}`}  onClick={()=>setActiveTab('stdin')}>Input</button>
          <button className={`tab ${activeTab==='output' ?'active':''}`}  onClick={()=>setActiveTab('output')}>Output</button>
          {question.test_cases?.length>0 &&
            <button className={`tab ${activeTab==='tests'?'active':''}`} onClick={()=>setActiveTab('tests')}>
              Test Cases {testResults.length>0 && <span className={`badge badge-${passed===total?'success':'danger'}`} style={{marginLeft:4}}>{passed}/{total}</span>}
            </button>
          }
        </div>
        <div style={{padding:'10px 12px', flex:1, overflowY:'auto'}}>
          {activeTab === 'stdin' && (
            <textarea className="form-input form-textarea" placeholder="Standard input (stdin)…"
              value={stdin} onChange={e=>setStdin(e.target.value)}
              style={{height:'100%', width:'100%', fontFamily:'var(--font-mono)', fontSize:'0.82rem', resize:'none'}} />
          )}
          {activeTab === 'output' && (
            <div className="terminal" style={{height:'100%'}}>
              {running && <span style={{color:'var(--primary-light)'}}>Running…</span>}
              {!running && !output && !stderr && <span style={{color:'var(--text-muted)'}}>Run code to see output.</span>}
              {output && <span>{output}</span>}
              {stderr && <span className="error">{stderr}</span>}
            </div>
          )}
          {activeTab === 'tests' && (
            <div style={{display:'flex',flexDirection:'column',gap:8}}>
              {testResults.length===0 && <span style={{color:'var(--text-muted)',fontSize:'0.85rem'}}>Run tests to see results.</span>}
              {testResults.map(r => (
                <div key={r.test_case_index} style={{
                  padding:'8px 12px', borderRadius:'var(--radius-sm)',
                  background: r.passed ? 'rgba(16,185,129,0.07)' : 'rgba(239,68,68,0.07)',
                  border: `1px solid ${r.passed ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)'}`,
                  fontSize:'0.8rem',
                }}>
                  <div style={{display:'flex',justifyContent:'space-between',marginBottom:r.is_hidden?0:4}}>
                    <span style={{fontWeight:600}}>Test {r.test_case_index+1} {r.is_hidden ? '🔒 Hidden' : ''}</span>
                    <span style={{color: r.passed?'var(--success)':'var(--danger)', fontWeight:700}}>
                      {r.passed ? '✅ Passed' : '❌ Failed'}
                    </span>
                  </div>
                  {!r.is_hidden && (
                    <>
                      {r.actual_output !== undefined && <div style={{color:'var(--text-muted)'}}>Got: <code>{r.actual_output}</code></div>}
                      {!r.passed && r.expected_output && <div style={{color:'var(--text-muted)'}}>Expected: <code>{r.expected_output}</code></div>}
                      {r.stderr && <div className="error">Error: {r.stderr}</div>}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function getStarter(lang) {
  const starters = {
    python: '# Write your solution here\ndef solution():\n    pass\n',
    javascript: '// Write your solution here\nfunction solution() {\n    \n}\n',
    java: 'public class Main {\n    public static void main(String[] args) {\n        // Write your solution here\n    }\n}\n',
    cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your solution here\n    return 0;\n}\n',
    c: '#include <stdio.h>\n\nint main() {\n    // Write your solution here\n    return 0;\n}\n',
    go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    // Write your solution here\n    fmt.Println("Hello")\n}\n',
    rust: 'fn main() {\n    // Write your solution here\n    println!("Hello");\n}\n',
  }
  return starters[lang] || '// Write your solution\n'
}
