import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { Application } from '../../types'

export function CandidateApplicationDetailPage() {
  const { applicationId } = useParams()
  const [app, setApp] = useState<Application | null>(null)

  useEffect(() => {
    if (!applicationId) return
    void api
      .get<Application>(`/applications/${applicationId}`)
      .then((res) => setApp(res.data))
  }, [applicationId])

  if (!app) return <div className="page-loading">Carregando...</div>

  return (
    <div className="stack">
      <div className="hero">
        <h1>Candidatura</h1>
        <p>{app.job_title}</p>
      </div>
      <div className="panel stack">
        <p>
          <strong>Status:</strong> <span className={`badge ${app.status}`}>{app.status}</span>
        </p>
        <p>
          <strong>Currículo:</strong> {app.resume_filename}
        </p>
        <p>
          <strong>Enviada em:</strong> {new Date(app.applied_at).toLocaleString('pt-BR')}
        </p>
      </div>
    </div>
  )
}
