import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('carlos.candidate@example.com')
  const [password, setPassword] = useState('Demo@1234')
  const [error, setError] = useState('')

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const user = await login(email, password)
      if (user.role === 'admin') navigate('/admin')
      else if (user.role === 'recruiter') navigate('/recruiter')
      else navigate('/candidate')
    } catch {
      setError('Falha no login. Verifique as credenciais.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Entrar</h1>
        <p>Acesse a plataforma com suas credenciais fictícias de demonstração.</p>
      </div>
      <form className="form panel" onSubmit={onSubmit}>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        </label>
        <label>
          Senha
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Entrar
        </button>
        <p className="muted">
          Não tem conta? <Link to="/register">Cadastre-se</Link>
        </p>
      </form>
    </div>
  )
}
