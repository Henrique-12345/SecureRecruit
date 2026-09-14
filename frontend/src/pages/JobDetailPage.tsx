import { FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { Job, Resume } from '../types'

export function JobDetailPage() {
  const { jobId } = useParams()
  const { user } = useAuth()
  const [job, setJob] = useState<Job | null>(null)
  const [resumes, setResumes] = useState<Resume[]>([])
  const [resumeId, setResumeId] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return
    void api.get<Job>(`/jobs/${jobId}`).then((res) => setJob(res.data))
    if (user?.role === 'candidate') {
      void api.get<Resume[]>('/resumes').then((res) => {
        setResumes(res.data)
        if (res.data[0]) setResumeId(res.data[0].id)
      })
    }
  }, [jobId, user])

  const apply = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await api.post(`/jobs/${jobId}/applications`, { resume_id: resumeId })
      setMessage('Candidatura enviada com sucesso.')
    } catch {
      setError('Não foi possível candidatar-se. Verifique se a vaga está aberta e o currículo.')
    }
  }

  if (!job) return <div className="page-loading">Carregando vaga...</div>

  return (
    <div className="stack">
      <div className="hero">
        <h1>{job.title}</h1>
        <p>
          {job.location} · {job.employment_type} · {job.salary_range || 'Salário a combinar'}
        </p>
      </div>
      <section className="panel stack">
        <span className={`badge ${job.status}`}>{job.status}</span>
        <div>
          <h3>Descrição</h3>
          <p>{job.description}</p>
        </div>
        <div>
          <h3>Requisitos</h3>
          <p>{job.requirements}</p>
        </div>
      </section>

      {user?.role === 'candidate' && job.status === 'open' && (
        <form className="panel form" onSubmit={apply}>
          <h3>Candidatar-se</h3>
          <label>
            Currículo
            <select value={resumeId} onChange={(e) => setResumeId(e.target.value)} required>
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.original_filename}
                </option>
              ))}
            </select>
          </label>
          {resumes.length === 0 && (
            <p className="muted">
              Você precisa <Link to="/candidate/resumes">enviar um currículo</Link> antes.
            </p>
          )}
          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
          <button className="btn primary" type="submit" disabled={!resumeId}>
            Enviar candidatura
          </button>
        </form>
      )}

      {!user && (
        <p className="muted">
          <Link to="/login">Faça login</Link> como candidato para se candidatar.
        </p>
      )}
    </div>
  )
}
