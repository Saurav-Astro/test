import { useEffect, useRef, useState, useCallback } from 'react'
import { proctorAPI } from '../services/api'

const FACE_API_CDN = 'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js'
const MODELS_URL   = 'https://cdn.jsdelivr.net/gh/justadudewhohacks/face-api.js@master/weights'

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
  const warnTimerRef= useRef(null)

  const [cameraStatus, setCameraStatus] = useState('initializing')
  const [faceCount,    setFaceCount]    = useState(-1)
  const [toast,        setToast]        = useState(null)

  const showToast = useCallback((msg, duration=3500) => {
    setToast(msg)
    clearTimeout(warnTimerRef.current)
    warnTimerRef.current = setTimeout(() => setToast(null), duration)
  }, [])

  const logEvent = useCallback(async (eventType, detail, severity='warning') => {
    if (!attemptId) return
    try {
      const res = await proctorAPI.log({ attempt_id: attemptId, event_type: eventType, section_index: sectionIndex, question_index: questionIndex, detail, severity })
      const newCount = res.data.violation_count ?? 0
      if (onViolation) onViolation(newCount)
      if (res.data.terminated && onTerminate) onTerminate('Exam terminated due to excessive violations')
    } catch {}
  }, [attemptId, sectionIndex, questionIndex, onViolation, onTerminate])

  useEffect(() => {
    if (!cfg.face_detection) return
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
              showToast('🔍 No face detected!')
              if (cfg.multi_face_check) await logEvent('face_not_detected', 'No face in frame', 'warning')
            } else if (count > 1) {
              setCameraStatus('warning')
              showToast('🚨 Multiple faces detected!')
              if (cfg.multi_face_check) await logEvent('multiple_faces', `${count} faces detected`, 'critical')
            } else {
              setCameraStatus('ok')
            }
          } catch {}
        }, 3000)
      } catch {
        setCameraStatus('error')
        showToast('📷 Camera access denied.')
      }
    })()

    return () => {
      active = false
      clearInterval(intervalRef.current)
      streamRef.current?.getTracks().forEach(t=>t.stop())
    }
  }, [cfg.face_detection])

  useEffect(() => {
    if (!cfg.window_switch_ban) return
    const handleBlur = async () => {
      showToast('🪟 Window switch detected!')
      await logEvent('window_switch', 'User switched tabs or windows', 'critical')
    }
    const handleVisibility = async () => {
      if (document.hidden) {
        showToast('👁️ Tab hidden!')
        await logEvent('window_switch', 'Tab became hidden', 'critical')
      }
    }
    window.addEventListener('blur', handleBlur)
    document.addEventListener('visibilitychange', handleVisibility)
    return () => {
      window.removeEventListener('blur', handleBlur)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [cfg.window_switch_ban])

  useEffect(() => {
    if (!cfg.keyboard_restriction) return
    const handle = async (e) => {
      const blocked =
        e.ctrlKey || e.altKey || e.metaKey ||
        (e.key?.startsWith('F') && e.key.length <= 3 && !isNaN(e.key.slice(1))) ||
        ['PrintScreen','ContextMenu','Escape'].includes(e.key)
      if (blocked) {
        e.preventDefault()
        e.stopPropagation()
        showToast(`? "${e.key}" restricted.`)
        await logEvent('keyboard_shortcut', `Blocked key: ${e.key}`, 'warning')
      }
    }
    window.addEventListener('keydown', handle, true)
    return () => window.removeEventListener('keydown', handle, true)
  }, [cfg.keyboard_restriction])

  useEffect(() => {
    const handler = e => e.preventDefault()
    document.addEventListener('contextmenu', handler)
    return () => document.removeEventListener('contextmenu', handler)
  }, [])

  useEffect(() => {
    if (!cfg.fullscreen_required) return
    const req = () => {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {})
    }
    req()
    const handleFsChange = async () => {
      if (!document.fullscreenElement) {
        showToast('🖥️ Full-screen exited.')
        await logEvent('fullscreen_exit', 'Fullscreen exited', 'warning')
        setTimeout(req, 1000)
      }
    }
    document.addEventListener('fullscreenchange', handleFsChange)
    return () => {
      document.removeEventListener('fullscreenchange', handleFsChange)
    }
  }, [cfg.fullscreen_required])

  const dotClass =
    cameraStatus === 'ok'      ? 'dot-green'  :
    cameraStatus === 'warning' ? 'dot-yellow' : 'dot-red'

  return (
    <>
      <div className="proctor-bar" />

      {toast && (
        <div className="proctor-warning-toast" style={{
          padding: '8px 20px', 
          background: 'rgba(239, 68, 68, 0.9)', 
          backdropFilter: 'blur(8px)',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
        }}>
          {toast}
          <button onClick={() => setToast(null)} style={{background:'none', border:'none', color:'#fff', cursor:'pointer', padding:4}}>?</button>
        </div>
      )}

      {cfg.face_detection && (
        <div className="camera-preview" style={{opacity: cameraStatus === 'ok' ? 0.3 : 0.8, transition: 'opacity 0.3s'}}>
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

