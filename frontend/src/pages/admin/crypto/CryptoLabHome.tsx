import { Link } from 'react-router-dom'

const links = [
  {
    to: '/admin/crypto/encrypt',
    title: 'Cifrar / Decifrar',
    desc: 'SPN didático e AES-256-GCM com chave dinâmica.',
  },
  {
    to: '/admin/crypto/stego',
    title: 'Esteganografia',
    desc: 'Ocultar payload cifrado em PNG via LSB.',
  },
  {
    to: '/admin/crypto/attacks',
    title: 'Ataques controlados',
    desc: 'Força bruta truncada, diferencial e estatístico.',
  },
  {
    to: '/admin/crypto/avalanche',
    title: 'Avalanche & métricas',
    desc: 'Difusão e análise estatística do ciphertext.',
  },
  {
    to: '/admin/security-dashboard',
    title: 'Dashboard de segurança',
    desc: 'KPIs, séries e alertas consolidados.',
  },
  {
    to: '/admin/anomalies',
    title: 'Anomalias',
    desc: 'Rodar detector e resolver alertas.',
  },
]

export function CryptoLabHome() {
  return (
    <div className="stack">
      <div className="hero">
        <h1>Crypto Lab</h1>
        <p>
          Laboratório acadêmico da Unidade 2: cifra, stego, ataques, métricas e anomalias.
          Acesso exclusivo de administrador.
        </p>
      </div>
      <div className="grid two">
        {links.map((item) => (
          <Link key={item.to} className="panel" to={item.to}>
            <h3>{item.title}</h3>
            <p className="muted">{item.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
