import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import ProtectedRoute, { AdminRoute } from './ProtectedRoute';
import AccessGate from './components/AccessGate';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import PostListPage from './pages/PostListPage';
import PostDetailPage from './pages/PostDetailPage';
import AdminPage from './pages/AdminPage';
import AdminDashboard from './pages/AdminDashboard';
import ProfileDetailPage from './pages/ProfileDetailPage';
import LoginPage from './pages/LoginPage';

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <main className="app-main">
        <Routes>
          {/* 公开：登录 */}
          <Route path="/login" element={<LoginPage />} />

          {/* 浏览页面：需要访问码（通过分享链接 ?code=xxx 或手动输入） */}
          <Route path="/" element={<AccessGate><HomePage /></AccessGate>} />
          <Route path="/posts" element={<AccessGate><PostListPage /></AccessGate>} />
          <Route path="/posts/:id" element={<AccessGate><PostDetailPage /></AccessGate>} />
          <Route path="/profile/:userId" element={<AccessGate><ProfileDetailPage /></AccessGate>} />

          {/* 写作/管理页面：必须登录 */}
          <Route path="/admin" element={
            <ProtectedRoute><AdminPage /></ProtectedRoute>
          } />
          <Route path="/admin-dashboard" element={
            <AdminRoute><AdminDashboard /></AdminRoute>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </AuthProvider>
  );
}
