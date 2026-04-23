import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import FacultyDashboard from './pages/FacultyDashboard'
import StudentDashboard from './pages/StudentDashboard'
import ExamBuilder from './pages/ExamBuilder'
import ExamAttempt from './pages/ExamAttempt'
import ExamResults from './pages/ExamResults'
import AdminPanel from './pages/AdminPanel'
import ProctoringReport from './pages/ProctoringReport'
import ExamJoinPage from './pages/ExamJoinPage'

function PrivateRoute({ children, allowedRoles }) {
  const user = useAuthStore(s => s.user)
  const token = useAuthStore(s => s.token)
  if (!token || !user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role))
    return <Navigate to={user.role === 'student' ? '/student' : '/faculty'} replace />
  return children
}

export default function App() {
  const user = useAuthStore(s => s.user)
  const token = useAuthStore(s => s.token)

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Public */}
        <Route path="/login"    element={(token && user) ? <Navigate to={user?.role === 'student' ? '/student' : user?.role === 'admin' ? '/admin' : '/faculty'} /> : <LoginPage />} />
        <Route path="/register" element={(token && user) ? <Navigate to={user?.role === 'student' ? '/student' : user?.role === 'admin' ? '/admin' : '/faculty'} /> : <RegisterPage />} />

        {/* Faculty */}
        <Route path="/faculty" element={
          <PrivateRoute allowedRoles={['faculty','admin']}>
            <Navbar /><FacultyDashboard />
          </PrivateRoute>
        } />
        <Route path="/faculty/exam/new" element={
          <PrivateRoute allowedRoles={['faculty','admin']}>
            <Navbar /><ExamBuilder />
          </PrivateRoute>
        } />
        <Route path="/faculty/exam/:examId/edit" element={
          <PrivateRoute allowedRoles={['faculty','admin']}>
            <Navbar /><ExamBuilder />
          </PrivateRoute>
        } />
        <Route path="/faculty/exam/:examId/report" element={
          <PrivateRoute allowedRoles={['faculty','admin']}>
            <Navbar /><ProctoringReport />
          </PrivateRoute>
        } />
        <Route path="/admin" element={
          <PrivateRoute allowedRoles={['admin']}>
            <Navbar /><AdminPanel />
          </PrivateRoute>
        } />

        {/* Student */}
        <Route path="/student" element={
          <PrivateRoute allowedRoles={['student']}>
            <Navbar /><StudentDashboard />
          </PrivateRoute>
        } />
        <Route path="/join-exam" element={
          <PrivateRoute allowedRoles={['student']}>
            <Navbar /><ExamJoinPage />
          </PrivateRoute>
        } />
        <Route path="/exam/:examId" element={
          <PrivateRoute allowedRoles={['student']}>
            <ExamAttempt />
          </PrivateRoute>
        } />
        <Route path="/results/:attemptId" element={
          <PrivateRoute allowedRoles={['student','faculty','admin']}>
            <Navbar /><ExamResults />
          </PrivateRoute>
        } />

        {/* Fallback */}
        <Route path="/" element={<Navigate to={(token && user) ? (user?.role === 'student' ? '/student' : user?.role === 'admin' ? '/admin' : '/faculty') : '/login'} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

