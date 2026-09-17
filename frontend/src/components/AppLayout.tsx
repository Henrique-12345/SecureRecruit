import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function AppLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          SecureRecruit
        </Link>
        <nav className="nav">
          <NavLink to="/jobs">Vagas</NavLink>
          {user?.role === 'candidate' && (
            <>
              <NavLink to="/candidate">Dashboard</NavLink>
              <NavLink to="/candidate/profile">Perfil</NavLink>
              <NavLink to="/candidate/resumes">Currículos</NavLink>
              <NavLink to="/candidate/applications">Candidaturas</NavLink>
              <NavLink to="/candidate/ai">IA</NavLink>
            </>
          )}
          {user?.role === 'recruiter' && (
            <>
              <NavLink to="/recruiter">Dashboard</NavLink>
              <NavLink to="/recruiter/jobs">Minhas vagas</NavLink>
              <NavLink to="/recruiter/ai">IA</NavLink>
            </>
          )}
          {user?.role === 'admin' && (
            <>
              <NavLink to="/admin">Admin</NavLink>
              <NavLink to="/admin/users">Usuários</NavLink>
              <NavLink to="/admin/applications">Candidaturas</NavLink>
              <NavLink to="/admin/logs">Logs</NavLink>
            </>
          )}
        </nav>
        <div className="auth-area">
          {user ? (
            <>
              <span className="user-chip">
                {user.name} · {user.role}
              </span>
              <button type="button" className="btn ghost" onClick={() => void logout()}>
                Sair
              </button>
            </>
          ) : (
            <>
              <Link className="btn ghost" to="/login">
                Entrar
              </Link>
              <Link className="btn primary" to="/register">
                Cadastrar
              </Link>
            </>
          )}
        </div>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        SecureRecruit - plataforma acadêmica fictícia para estudo de cibersegurança.
      </footer>
    </div>
  )
}
