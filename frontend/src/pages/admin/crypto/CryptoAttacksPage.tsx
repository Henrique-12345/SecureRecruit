import { FormEvent, useEffect, useState } from 'react'
import { api } from '../../../api/client'
import type { AttackExperiment } from '../../../types/cryptoLab'

type Tab = 'brute_force' | 'differential' | 'statistical'

export function CryptoAttacksPage() {
  const [tab, setTab] = useState<Tab>('differential')
  const [plaintext, setPlaintext] = useState('texto base para ataque diferencial')
  const [bits, setBits] = useState(10)
  const [result, setResult] = useState<AttackExperiment | null>(null)
  const [history, setHistory] = useState<AttackExperiment[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function loadHistory() {
    const { data } = await api.get<AttackExperiment[]>('/crypto/attacks/experiments', {
      params: { limit: 20 },
    })
    setHistory(data)
  }

  useEffect(() => {
    void loadHistory().catch(() => undefined)
  }, [])

  async function onRun(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      let data: AttackExperiment
      if (tab === 'brute_force') {
        data = (
          await api.post<AttackExperiment>('/crypto/attacks/brute-force', {
            plaintext,
            searchable_bits: bits,
          })
        ).data
      } else if (tab === 'differential') {
        data = (
          await api.post<AttackExperiment>('/crypto/attacks/differential', {
            plaintext,
          })
        ).data
      } else {
        data = (
          await api.post<AttackExperiment>('/crypto/attacks/statistical', {
            plaintext,
          })
        ).data
      }
      setResult(data)
      await loadHistory()
    } catch {
      setError('Falha ao executar o ataque (admin only / lab SPN).')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Ataques controlados</h1>
        <p>Somente contra a cifra didática SPN, com limites de laboratório.</p>
      </div>

      <div className="actions">
        {(
          [
            ['differential', 'Diferencial'],
            ['brute_force', 'Força bruta'],
            ['statistical', 'Estatístico'],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`btn ${tab === id ? 'primary' : 'ghost'}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="panel">
        <form className="form" onSubmit={(e) => void onRun(e)}>
          <label>
            Plaintext
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} required />
          </label>
          {tab === 'brute_force' && (
            <label>
              Bits pesquisáveis (1–20)
              <input
                type="number"
                min={1}
                max={20}
                value={bits}
                onChange={(e) => setBits(Number(e.target.value))}
              />
            </label>
          )}
          <button className="btn primary" type="submit" disabled={busy}>
            Executar ataque
          </button>
        </form>
      </div>

      {result && (
        <div className="panel">
          <h3 className="section-title">Resultado</h3>
          <p>
            <span className="badge">{result.attack_type}</span>{' '}
            score={result.effectiveness_score?.toFixed(3)} — {result.result_summary}
          </p>
          <pre className="code-block">{JSON.stringify(result.metrics, null, 2)}</pre>
        </div>
      )}

      <div className="panel">
        <h3 className="section-title">Histórico recente</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Quando</th>
              <th>Tipo</th>
              <th>Score</th>
              <th>Resumo</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>{new Date(item.created_at).toLocaleString('pt-BR')}</td>
                <td>{item.attack_type}</td>
                <td>{item.effectiveness_score?.toFixed(3) ?? '—'}</td>
                <td>{item.result_summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
