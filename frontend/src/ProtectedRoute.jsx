import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

// 需要登录才能访问的路由（写作、个人管理）
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading">加载中...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// 管理员路由 — 必须登录且为管理员
export function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading">加载中...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!user.is_admin) {
    return <Navigate to="/" replace />;
  }

  return children;
}
