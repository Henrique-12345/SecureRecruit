import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Application } from '../../types'

export function CandidateApplicationsPage() {
  const [apps, setApps] = useState<Application[]>([])

  useEffect(() => {
    void api.get<Application[]>('/applications/me').then((res) => setApps(res.data))
  }, [])

  return (
    <div className="stack">
      <div className="hero">
        <h1>Minhas candidaturas</h1>
        <p>Acompanhe o andamento das suas aplicações.</p>
      </div>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Vaga</th>
              <th>Currículo</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.id}>
                <td>{a.job_title}</td>
                <td>{a.resume_filename}</td>
                <td>
                  <span className={`badge ${a.status}`}>{a.status}</span>
                </td>
                <td>
                  <Link to={`/candidate/applications/${a.id}`}>Detalhes</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
