import { useSearchParams } from 'react-router-dom';
import { useAuth } from './AuthContext';

const ACCESS_KEY = 'mylog2026';

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const [search] = useSearchParams();
  const key = search.get('key');

  // 通过 ?key=xxx 链接访问 → 保存到 sessionStorage，本次会话有效
  if (key === ACCESS_KEY) {
    sessionStorage.setItem('mylog_access', '1');
  }

  const hasAccess = !!user || sessionStorage.getItem('mylog_access') === '1';

  if (loading) return <div className="loading">加载中...</div>;

  if (!hasAccess) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 16px', maxWidth: 500, margin: '0 auto' }}>
        <h2 style={{ fontSize: '1.3rem', marginBottom: 12 }}>MyLog</h2>
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: 16, lineHeight: 1.7 }}>
          这是一个私有的个人主页与成长日志系统，仅限团队成员访问。<br />
          如果你有访问权限，请使用团队分享的链接打开。
        </p>
        <a href="/login" className="btn btn-primary" style={{ marginRight: 8 }}>
          团队成员登录
        </a>
      </div>
    );
  }

  return children;
}

// 管理员权限检查（仅用于 admin 路由）
export function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="loading">加载中...</div>;
  if (!user) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <p>请先登录</p>
        <a href="/login" className="btn btn-primary btn-sm">登录</a>
      </div>
    );
  }
  return children;
}
