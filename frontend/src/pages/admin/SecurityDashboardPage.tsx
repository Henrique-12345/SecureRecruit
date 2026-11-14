import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type {
  AnalyticsSummary,
  AnalyticsTimeseries,
  AnomalyEvent,
  AttackExperiment,
} from '../../types/cryptoLab'

function BarChart({
  items,
  color = 'var(--accent)',
}: {
  items: Array<{ label: string; value: number }>
  color?: string
}) {
  const max = Math.max(1, ...items.map((i) => i.value))
  return (
    <div className="bar-chart">
      {items.map((item) => (
        <div key={item.label} className="bar-row">
          <span className="bar-label">{item.label}</span>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{ width: `${(item.value / max) * 100}%`, background: color }}
            />
          </div>
          <span className="bar-value">{item.value}</span>
        </div>
      ))}
    </div>
  )
}

export function SecurityDashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [series, setSeries] = useState<AnalyticsTimeseries | null>(null)
  const [attacks, setAttacks] = useState<AttackExperiment[]>([])
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([])
  const [error, setError] = useState('')
  const [seeding, setSeeding] = useState(false)

  async function load() {
    const [s, t, a, an] = await Promise.all([
      api.get<AnalyticsSummary>('/analytics/events/summary', { params: { hours: 24 } }),
      api.get<AnalyticsTimeseries>('/analytics/events/timeseries', {
        params: { hours: 24, bucket: 'hour' },
      }),
      api.get<AttackExperiment[]>('/crypto/attacks/experiments', { params: { limit: 10 } }),
      api.get<AnomalyEvent[]>('/anomalies', { params: { resolved: false, limit: 10 } }),
    ])
    setSummary(s.data)
    setSeries(t.data)
    setAttacks(a.data)
    setAnomalies(an.data)
  }

  useEffect(() => {
    void load().catch(() => setError('Não foi possível carregar o dashboard.'))
  }, [])

  async function seedVolume() {
    setSeeding(true)
    setError('')
    try {
      await api.post('/analytics/seed-load', {
        crypto_events: 1000,
        auth_failures: 80,
        attack_events: 20,
        hours_span: 24,
      })
      await api.post('/anomalies/run', { hours: 24, auth_burst_threshold: 20 })
      await load()
    } catch {
      setError('Falha ao gerar carga / anomalias.')
    } finally {
      setSeeding(false)
    }
  }

  const totals = summary?.totals
  const opBars = Object.entries(summary?.crypto_by_operation_type ?? {}).map(([label, value]) => ({
    label,
    value,
  }))
  const hourBars =
    series?.crypto_operations.slice(-12).map((p) => ({
      label: new Date(p.bucket).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
      value: p.count,
    })) ?? []

  const highAlerts = anomalies.filter((a) => a.severity === 'high')

  return (
    <div className="stack">
      <div className="hero">
        <h1>Dashboard de segurança</h1>
        <p>Visão consolidada do Crypto Lab: eventos, ataques e anomalias (24h).</p>
        <div className="actions">
          <button className="btn primary" type="button" disabled={seeding} onClick={() => void seedVolume()}>
            Gerar carga + rodar detector
          </button>
          <Link className="btn ghost" to="/admin/crypto">
            Crypto Lab
          </Link>
          <Link className="btn ghost" to="/admin/anomalies">
            Anomalias
          </Link>
        </div>
      </div>

      {totals && (
        <div className="kpi-grid">
          <div className="panel kpi">
            <span className="kpi-label">Eventos crypto</span>
            <strong className="kpi-value">{totals.crypto_operations}</strong>
          </div>
          <div className="panel kpi">
            <span className="kpi-label">Falhas auth</span>
            <strong className="kpi-value">{totals.auth_failures}</strong>
          </div>
          <div className="panel kpi">
            <span className="kpi-label">Falhas crypto</span>
            <strong className="kpi-value">{totals.crypto_failures}</strong>
          </div>
          <div className="panel kpi">
            <span className="kpi-label">Anomalias abertas</span>
            <strong className="kpi-value">{anomalies.length}</strong>
          </div>
        </div>
      )}

      <div className="grid two">
        <div className="panel">
          <h3 className="section-title">Série temporal (crypto / hora)</h3>
          {hourBars.length ? (
            <BarChart items={hourBars} />
          ) : (
            <p className="muted">Sem dados na janela.</p>
          )}
        </div>
        <div className="panel">
          <h3 className="section-title">Operações por tipo</h3>
          {opBars.length ? (
            <BarChart items={opBars} color="var(--accent-2)" />
          ) : (
            <p className="muted">Sem operações agregadas.</p>
          )}
        </div>
      </div>

      <div className="panel">
        <h3 className="section-title">Alertas high (não resolvidos)</h3>
        {highAlerts.length === 0 ? (
          <p className="muted">Nenhum alerta high aberto.</p>
        ) : (
          <ul className="alert-list">
            {highAlerts.map((a) => (
              <li key={a.id}>
                <span className="badge closed">{a.severity}</span> {a.anomaly_type} · score=
                {a.score}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="panel">
        <h3 className="section-title">Últimos experimentos de ataque</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Quando</th>
              <th>Tipo</th>
              <th>Eficácia</th>
              <th>Resumo</th>
            </tr>
          </thead>
          <tbody>
            {attacks.map((item) => (
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
