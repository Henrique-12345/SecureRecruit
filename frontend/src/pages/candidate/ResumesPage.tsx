import { FormEvent, useEffect, useState } from 'react'
import { api, getApiBaseUrl } from '../../api/client'
import type { Resume } from '../../types'

export function CandidateResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get<Resume[]>('/resumes')
    setResumes(data)
  }

  useEffect(() => {
    void load()
  }, [])

  const upload = async (e: FormEvent) => {
    e.preventDefault()
    if (!file) return
    setError('')
    setMessage('')
    const form = new FormData()
    form.append('file', file)
    try {
      await api.post('/resumes', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setFile(null)
      setMessage('Currículo enviado com sucesso.')
      await load()
    } catch {
      setError('Falha no upload. Aceitos: PDF e DOCX até o limite configurado.')
    }
  }

  const remove = async (id: string) => {
    await api.delete(`/resumes/${id}`)
    await load()
  }

  const download = (id: string) => {
    const token = localStorage.getItem('sr_token')
    window.open(`${getApiBaseUrl()}/api/v1/resumes/${id}/download?token_hint=use_header`, '_blank')
    // Prefer authenticated fetch + blob for Authorization header
    void api
      .get(`/resumes/${id}/download`, { responseType: 'blob' })
      .then((res) => {
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = resumes.find((r) => r.id === id)?.original_filename || 'resume'
        a.click()
        URL.revokeObjectURL(url)
      })
    void token
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Meus currículos</h1>
        <p>Upload com metadados, MIME type e hash SHA-256.</p>
      </div>

      <form className="panel form" onSubmit={upload}>
        <label>
          Arquivo (PDF ou DOCX)
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="btn primary" type="submit" disabled={!file}>
          Enviar currículo
        </button>
      </form>

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Arquivo</th>
              <th>Tamanho</th>
              <th>SHA-256</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {resumes.map((r) => (
              <tr key={r.id}>
                <td>{r.original_filename}</td>
                <td>{Math.round(r.file_size / 1024)} KB</td>
                <td>
                  <code>{r.sha256_hash.slice(0, 16)}...</code>
                </td>
                <td className="actions">
                  <button className="btn ghost" type="button" onClick={() => download(r.id)}>
                    Baixar
                  </button>
                  <button className="btn danger" type="button" onClick={() => void remove(r.id)}>
                    Excluir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
