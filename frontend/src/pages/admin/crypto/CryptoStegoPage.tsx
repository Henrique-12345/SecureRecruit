import { FormEvent, useState } from 'react'
import { api } from '../../../api/client'
import type { StegoArtifact } from '../../../types/cryptoLab'

export function CryptoStegoPage() {
  const [file, setFile] = useState<File | null>(null)
  const [plaintext, setPlaintext] = useState('payload oculto SecureRecruit')
  const [algorithm, setAlgorithm] = useState('custom_spn')
  const [artifact, setArtifact] = useState<StegoArtifact | null>(null)
  const [extracted, setExtracted] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onEmbed(e: FormEvent) {
    e.preventDefault()
    if (!file) {
      setError('Selecione uma imagem PNG de capa.')
      return
    }
    setBusy(true)
    setError('')
    setExtracted('')
    try {
      const form = new FormData()
      form.append('cover', file)
      form.append('plaintext', plaintext)
      form.append('algorithm', algorithm)
      const { data } = await api.post<{ artifact: StegoArtifact }>('/stego/embed', form)
      setArtifact(data.artifact)
    } catch {
      setError('Falha no embed. Use PNG válido e payload que caiba na capacidade.')
    } finally {
      setBusy(false)
    }
  }

  async function onExtract() {
    if (!artifact) return
    setBusy(true)
    setError('')
    try {
      const form = new FormData()
      form.append('artifact_id', artifact.id)
      const { data } = await api.post<{ plaintext: string }>('/stego/extract', form)
      setExtracted(data.plaintext)
    } catch {
      setError('Falha ao extrair/decifrar o payload.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Esteganografia LSB</h1>
        <p>Cifra o texto e oculta o ciphertext nos bits menos significativos de um PNG.</p>
      </div>
      <div className="panel">
        <form className="form" onSubmit={(e) => void onEmbed(e)}>
          <label>
            Imagem capa (PNG)
            <input
              type="file"
              accept="image/png,.png"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
          </label>
          <label>
            Payload (texto)
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} required />
          </label>
          <label>
            Algoritmo
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
              <option value="custom_spn">custom_spn</option>
              <option value="aes-256-gcm">aes-256-gcm</option>
            </select>
          </label>
          <button className="btn primary" type="submit" disabled={busy}>
            Cifrar + Embed
          </button>
        </form>
      </div>

      {artifact && (
        <div className="panel stack">
          <h3 className="section-title">Artefato</h3>
          <p className="muted">
            id={artifact.id.slice(0, 8)}… · capacidade={artifact.capacity_bits} bits · payload=
            {artifact.payload_bits} bits
          </p>
          <div className="actions">
            <button
              className="btn secondary"
              type="button"
              disabled={busy}
              onClick={() => {
                void api
                  .get(`/stego/artifacts/${artifact.id}/download`, { responseType: 'blob' })
                  .then((res) => {
                    const url = URL.createObjectURL(res.data)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = artifact.stego_stored_filename
                    a.click()
                    URL.revokeObjectURL(url)
                  })
              }}
            >
              Baixar PNG stego
            </button>
            <button className="btn primary" type="button" disabled={busy} onClick={() => void onExtract()}>
              Extrair + Decifrar
            </button>
          </div>
          {extracted && <p className="success">Recuperado: {extracted}</p>}
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
