import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Job } from '../types'

export function HomePage() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    void api.get<Job[]>('/jobs').then((res) => setJobs(res.data.slice(0, 3)))
  }, [])

  return (
    <div className="stack">
      <section className="hero">
        <h1>SecureRecruit</h1>
        <p>
          Plataforma de recrutamento e seleção com perfis, currículos, candidaturas e análise por
          IA - construída para estudos acadêmicos de cibersegurança aplicada a dados e IA.
        </p>
        <div className="actions">
          <Link className="btn primary" to="/jobs">
            Ver vagas
          </Link>
          <Link className="btn secondary" to="/register">
            Criar conta
          </Link>
        </div>
        <div className="hero-visual">
          <strong>Recrutamento com trilha de auditoria</strong>
          <span>Upload, hash SHA-256, JWT e logs de segurança em um fluxo realista.</span>
        </div>
      </section>

      <section className="stack">
        <h2 className="section-title">Vagas em destaque</h2>
        <div className="grid jobs">
          {jobs.map((job) => (
            <article key={job.id} className="panel job-item">
              <h3>{job.title}</h3>
              <p className="muted">{job.location}</p>
              <p>{job.description.slice(0, 120)}...</p>
              <Link className="btn ghost" to={`/jobs/${job.id}`}>
                Detalhes
              </Link>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
