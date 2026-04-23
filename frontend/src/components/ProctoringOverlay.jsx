import { useEffect, useRef, useState, useCallback } from 'react'
import api, { proctorAPI } from '../services/api'

const FACE_API_CDN = 'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js'
const MODELS_URL   = 'https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@master/weights'
const SECRET_KEY   = 'proxm_secure_exam_secret_2026'

let faceApiLoaded = false
let faceApiLoading = false

async function loadFaceApi() {
  if (faceApiLoaded) return true
  if (faceApiLoading) { await new Promise(r => setTimeout(r, 2000)); return faceApiLoaded }
  faceApiLoading = true
  return new Promise((resolve) => {
    if (window.faceapi) { faceApiLoaded = true; resolve(true); return }
    const script = document.createElement('script')
    script.src = FACE_API_CDN
    script.onload = async () => {
      try {
        await Promise.all([
          window.faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
          window.faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODELS_URL),
        ])
        faceApiLoaded = true
        resolve(true)
      } catch { resolve(false) }
    }
    script.onerror = () => resolve(false)
    document.head.appendChild(script)
  })
}

async function signEvent(eventType, timestamp) {
  const msg = new TextEncoder().encode(`${eventType}${timestamp}${SECRET_KEY}`)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msg)
  return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('')
}

