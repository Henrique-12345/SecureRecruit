import { Link } from 'react-router-dom'

export function AdminDashboard() {
  return (
    <div className="stack">
      <div className="hero">
        <h1>Administração</h1>
        <p>Gestão de usuários, candidaturas e logs de segurança.</p>
      </div>
      <div className="grid two">
        <Link className="panel" to="/admin/users">
          <h3>Usuários</h3>
          <p className="muted">Listar e ativar/desativar contas.</p>
        </Link>
        <Link className="panel" to="/admin/applications">
          <h3>Candidaturas</h3>
          <p className="muted">Visão global das aplicações.</p>
        </Link>
        <Link className="panel" to="/admin/logs">
          <h3>Logs de segurança</h3>
          <p className="muted">Auditoria de eventos relevantes.</p>
        </Link>
        <Link className="panel" to="/jobs">
          <h3>Vagas</h3>
          <p className="muted">Consultar vagas publicadas.</p>
        </Link>
      </div>
    </div>
  )
}
