import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { AnomalyEvent } from '../../types/cryptoLab'

export function AnomaliesPage() {
  const [items, setItems] = useState<AnomalyEvent[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [info, setInfo] = useState('')

  async function load() {
    const { data } = await api.get<AnomalyEvent[]>('/anomalies', { params: { limit: 50 } })
    setItems(data)
  }

  useEffect(() => {
    void load().catch(() => setError('Falha ao listar anomalias.'))
  }, [])

  async function runDetector() {
    setBusy(true)
    setError('')
    try {
      const { data } = await api.post<{ created_count: number }>('/anomalies/run', {
        hours: 24,
        auth_burst_threshold: 20,
      })
      setInfo(`Detector concluiu: ${data.created_count} nova(s) anomalia(s).`)
      await load()
    } catch {
      setError('Falha ao rodar o detector.')
    } finally {
      setBusy(false)
    }
  }

  async function resolve(id: string) {
    setBusy(true)
    try {
      await api.patch(`/anomalies/${id}/resolve`)
      await load()
    } catch {
      setError('Falha ao resolver anomalia.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Anomalias</h1>
        <p>Detector por regras + z-score (auth burst, decrypt fail, integridade, acessos, picos).</p>
        <div className="actions">
          <button className="btn primary" type="button" disabled={busy} onClick={() => void runDetector()}>
            Rodar detector
          </button>
        </div>
      </div>

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Quando</th>
              <th>Tipo</th>
              <th>Severidade</th>
              <th>Score</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{new Date(item.detected_at).toLocaleString('pt-BR')}</td>
                <td>{item.anomaly_type}</td>
                <td>
                  <span className={`badge ${item.severity === 'high' ? 'closed' : 'ok'}`}>
                    {item.severity}
                  </span>
                </td>
                <td>{item.score}</td>
                <td>{item.resolved ? 'resolvida' : 'aberta'}</td>
                <td>
                  {!item.resolved && (
                    <button
                      className="btn ghost"
                      type="button"
                      disabled={busy}
                      onClick={() => void resolve(item.id)}
                    >
                      Resolver
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {info && <p className="success">{info}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
