export type CryptoAlgorithm = 'custom_spn' | 'aes-256-gcm'

export interface EncryptResponse {
  operation_id: string
  algorithm: string
  ciphertext_b64: string
  key_id: string | null
  key_fingerprint: string
  input_size: number
  output_size: number
  duration_ms: number | null
}

export interface DecryptResponse {
  operation_id: string
  algorithm: string
  plaintext: string
  key_id: string | null
  input_size: number
  output_size: number
  duration_ms: number | null
}

export interface StegoArtifact {
  id: string
  user_id: string
  payload_operation_id: string | null
  cover_original_filename: string
  stego_stored_filename: string
  capacity_bits: number
  payload_bits: number
  created_at: string
}

export interface AttackExperiment {
  id: string
  user_id: string | null
  attack_type: string
  algorithm: string
  parameters: Record<string, unknown> | null
  result_summary: string | null
  metrics: Record<string, unknown> | null
  effectiveness_score: number | null
  created_at: string
}

export interface AnomalyEvent {
  id: string
  anomaly_type: string
  severity: string
  score: number
  source_user_id: string | null
  evidence: Record<string, unknown> | null
  resolved: boolean
  detected_at: string
}

export interface AnalyticsSummary {
  window_hours: number
  since: string
  totals: {
    crypto_operations: number
    crypto_failures: number
    security_logs: number
    auth_failures: number
    attack_experiments: number
    stego_artifacts: number
    events_combined: number
  }
  crypto_by_operation_type: Record<string, number>
}

export interface AnalyticsTimeseries {
  window_hours: number
  bucket: string
  crypto_operations: Array<{ bucket: string; count: number }>
  auth_failures: Array<{ bucket: string; count: number }>
  attack_experiments: Array<{ bucket: string; count: number }>
}
