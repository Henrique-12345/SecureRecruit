import { FormEvent, useState } from 'react'
import { api } from '../../../api/client'
import type { CryptoAlgorithm, DecryptResponse, EncryptResponse } from '../../../types/cryptoLab'

export function CryptoEncryptPage() {
  const [algorithm, setAlgorithm] = useState<CryptoAlgorithm>('custom_spn')
  const [plaintext, setPlaintext] = useState('mensagem confidencial do lab')
  const [ciphertext, setCiphertext] = useState('')
  const [keyId, setKeyId] = useState<string | null>(null)
  const [recovered, setRecovered] = useState('')
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [busy, setBusy] = useState(false)

  async function onEncrypt(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    setRecovered('')
    try {
      const { data } = await api.post<EncryptResponse>('/crypto/encrypt', {
        algorithm,
        plaintext,
        key_id: keyId,
      })
      setCiphertext(data.ciphertext_b64)
      setKeyId(data.key_id)
      setInfo(
        `Cifrado com ${data.algorithm}. key=${data.key_id?.slice(0, 8)}… ` +
          `in=${data.input_size} out=${data.output_size} (${data.duration_ms ?? 0} ms)`,
      )
    } catch {
      setError('Falha ao cifrar. Verifique se você está logado como admin.')
    } finally {
      setBusy(false)
    }
  }

  async function onDecrypt(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const { data } = await api.post<DecryptResponse>('/crypto/decrypt', {
        algorithm,
        ciphertext_b64: ciphertext,
        key_id: keyId,
      })
      setRecovered(data.plaintext)
      setInfo(`Decifrado OK (${data.duration_ms ?? 0} ms)`)
    } catch {
      setError('Falha ao decifrar (chave/algoritmo incorretos ou ciphertext inválido).')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Cifrar / Decifrar</h1>
        <p>Round-trip de texto com Custom SPN ou AES-256-GCM.</p>
      </div>
      <div className="panel">
        <form className="form" onSubmit={(e) => void onEncrypt(e)}>
          <label>
            Algoritmo
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value as CryptoAlgorithm)}
            >
              <option value="custom_spn">custom_spn (didático)</option>
              <option value="aes-256-gcm">aes-256-gcm</option>
            </select>
          </label>
          <label>
            Plaintext
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} required />
          </label>
          <label>
            Key ID (opcional)
            <input
              value={keyId ?? ''}
              onChange={(e) => setKeyId(e.target.value || null)}
              placeholder="UUID da chave gerada"
            />
          </label>
          <div className="actions">
            <button className="btn primary" type="submit" disabled={busy}>
              Cifrar
            </button>
          </div>
        </form>
      </div>

      {ciphertext && (
        <div className="panel">
          <h3 className="section-title">Ciphertext (base64)</h3>
          <textarea value={ciphertext} readOnly />
          <form className="form" onSubmit={(e) => void onDecrypt(e)} style={{ marginTop: '1rem' }}>
            <button className="btn secondary" type="submit" disabled={busy}>
              Decifrar
            </button>
          </form>
        </div>
      )}

      {recovered && (
        <div className="panel">
          <h3 className="section-title">Plaintext recuperado</h3>
          <p className="success">{recovered}</p>
        </div>
      )}
      {info && <p className="muted">{info}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
