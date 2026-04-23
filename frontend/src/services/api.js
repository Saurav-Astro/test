import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(err)
  }
)

export default api

export const authAPI = {
  login:          (d) => api.post('/auth/login', d),
  register:       (d) => api.post('/auth/register', d),
  me:             ()  => api.get('/auth/me'),
  forgotPassword: (d) => api.post('/auth/forgot-password', d),
  verifyOTP:      (d) => api.post('/auth/verify-otp-reset', d),
  changePassword: (d) => api.patch('/auth/me/password', d),
}

export const examsAPI = {
  list:          ()       => api.get('/exams'),
  available:     ()       => api.get('/exams/available'),
  get:           (id)     => api.get(`/exams/${id}`),
  getForStudent: (id)     => api.get(`/exams/${id}/student`),
  create:        (d)      => api.post('/exams', d),
  update:        (id, d)  => api.put(`/exams/${id}`, d),
  togglePublish: (id)     => api.patch(`/exams/${id}/publish`),
  delete:        (id)     => api.delete(`/exams/${id}`),
  allStudents:   ()       => api.get('/exams/all/students'),
}

export const attemptsAPI = {
  start:          (d)  => api.post('/attempts/start', d),
  saveAnswer:     (d)  => api.post('/attempts/submit-answer', d),
  submitSection:  (d)  => api.post('/attempts/submit-section', d),
  submitExam:     (d)  => api.post('/attempts/submit', d),
  runCode:        (d)  => api.post('/attempts/execute', d),
  results:        (id) => api.get(`/attempts/results/${id}`),
  allForExam:     (id) => api.get(`/attempts/exam/${id}/all`),
}

export const proctorAPI = {
  log:       (d)  => api.post('/proctor/log', d),
  terminate: (d)  => api.post('/proctor/terminate', d),
  logs:      (id) => api.get(`/proctor/logs/${id}`),
  summary:   (id) => api.get(`/proctor/summary/${id}`),
}

export const codeAPI = {
  runtimes: () => api.get('/code/runtimes'),
}

export const adminAPI = {
  listUsers:    ()  => api.get('/admin/users'),
  createUser:   (d) => api.post('/admin/users', d),
  toggleActive: (id)=> api.patch(`/admin/users/${id}/toggle-active`),
  resetPw:      (d) => api.patch('/admin/users/reset-password', d),
  deleteUser:   (id)=> api.delete(`/admin/users/${id}`),
}
