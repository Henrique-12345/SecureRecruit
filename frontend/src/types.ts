export type UserRole = 'candidate' | 'recruiter' | 'admin'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  cpf?: string | null
  phone?: string | null
  birth_date?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Job {
  id: string
  recruiter_id: string
  title: string
  description: string
  requirements: string
  location: string
  employment_type: string
  salary_range?: string | null
  status: 'open' | 'closed'
  created_at: string
  updated_at: string
}

export interface Resume {
  id: string
  candidate_id: string
  original_filename: string
  stored_filename: string
  content_type: string
  file_size: number
  sha256_hash: string
  uploaded_at: string
}

export interface Application {
  id: string
  candidate_id: string
  job_id: string
  resume_id: string
  status: string
  applied_at: string
  updated_at: string
  candidate_name?: string | null
  job_title?: string | null
  resume_filename?: string | null
}

export interface CandidateProfile {
  id: string
  user_id: string
  address?: string | null
  city?: string | null
  state?: string | null
  professional_summary?: string | null
  education?: string | null
  skills?: string | null
  experience?: string | null
  linkedin_url?: string | null
  created_at: string
  updated_at: string
}

export interface AIAnalysisResult {
  summary: string
  key_skills: string[]
  technologies: string[]
  relevant_experience: string[]
  strengths: string[]
  gaps: string[]
  compatibility_notes?: string | null
  compatibility_score?: number | null
}

export interface AIAnalysis {
  id: string
  resume_id: string
  job_id?: string | null
  analysis_text: string
  extracted_skills?: string | null
  compatibility_score?: number | null
  created_at: string
  result?: AIAnalysisResult | null
}

export interface SecurityLog {
  id: string
  user_id?: string | null
  event_type: string
  action: string
  resource?: string | null
  resource_id?: string | null
  ip_address?: string | null
  user_agent?: string | null
  success: boolean
  timestamp: string
  details?: string | null
}
