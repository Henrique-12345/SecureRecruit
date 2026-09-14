import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { Resume } from '../../types'

export function RecruiterResumePage() {
  const { resumeId } = useParams()
  const [resume, setResume] = useState<Resume | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!resumeId) return
    void api
      .get<Resume>(`/resumes/${resumeId}`)
      .then((res) => setResume(res.data))
      .catch(() => setError('Sem autorização para este currículo.'))
  }, [resumeId])

  const download = async () => {
    if (!resumeId || !resume) return
    const res = await api.get(`/resumes/${resumeId}/download`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = resume.original_filename
    a.click()
    URL.revokeObjectURL(url)
  }

  if (error) return <p className="error">{error}</p>
  if (!resume) return <div className="page-loading">Carregando...</div>

  return (
    <div className="stack">
      <div className="hero">
        <h1>Currículo do candidato</h1>
        <p>{resume.original_filename}</p>
      </div>
      <div className="panel stack">
        <p>
          <strong>MIME:</strong> {resume.content_type}
        </p>
        <p>
          <strong>Tamanho:</strong> {Math.round(resume.file_size / 1024)} KB
        </p>
        <p>
          <strong>SHA-256:</strong> <code>{resume.sha256_hash}</code>
        </p>
        <button className="btn primary" type="button" onClick={() => void download()}>
          Baixar arquivo
        </button>
      </div>
    </div>
  )
}
