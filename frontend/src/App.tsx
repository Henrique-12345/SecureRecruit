import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { AppLayout } from './components/AppLayout'
import { HomePage } from './pages/JobsPage'
import { JobsListPage } from './pages/JobsListPage'
import { JobDetailPage } from './pages/JobDetailPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { CandidateDashboard } from './pages/candidate/Dashboard'
import { CandidateProfilePage } from './pages/candidate/ProfilePage'
import { CandidateResumesPage } from './pages/candidate/ResumesPage'
import { CandidateApplicationsPage } from './pages/candidate/ApplicationsPage'
import { CandidateApplicationDetailPage } from './pages/candidate/ApplicationDetailPage'
import { CandidateAIPage } from './pages/candidate/AIPage'
import { RecruiterDashboard } from './pages/recruiter/Dashboard'
import { RecruiterJobsPage } from './pages/recruiter/JobsPage'
import { RecruiterJobCreatePage } from './pages/recruiter/JobCreatePage'
import { RecruiterJobEditPage } from './pages/recruiter/JobEditPage'
import { RecruiterApplicationsPage } from './pages/recruiter/ApplicationsPage'
import { RecruiterCandidatePage } from './pages/recruiter/CandidatePage'
import { RecruiterResumePage } from './pages/recruiter/ResumePage'
import { RecruiterAIPage } from './pages/recruiter/AIPage'
import { AdminDashboard } from './pages/admin/Dashboard'
import { AdminUsersPage } from './pages/admin/UsersPage'
import { AdminUserDetailPage } from './pages/admin/UserDetailPage'
import { AdminApplicationsPage } from './pages/admin/ApplicationsPage'
import { AdminLogsPage } from './pages/admin/LogsPage'
import { CryptoLabHome } from './pages/admin/crypto/CryptoLabHome'
import { CryptoEncryptPage } from './pages/admin/crypto/CryptoEncryptPage'
import { CryptoStegoPage } from './pages/admin/crypto/CryptoStegoPage'
import { CryptoAttacksPage } from './pages/admin/crypto/CryptoAttacksPage'
import { CryptoAvalanchePage } from './pages/admin/crypto/CryptoAvalanchePage'
import { SecurityDashboardPage } from './pages/admin/SecurityDashboardPage'
import { AnomaliesPage } from './pages/admin/AnomaliesPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/jobs" element={<JobsListPage />} />
        <Route path="/jobs/:jobId" element={<JobDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<ProtectedRoute roles={['candidate']} />}>
          <Route path="/candidate" element={<CandidateDashboard />} />
          <Route path="/candidate/profile" element={<CandidateProfilePage />} />
          <Route path="/candidate/resumes" element={<CandidateResumesPage />} />
          <Route path="/candidate/applications" element={<CandidateApplicationsPage />} />
          <Route
            path="/candidate/applications/:applicationId"
            element={<CandidateApplicationDetailPage />}
          />
          <Route path="/candidate/ai" element={<CandidateAIPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={['recruiter']} />}>
          <Route path="/recruiter" element={<RecruiterDashboard />} />
          <Route path="/recruiter/jobs" element={<RecruiterJobsPage />} />
          <Route path="/recruiter/jobs/new" element={<RecruiterJobCreatePage />} />
          <Route path="/recruiter/jobs/:jobId/edit" element={<RecruiterJobEditPage />} />
          <Route
            path="/recruiter/jobs/:jobId/applications"
            element={<RecruiterApplicationsPage />}
          />
          <Route path="/recruiter/candidates/:candidateId" element={<RecruiterCandidatePage />} />
          <Route path="/recruiter/resumes/:resumeId" element={<RecruiterResumePage />} />
          <Route path="/recruiter/ai" element={<RecruiterAIPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={['admin']} />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/users" element={<AdminUsersPage />} />
          <Route path="/admin/users/:userId" element={<AdminUserDetailPage />} />
          <Route path="/admin/applications" element={<AdminApplicationsPage />} />
          <Route path="/admin/logs" element={<AdminLogsPage />} />
          <Route path="/admin/crypto" element={<CryptoLabHome />} />
          <Route path="/admin/crypto/encrypt" element={<CryptoEncryptPage />} />
          <Route path="/admin/crypto/stego" element={<CryptoStegoPage />} />
          <Route path="/admin/crypto/attacks" element={<CryptoAttacksPage />} />
          <Route path="/admin/crypto/avalanche" element={<CryptoAvalanchePage />} />
          <Route path="/admin/security-dashboard" element={<SecurityDashboardPage />} />
          <Route path="/admin/anomalies" element={<AnomaliesPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
