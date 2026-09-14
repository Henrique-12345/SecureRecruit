import { FormEvent, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { CandidateProfile } from '../../types'

export function CandidateProfilePage() {
  const [profile, setProfile] = useState<Partial<CandidateProfile>>({})
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    void api.get<CandidateProfile>('/candidates/me').then((res) => setProfile(res.data))
  }, [])

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setMessage('')
    setError('')
    try {
      const { data } = await api.put<CandidateProfile>('/candidates/me', {
        address: profile.address,
        city: profile.city,
        state: profile.state,
        professional_summary: profile.professional_summary,
        education: profile.education,
        skills: profile.skills,
        experience: profile.experience,
        linkedin_url: profile.linkedin_url,
      })
      setProfile(data)
      setMessage('Perfil atualizado.')
    } catch {
      setError('Falha ao atualizar perfil.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Meu perfil</h1>
        <p>Dados profissionais fictícios do candidato.</p>
      </div>
      <form className="panel form" onSubmit={onSubmit} style={{ maxWidth: 720 }}>
        <label>
          Resumo profissional
          <textarea
            value={profile.professional_summary || ''}
            onChange={(e) => setProfile({ ...profile, professional_summary: e.target.value })}
          />
        </label>
        <label>
          Skills
          <textarea
            value={profile.skills || ''}
            onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
          />
        </label>
        <label>
          Experiência
          <textarea
            value={profile.experience || ''}
            onChange={(e) => setProfile({ ...profile, experience: e.target.value })}
          />
        </label>
        <label>
          Formação
          <textarea
            value={profile.education || ''}
            onChange={(e) => setProfile({ ...profile, education: e.target.value })}
          />
        </label>
        <div className="grid two">
          <label>
            Cidade
            <input
              value={profile.city || ''}
              onChange={(e) => setProfile({ ...profile, city: e.target.value })}
            />
          </label>
          <label>
            Estado
            <input
              value={profile.state || ''}
              onChange={(e) => setProfile({ ...profile, state: e.target.value })}
            />
          </label>
        </div>
        <label>
          Endereço
          <input
            value={profile.address || ''}
            onChange={(e) => setProfile({ ...profile, address: e.target.value })}
          />
        </label>
        <label>
          LinkedIn
          <input
            value={profile.linkedin_url || ''}
            onChange={(e) => setProfile({ ...profile, linkedin_url: e.target.value })}
          />
        </label>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Salvar
        </button>
      </form>
    </div>
  )
}
