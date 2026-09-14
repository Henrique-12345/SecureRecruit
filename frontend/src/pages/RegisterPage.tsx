import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import type { UserRole } from '../types'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<UserRole>('candidate')
  const [error, setError] = useState('')

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const user = await register({ name, email, password, role })
      if (user.role === 'recruiter') navigate('/recruiter')
      else navigate('/candidate')
    } catch {
      setError('Não foi possível cadastrar. Verifique os dados.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Cadastro</h1>
        <p>Crie uma conta fictícia de candidato ou recrutador.</p>
      </div>
      <form className="form panel" onSubmit={onSubmit}>
        <label>
          Nome
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
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
            minLength={8}
            required
          />
        </label>
        <label>
          Papel
          <select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
            <option value="candidate">Candidato</option>
            <option value="recruiter">Recrutador</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Criar conta
        </button>
        <p className="muted">
          Já possui conta? <Link to="/login">Entrar</Link>
        </p>
      </form>
    </div>
  )
}
