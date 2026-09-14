import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Job } from '../types'

export function JobsListPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    void api
      .get<Job[]>('/jobs')
      .then((res) => setJobs(res.data))
      .catch(() => setError('Não foi possível carregar as vagas.'))
  }, [])

  return (
    <div className="stack">
      <div className="hero">
        <h1>Vagas</h1>
        <p>Oportunidades abertas disponíveis na plataforma.</p>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="grid jobs">
        {jobs.map((job) => (
          <article key={job.id} className="panel job-item">
            <div className="actions" style={{ justifyContent: 'space-between' }}>
              <h3>{job.title}</h3>
              <span className={`badge ${job.status}`}>{job.status}</span>
            </div>
            <p className="muted">
              {job.location} · {job.employment_type}
            </p>
            <p>{job.description.slice(0, 160)}...</p>
            <Link className="btn primary" to={`/jobs/${job.id}`}>
              Ver detalhes
            </Link>
          </article>
        ))}
      </div>
    </div>
  )
}
