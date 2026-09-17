import { FormEvent, useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { AIAnalysis, Application, Job } from '../../types'

export function RecruiterAIPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [jobId, setJobId] = useState('')
  const [apps, setApps] = useState<Application[]>([])
  const [resumeId, setResumeId] = useState('')
  const [result, setResult] = useState<AIAnalysis | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    void api.get<Job[]>('/jobs', { params: { mine: true } }).then((res) => {
      setJobs(res.data)
      if (res.data[0]) setJobId(res.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!jobId) return
    void api.get<Application[]>(`/jobs/${jobId}/applications`).then((res) => {
      setApps(res.data)
      if (res.data[0]) setResumeId(res.data[0].resume_id)
    })
  }, [jobId])

  const analyze = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post<AIAnalysis>('/ai/match-resume-job', {
        resume_id: resumeId,
        job_id: jobId,
      })
      setResult(data)
    } catch {
      setError('Falha na análise. Verifique se o currículo está associado à vaga.')
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>IA do recrutador</h1>
        <p>Analise compatibilidade entre candidatos das suas vagas e os requisitos.</p>
      </div>
      <form className="panel form" onSubmit={analyze}>
        <label>
          Vaga
          <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Currículo do candidato
          <select value={resumeId} onChange={(e) => setResumeId(e.target.value)}>
            {apps.map((a) => (
              <option key={a.id} value={a.resume_id}>
                {a.candidate_name} - {a.resume_filename}
              </option>
            ))}
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit" disabled={!resumeId}>
          Analisar compatibilidade
        </button>
      </form>
      {result?.result && (
        <div className="panel stack">
          <h3>Resultado</h3>
          <p>{result.result.summary}</p>
          <p>
            <strong>Score:</strong> {result.result.compatibility_score}
          </p>
          <p>
            <strong>Skills:</strong> {result.result.key_skills.join(', ')}
          </p>
          <p>
            <strong>Lacunas:</strong> {result.result.gaps.join(', ')}
          </p>
          <p>{result.result.compatibility_notes}</p>
        </div>
      )}
    </div>
  )
}
