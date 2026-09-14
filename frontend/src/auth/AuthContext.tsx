import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api } from '../api/client'
import type { TokenResponse, User, UserRole } from '../types'

interface AuthContextValue {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (payload: {
    name: string
    email: string
    password: string
    role: UserRole
  }) => Promise<User>
  logout: () => Promise<void>
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('sr_token'))
  const [loading, setLoading] = useState(true)

  const persist = (data: TokenResponse) => {
    localStorage.setItem('sr_token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }

  const refreshMe = useCallback(async () => {
    if (!localStorage.getItem('sr_token')) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get<User>('/auth/me')
      setUser(data)
    } catch {
      localStorage.removeItem('sr_token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshMe()
  }, [refreshMe])

  const login = async (email: string, password: string) => {
    const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
    persist(data)
    return data.user
  }

  const register = async (payload: {
    name: string
    email: string
    password: string
    role: UserRole
  }) => {
    const { data } = await api.post<TokenResponse>('/auth/register', payload)
    persist(data)
    return data.user
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // ignore network errors on logout
    }
    localStorage.removeItem('sr_token')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout, refreshMe }),
    [user, token, loading, refreshMe],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
