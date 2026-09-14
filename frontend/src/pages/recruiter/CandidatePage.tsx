import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../api/client'

interface CandidatePublic {
  user_id: string
  name: string
  email: string
  professional_summary?: string | null
  education?: string | null
  skills?: string | null
  experience?: string | null
  city?: string | null
  state?: string | null
  linkedin_url?: string | null
}

export function RecruiterCandidatePage() {
  const { candidateId } = useParams()
  const [candidate, setCandidate] = useState<CandidatePublic | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!candidateId) return
    void api
      .get<CandidatePublic>(`/candidates/${candidateId}`)
      .then((res) => setCandidate(res.data))
      .catch(() => setError('Não autorizado a visualizar este candidato.'))
  }, [candidateId])

  if (error) return <p className="error">{error}</p>
  if (!candidate) return <div className="page-loading">Carregando...</div>

  return (
    <div className="stack">
      <div className="hero">
        <h1>{candidate.name}</h1>
        <p>
          {candidate.city}/{candidate.state} · {candidate.email}
        </p>
      </div>
      <div className="panel stack">
        <p>
          <strong>Resumo:</strong> {candidate.professional_summary}
        </p>
        <p>
          <strong>Skills:</strong> {candidate.skills}
        </p>
        <p>
          <strong>Experiência:</strong> {candidate.experience}
        </p>
        <p>
          <strong>Formação:</strong> {candidate.education}
        </p>
      </div>
    </div>
  )
}
