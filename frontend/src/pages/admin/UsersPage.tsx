import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { User } from '../../types'

export function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])

  const load = async () => {
    const { data } = await api.get<User[]>('/admin/users')
    setUsers(data)
  }

  useEffect(() => {
    void load()
  }, [])

  const toggle = async (user: User) => {
    await api.patch(`/admin/users/${user.id}/status`, { is_active: !user.is_active })
    await load()
  }

  return (
    <div className="stack">
      <div className="hero">
        <h1>Usuários</h1>
        <p>Contas fictícias do ambiente de demonstração.</p>
      </div>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Papel</th>
              <th>Ativo</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>
                  <Link to={`/admin/users/${u.id}`}>{u.name}</Link>
                </td>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>
                  <span className={`badge ${u.is_active ? 'ok' : 'closed'}`}>
                    {u.is_active ? 'sim' : 'não'}
                  </span>
                </td>
                <td>
                  <button className="btn ghost" type="button" onClick={() => void toggle(u)}>
                    {u.is_active ? 'Desativar' : 'Ativar'}
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
