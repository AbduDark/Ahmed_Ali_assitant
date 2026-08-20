import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './components/layout/DashboardLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import StudentsPage from './pages/StudentsPage';
import ConversationsPage from './pages/ConversationsPage';
import ConversationDetailPage from './pages/ConversationDetailPage';
import ReferencesPage from './pages/ReferencesPage';
import SubjectsPage from './pages/SubjectsPage';
import InstructionsPage from './pages/InstructionsPage';
import CorrectionsPage from './pages/CorrectionsPage';
import AnalyticsPage from './pages/AnalyticsPage';

function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="conversations" element={<ConversationsPage />} />
        <Route path="conversations/:id" element={<ConversationDetailPage />} />
        <Route path="references" element={<ReferencesPage />} />
        <Route path="subjects" element={<SubjectsPage />} />
        <Route path="instructions" element={<InstructionsPage />} />
        <Route path="corrections" element={<CorrectionsPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
