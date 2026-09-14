import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'

export function RecruiterJobCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    employment_type: 'full_time',
    salary_range: '',
  })
  const [error, setError] = useState('')

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const { data } = await api.post('/jobs', form)
      navigate(`/recruiter/jobs/${data.id}/applications`)
    } catch {
      setError('Não foi possível criar a vaga.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Criar vaga</h1>
        <p>A vaga será vinculada ao recrutador autenticado.</p>
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
          Tipo
          <select
            value={form.employment_type}
            onChange={(e) => setForm({ ...form, employment_type: e.target.value })}
          >
            <option value="full_time">Integral</option>
            <option value="part_time">Parcial</option>
            <option value="contract">Contrato</option>
            <option value="internship">Estágio</option>
            <option value="remote">Remoto</option>
          </select>
        </label>
        <label>
          Faixa salarial
          <input
            value={form.salary_range}
            onChange={(e) => setForm({ ...form, salary_range: e.target.value })}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Publicar
        </button>
      </form>
    </div>
  )
}
