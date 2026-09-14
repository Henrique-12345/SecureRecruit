import { Link } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'

export function CandidateDashboard() {
  const { user } = useAuth()
  return (
    <div className="stack">
      <div className="hero">
        <h1>Olá, {user?.name}</h1>
        <p>Gerencie seu perfil, currículos e candidaturas.</p>
      </div>
      <div className="grid two">
        <Link className="panel" to="/candidate/profile">
          <h3>Meu perfil</h3>
          <p className="muted">Atualize resumo, skills e experiência.</p>
        </Link>
        <Link className="panel" to="/candidate/resumes">
          <h3>Currículos</h3>
          <p className="muted">Envie PDF/DOCX com hash SHA-256.</p>
        </Link>
        <Link className="panel" to="/candidate/applications">
          <h3>Candidaturas</h3>
          <p className="muted">Acompanhe o status das suas aplicações.</p>
        </Link>
        <Link className="panel" to="/candidate/ai">
          <h3>Análise por IA</h3>
          <p className="muted">Analise seu currículo e compatibilidade com vagas.</p>
        </Link>
      </div>
    </div>
  )
}
