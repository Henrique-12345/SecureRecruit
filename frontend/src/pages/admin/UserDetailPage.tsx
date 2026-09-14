import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../../api/client'
import type { User } from '../../types'

export function AdminUserDetailPage() {
  const { userId } = useParams()
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    if (!userId) return
    void api.get<User>(`/admin/users/${userId}`).then((res) => setUser(res.data))
  }, [userId])

  if (!user) return <div className="page-loading">Carregando...</div>

  return (
    <div className="stack">
      <div className="hero">
        <h1>{user.name}</h1>
        <p>{user.email}</p>
      </div>
      <div className="panel stack">
        <p>
          <strong>Papel:</strong> {user.role}
        </p>
        <p>
          <strong>CPF (fictício):</strong> {user.cpf}
        </p>
        <p>
          <strong>Telefone:</strong> {user.phone}
        </p>
        <p>
          <strong>Ativo:</strong> {user.is_active ? 'sim' : 'não'}
        </p>
        <p>
          <strong>Criado em:</strong> {new Date(user.created_at).toLocaleString('pt-BR')}
        </p>
      </div>
    </div>
  )
}
