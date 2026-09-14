import { Link } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'

export function RecruiterDashboard() {
  const { user } = useAuth()
  return (
    <div className="stack">
      <div className="hero">
        <h1>Painel do recrutador</h1>
        <p>Bem-vindo, {user?.name}. Gerencie vagas e candidaturas.</p>
      </div>
      <div className="grid two">
        <Link className="panel" to="/recruiter/jobs">
          <h3>Minhas vagas</h3>
          <p className="muted">Criar, editar e acompanhar vagas.</p>
        </Link>
        <Link className="panel" to="/recruiter/jobs/new">
          <h3>Nova vaga</h3>
          <p className="muted">Publicar oportunidade.</p>
        </Link>
        <Link className="panel" to="/recruiter/ai">
          <h3>Análise por IA</h3>
          <p className="muted">Comparar currículo e vaga.</p>
        </Link>
      </div>
    </div>
  )
}
