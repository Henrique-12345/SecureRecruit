import { FormEvent, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { Job } from '../../types'

export function RecruiterJobEditPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    employment_type: 'full_time',
    salary_range: '',
    status: 'open',
  })
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return
    void api.get<Job>(`/jobs/${jobId}`).then((res) => {
      const j = res.data
      setForm({
        title: j.title,
        description: j.description,
        requirements: j.requirements,
        location: j.location,
        employment_type: j.employment_type,
        salary_range: j.salary_range || '',
        status: j.status,
      })
    })
  }, [jobId])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await api.put(`/jobs/${jobId}`, form)
      navigate('/recruiter/jobs')
    } catch {
      setError('Falha ao atualizar a vaga.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Editar vaga</h1>
      </div>
      <form className="panel form" style={{ maxWidth: 720 }} onSubmit={onSubmit}>
        <label>
          Título
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
        </label>
        <label>
          Descrição
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            required
          />
        </label>
        <label>
          Requisitos
          <textarea
            value={form.requirements}
            onChange={(e) => setForm({ ...form, requirements: e.target.value })}
            required
          />
        </label>
        <label>
          Local
          <input
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            required
          />
        </label>
        <label>
          Status
          <select
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          >
            <option value="open">open</option>
            <option value="closed">closed</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Salvar
        </button>
      </form>
    </div>
  )
}
