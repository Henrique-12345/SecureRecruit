import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { Application } from '../../types'

export function AdminApplicationsPage() {
  const [apps, setApps] = useState<Application[]>([])

  useEffect(() => {
    void api.get<Application[]>('/admin/applications').then((res) => setApps(res.data))
  }, [])

  return (
    <div className="stack">
      <div className="hero">
        <h1>Candidaturas</h1>
        <p>Visão administrativa de todas as aplicações.</p>
      </div>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Candidato</th>
              <th>Vaga</th>
              <th>Status</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.id}>
                <td>{a.candidate_name}</td>
                <td>{a.job_title}</td>
                <td>
                  <span className={`badge ${a.status}`}>{a.status}</span>
                </td>
                <td>{new Date(a.applied_at).toLocaleString('pt-BR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
