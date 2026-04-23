import { useEffect, useRef, useState } from 'react'

export default function Timer({ totalSeconds, onExpire, warningAt = 60, criticalAt = 30 }) {
  const [remaining, setRemaining] = useState(totalSeconds)
  const intervalRef = useRef(null)

  useEffect(() => {
    setRemaining(totalSeconds)
  }, [totalSeconds])

  useEffect(() => {
    if (remaining <= 0) { onExpire?.(); return }
    intervalRef.current = setInterval(() => {
      setRemaining(prev => {
        if (prev <= 1) { clearInterval(intervalRef.current); onExpire?.(); return 0 }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(intervalRef.current)
  }, [totalSeconds])

  const mins = Math.floor(remaining / 60).toString().padStart(2, '0')
  const secs = (remaining % 60).toString().padStart(2, '0')
  const cls = remaining <= criticalAt ? 'critical' : remaining <= warningAt ? 'warning' : ''

  return (
    <div className={`timer-box ${cls}`}>
      <span>⏱</span>
      <span>{mins}:{secs}</span>
    </div>
  )
}
