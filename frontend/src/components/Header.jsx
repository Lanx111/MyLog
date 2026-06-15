import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="app-header">
      <span className="logo">MyLog</span>
      <nav>
        <NavLink to="/" end>首页</NavLink>
        <NavLink to="/posts">日志</NavLink>
        {user ? (
          <>
            {user.is_admin && <NavLink to="/admin-dashboard">管理面板</NavLink>}
            <NavLink to="/admin">我的</NavLink>
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', padding: '6px 0' }}>
              {user.username}
            </span>
            <button
              onClick={handleLogout}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '0.85rem', color: 'var(--color-text-secondary)',
                padding: '6px 0',
              }}
            >
              退出
            </button>
          </>
        ) : (
          <NavLink to="/login">登录</NavLink>
        )}
      </nav>
    </header>
  );
}
