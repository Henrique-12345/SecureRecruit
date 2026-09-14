import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import type { SecurityLog } from '../../types'

export function AdminLogsPage() {
  const [logs, setLogs] = useState<SecurityLog[]>([])

  useEffect(() => {
    void api.get<SecurityLog[]>('/admin/logs', { params: { limit: 200 } }).then((res) => {
      setLogs(res.data)
    })
  }, [])

  return (
    <div className="stack">
      <div className="hero">
        <h1>Logs de segurança</h1>
        <p>Eventos de autenticação, autorização, upload, IA e administração.</p>
      </div>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Quando</th>
              <th>Ação</th>
              <th>Recurso</th>
              <th>Sucesso</th>
              <th>Detalhes</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleString('pt-BR')}</td>
                <td>{log.action}</td>
                <td>
                  {log.resource} {log.resource_id ? `#${log.resource_id.slice(0, 8)}` : ''}
                </td>
                <td>
                  <span className={`badge ${log.success ? 'ok' : 'closed'}`}>
                    {log.success ? 'ok' : 'falha'}
                  </span>
                </td>
                <td>{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
