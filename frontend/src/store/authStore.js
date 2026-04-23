import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user:  null,
      token: null,

      login: (user, token) => set({ user, token }),

      logout: () => {
        set({ user: null, token: null })
        window.location.href = '/login'
      },

      isLoggedIn:  () => !!get().token,
      isFaculty:   () => ['faculty', 'admin'].includes(get().user?.role),
      isAdmin:     () => get().user?.role === 'admin',
      isStudent:   () => get().user?.role === 'student',
    }),
    {
      name: 'proxm-auth',
      partialize: (s) => ({ user: s.user, token: s.token }),
    }
  )
)