export default function ProctoringOverlay({
  attemptId,
  sectionIndex,
  questionIndex,
  proctoringConfig,
  onViolation,
  onTerminate,
}) {
  const cfg = proctoringConfig || {}
  const videoRef    = useRef(null)
  const streamRef   = useRef(null)
  const intervalRef = useRef(null)
  const pollTimerRef = useRef(null)
  const absenceTimerRef = useRef(null)

  const [cameraStatus, setCameraStatus] = useState('initializing')
  const [faceCount,    setFaceCount]    = useState(-1)
  const [violationScore, setViolationScore] = useState(0)
  const [hardLock, setHardLock] = useState(false)
  const [lockMessage, setLockMessage] = useState('')

  const logEvent = useCallback(async (eventType, detail, severity='warning') => {
    if (!attemptId || hardLock) return
    try {
      const timestamp = new Date().toISOString()
      const signature = await signEvent(eventType, timestamp)
      
      const res = await proctorAPI.log({ 
        attempt_id: attemptId, 
        event_type: eventType, 
        section_index: sectionIndex, 
        question_index: questionIndex, 
        detail, 
        severity,
        timestamp,
        signature
      })
      
      if (res.data.status === "ignored") return

      const score = res.data.violation_score ?? 0
      setViolationScore(score)
      if (onViolation) onViolation(score)
      
      if (res.data.terminated && onTerminate) {
        setHardLock(true)
        setLockMessage('Exam terminated due to violation threshold reached.')
        onTerminate('Exam terminated due to violation threshold reached.')
      }
    } catch (e) {
      console.error("Proctoring Log Error:", e)
    }
  }, [attemptId, sectionIndex, questionIndex, onViolation, onTerminate, hardLock])

  // --- REAL-TIME BACKEND POLLING ---
  useEffect(() => {
    if (!attemptId) return
    pollTimerRef.current = setInterval(async () => {
      try {
        const res = await api.get(`/proctor/status/${attemptId}`)
        if (res.data.terminated && !hardLock) {
          setHardLock(true)
          setLockMessage('Exam externally terminated by system or proctor.')
          if (onTerminate) onTerminate('Exam externally terminated by system or proctor.')
        }
      } catch (e) {
        console.error("Polling error", e)
      }
    }, 5000)
    return () => clearInterval(pollTimerRef.current)
  }, [attemptId, hardLock, onTerminate])

  // --- CAMERA & FACE DETECT UPGRADE ---
  useEffect(() => {
    if (hardLock) return // Enforced globally
    let active = true ;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width:320, height:240 } })
        if (!active) { stream.getTracks().forEach(t=>t.stop()); return }
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream

        const loaded = await loadFaceApi()
        if (!loaded || !active) return
        setCameraStatus('ok')
        await logEvent('session_start', 'Proctoring session started', 'info')

        intervalRef.current = setInterval(async () => {
          if (!videoRef.current || !active) return
          try {
            const dets = await window.faceapi
              .detectAllFaces(videoRef.current, new window.faceapi.TinyFaceDetectorOptions({ inputSize:224, scoreThreshold:0.5 }))
            const count = dets?.length ?? 0
            setFaceCount(count)

            if (count === 0) {
              setCameraStatus('warning')
              if (!absenceTimerRef.current) {
                absenceTimerRef.current = setTimeout(async () => {
                   await logEvent('face_missing_timeout', 'Face missing for > 5 seconds', 'critical')
                }, 5000)
              }
              await logEvent('face_not_detected', 'No face in frame', 'warning')
              
            } else if (count > 1) {
              clearTimeout(absenceTimerRef.current)
              absenceTimerRef.current = null
              setCameraStatus('warning')
              await logEvent('multiple_faces', `${count} faces detected`, 'critical')
            } else {
              clearTimeout(absenceTimerRef.current)
              absenceTimerRef.current = null
              setCameraStatus('ok')
            }
          } catch {}
        }, 2000)
      } catch {
        setCameraStatus('error')
        setHardLock(true)
        setLockMessage('CAMERA ACCESS MANDATORY. Exam blocked.')
        await logEvent('camera_off', 'Camera permission denied or unavailable', 'critical')
      }
    })()

    return () => {
      active = false
      clearInterval(intervalRef.current)
      clearTimeout(absenceTimerRef.current)
      streamRef.current?.getTracks().forEach(t=>t.stop())
    }
  }, [cfg.face_detection, logEvent, cfg.multi_face_check, hardLock])

  // --- WINDOW BLUR & TAB SWITCH ---
  useEffect(() => {
    if (hardLock) return // Enforced globally
    const handleBlur = async () => {
      navigator.clipboard?.writeText('Exam in progress - content hidden')
      await logEvent('window_switch', 'User switched tabs or windows (Window Blur)', 'critical')
    }
    const handleVisibility = async () => {
      if (document.hidden) {
        await logEvent('window_switch', 'Tab became hidden (Visibility Change)', 'critical')
      }
    }
    window.addEventListener('blur', handleBlur)
    document.addEventListener('visibilitychange', handleVisibility)
    return () => {
      window.removeEventListener('blur', handleBlur)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [cfg.window_switch_ban, logEvent, hardLock])

  // --- KEYBOARD & CLIPBOARD LOCKDOWN ---
  useEffect(() => {
    if (hardLock) return // Enforced globally
        const handleKeyup = async (e) => {
      if (e.key === 'PrintScreen') {
        e.preventDefault()
        navigator.clipboard?.writeText('Screenshots blocked')
        await logEvent('screenshot_attempt', 'PrintScreen key pressed (keyup)', 'critical')
      }
    }
    window.addEventListener('keyup', handleKeyup, true)

    const handleKeydown = async (e) => {
      // Screenshot Block
      if (e.key === 'PrintScreen') {
        e.preventDefault()
        await logEvent('screenshot_attempt', 'PrintScreen key pressed', 'critical')
        return
      }

      // DevTools Block
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'i')) {
        e.preventDefault()
        await logEvent('devtools_attempt', 'DevTools opened', 'critical')
        return
      }

      const blocked = e.ctrlKey || e.altKey || e.metaKey || (e.key?.startsWith('F') && e.key.length <= 3 && !isNaN(e.key.slice(1))) || ['ContextMenu','Escape'].includes(e.key)
      if (blocked) {
        e.preventDefault()
        e.stopPropagation()
        await logEvent('keyboard_shortcut', `Blocked key: ${e.key}`, 'warning')
      }
    }
    window.addEventListener('keydown', handleKeydown, true)

    const handleClipboard = async (e) => {
      e.preventDefault()
      const action = e.type
      await logEvent(`${action}_attempt`, `User attempted to ${action}`, 'warning')
    }
    window.addEventListener('copy', handleClipboard, true)
    window.addEventListener('cut', handleClipboard, true)
    window.addEventListener('paste', handleClipboard, true)

        return () => {
      window.removeEventListener('keyup', handleKeyup, true)
      window.removeEventListener('keydown', handleKeydown, true)
      window.removeEventListener('copy', handleClipboard, true)
      window.removeEventListener('cut', handleClipboard, true)
      window.removeEventListener('paste', handleClipboard, true)
    }
  }, [cfg.keyboard_restriction, logEvent, hardLock])

  useEffect(() => {
    const handler = async (e) => { e.preventDefault() }
    document.addEventListener('contextmenu', handler)
    return () => document.removeEventListener('contextmenu', handler)
  }, [])

  // --- FULLSCREEN LOCK ---
  useEffect(() => {
    if (hardLock) return // Enforced globally
    const req = () => { if (!document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {}) }
    req()
    const handleFsChange = async () => {
      if (!document.fullscreenElement) {
        await logEvent('fullscreen_exit', 'Fullscreen exited', 'critical')
        setTimeout(req, 1000)
      }
    }
    document.addEventListener('fullscreenchange', handleFsChange)
    return () => { document.removeEventListener('fullscreenchange', handleFsChange) }
  }, [cfg.fullscreen_required, logEvent, hardLock])

  const dotClass = cameraStatus === 'ok' ? 'dot-green' : cameraStatus === 'warning' ? 'dot-yellow' : 'dot-red'

  return (
    <>
      <div className="proctor-bar" style={{ position: 'fixed', top: 0, left: 0, right: 0, height: 4, zIndex: 9999, background: violationScore > 50 ? 'red' : 'green' }} />
      
      {/* HARD LOCK OVERLAY */}
      {(hardLock || cameraStatus === 'error') && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.95)', zIndex: 10000,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          color: 'white', textAlign: 'center', backdropFilter: 'blur(20px)'
        }}>
          <h1 style={{ color: '#ef4444', fontSize: '3rem', marginBottom: '1rem' }}>⛔ EXAM LOCKED</h1>
          <p style={{ fontSize: '1.5rem', maxWidth: '600px' }}>{lockMessage || 'An unrecoverable proctoring violation has occurred.'}</p>
          <p style={{ marginTop: '2rem', opacity: 0.7 }}>Please contact your instructor.</p>
        </div>
      )}

      {/* SCREEN BLUR DURING VIOLATIONS */}
      {(!hardLock && violationScore >= 80) && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(255, 0, 0, 0.2)', zIndex: 9998,
          backdropFilter: 'blur(10px)', pointerEvents: 'none'
        }} />
      )}

      {true && (
        <div className="camera-preview" style={{opacity: cameraStatus === 'ok' ? 0.3 : 1, transition: 'opacity 0.3s', zIndex: 9999}}>
          <video ref={videoRef} autoPlay muted playsInline />
          <div className="camera-status">
            <div className={`dot ${dotClass}`} />
            {faceCount < 0 ? 'Loading…' : faceCount === 0 ? 'NO FACE' : faceCount === 1 ? 'OK' : `${faceCount} FACES`}
          </div>
        </div>
      )}
    </>
  )
}
