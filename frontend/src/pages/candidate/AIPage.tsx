import { FormEvent, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { AIAnalysis, Job, Resume } from '../../types'

export function CandidateAIPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [resumeId, setResumeId] = useState('')
  const [jobId, setJobId] = useState('')
  const [result, setResult] = useState<AIAnalysis | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    void api.get<Resume[]>('/resumes').then((res) => {
      setResumes(res.data)
      if (res.data[0]) setResumeId(res.data[0].id)
    })
    void api.get<Job[]>('/jobs').then((res) => {
      setJobs(res.data)
      if (res.data[0]) setJobId(res.data[0].id)
    })
  }, [])

  const analyze = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      if (jobId) {
        const { data } = await api.post<AIAnalysis>('/ai/match-resume-job', {
          resume_id: resumeId,
          job_id: jobId,
        })
        setResult(data)
      } else {
        const { data } = await api.post<AIAnalysis>('/ai/analyze-resume', {
          resume_id: resumeId,
        })
        setResult(data)
      }
    } catch {
      setError('Falha na análise de IA.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Análise de currículo por IA</h1>
        <p>O conteúdo do currículo é tratado como dado não confiável no prompt.</p>
      </div>
      <form className="panel form" onSubmit={analyze}>
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
        <label>
          Vaga (opcional para match)
          <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
            <option value="">Somente análise do currículo</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title}
              </option>
            ))}
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit">
          Executar análise
        </button>
      </form>

      {result?.result && (
        <div className="panel stack">
          <h3>Resultado</h3>
          <p>{result.result.summary}</p>
          <p>
            <strong>Score:</strong>{' '}
            {result.result.compatibility_score ?? result.compatibility_score ?? 'N/A'}
          </p>
          <p>
            <strong>Skills:</strong> {result.result.key_skills.join(', ')}
          </p>
          <p>
            <strong>Pontos fortes:</strong> {result.result.strengths.join(', ')}
          </p>
          <p>
            <strong>Lacunas:</strong> {result.result.gaps.join(', ')}
          </p>
          {result.result.compatibility_notes && <p>{result.result.compatibility_notes}</p>}
        </div>
      )}
    </div>
  )
}
