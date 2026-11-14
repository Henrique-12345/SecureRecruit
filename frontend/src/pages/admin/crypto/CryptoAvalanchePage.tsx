import { FormEvent, useState } from 'react'
import { api } from '../../../api/client'

export function CryptoAvalanchePage() {
  const [plaintext, setPlaintext] = useState('AAAAAAAAAAAAAAA!')
  const [algorithm, setAlgorithm] = useState('custom_spn')
  const [avalanche, setAvalanche] = useState<Record<string, unknown> | null>(null)
  const [stats, setStats] = useState<Record<string, unknown> | null>(null)
  const [ciphertext, setCiphertext] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onRun(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const enc = await api.post<{ ciphertext_b64: string; key_id: string }>('/crypto/encrypt', {
        algorithm,
        plaintext,
      })
      setCiphertext(enc.data.ciphertext_b64)
      const av = await api.post<{ report: Record<string, unknown> }>('/crypto/metrics/avalanche', {
        algorithm,
        plaintext,
        key_id: enc.data.key_id,
      })
      setAvalanche(av.data.report)
      const st = await api.post<{ report: Record<string, unknown> }>('/crypto/metrics/statistical', {
        algorithm,
        ciphertext_b64: enc.data.ciphertext_b64,
      })
      setStats(st.data.report)
    } catch {
      setError('Falha ao calcular métricas.')
    } finally {
      setBusy(false)
    }
  }

  const score = typeof avalanche?.avalanche_score === 'number' ? avalanche.avalanche_score : 0

  return (
    <div className="stack">
      <div className="hero">
        <h1>Avalanche & métricas</h1>
        <p>Flip de 1 bit no plaintext e análise estatística do ciphertext.</p>
      </div>
      <div className="panel">
        <form className="form" onSubmit={(e) => void onRun(e)}>
          <label>
            Plaintext
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} required />
          </label>
          <label>
            Algoritmo
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
              <option value="custom_spn">custom_spn</option>
              <option value="aes-256-gcm">aes-256-gcm (nonce aleatório)</option>
            </select>
          </label>
          <button className="btn primary" type="submit" disabled={busy}>
            Calcular
          </button>
        </form>
      </div>

      {avalanche && (
        <div className="panel">
          <h3 className="section-title">Avalanche</h3>
          <p className="muted">Ideal ≈ 0.5 para boa difusão (SPN).</p>
          <div className="meter">
            <div className="meter-fill" style={{ width: `${Math.min(100, score * 100)}%` }} />
          </div>
          <p>
            score=<strong>{score.toFixed(4)}</strong> · bits=
            {String(avalanche.hamming_bits ?? '—')}
          </p>
          <p className="muted">{String(avalanche.note ?? '')}</p>
        </div>
      )}

      {stats && (
        <div className="panel">
          <h3 className="section-title">Estatística do ciphertext</h3>
          <p>
            entropia={String(stats.entropy_bits)} / 8 · χ²=
            {String(stats.chi_square_uniform)} · bytes únicos=
            {String(stats.unique_bytes)}
          </p>
          {ciphertext && (
            <p className="muted">ciphertext b64 ({ciphertext.length} chars)</p>
          )}
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
