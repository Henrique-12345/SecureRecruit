import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { Job } from '../../types'

export function RecruiterJobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    void api.get<Job[]>('/jobs', { params: { mine: true } }).then((res) => setJobs(res.data))
  }, [])

  return (
    <div className="stack">
      <div className="hero">
        <h1>Minhas vagas</h1>
        <p>Vagas vinculadas ao recrutador autenticado.</p>
      </div>
      <div className="actions">
        <Link className="btn primary" to="/recruiter/jobs/new">
          Criar vaga
        </Link>
      </div>
      <div className="grid jobs">
        {jobs.map((job) => (
          <article key={job.id} className="panel job-item">
            <div className="actions" style={{ justifyContent: 'space-between' }}>
              <h3>{job.title}</h3>
              <span className={`badge ${job.status}`}>{job.status}</span>
            </div>
            <p className="muted">{job.location}</p>
            <div className="actions">
              <Link className="btn ghost" to={`/recruiter/jobs/${job.id}/edit`}>
                Editar
              </Link>
              <Link className="btn secondary" to={`/recruiter/jobs/${job.id}/applications`}>
                Candidatos
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
