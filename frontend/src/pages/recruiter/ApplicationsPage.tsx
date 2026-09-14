import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { Application } from '../../types'

const STATUSES = ['submitted', 'reviewing', 'interview', 'approved', 'rejected']

export function RecruiterApplicationsPage() {
  const { jobId } = useParams()
  const [apps, setApps] = useState<Application[]>([])
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get<Application[]>(`/jobs/${jobId}/applications`)
    setApps(data)
  }

  useEffect(() => {
    void load().catch(() => setError('Sem permissão ou vaga inexistente.'))
  }, [jobId])

  const updateStatus = async (applicationId: string, status: string) => {
    await api.patch(`/applications/${applicationId}/status`, { status })
    await load()
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Candidatos da vaga</h1>
        <p>Visualize candidaturas e altere o status.</p>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Candidato</th>
              <th>Currículo</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/recruiter/candidates/${a.candidate_id}`}>{a.candidate_name}</Link>
                </td>
                <td>
                  <Link to={`/recruiter/resumes/${a.resume_id}`}>{a.resume_filename}</Link>
                </td>
                <td>
                  <span className={`badge ${a.status}`}>{a.status}</span>
                </td>
                <td>
                  <select
                    value={a.status}
                    onChange={(e) => void updateStatus(a.id, e.target.value)}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
