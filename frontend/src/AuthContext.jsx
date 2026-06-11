import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { setToken, clearToken, post, get } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore session from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('mylog_user');
    const savedToken = localStorage.getItem('mylog_token');
    if (saved && savedToken) {
      setUser(JSON.parse(saved));
      setToken(savedToken);
      // Verify token is still valid
      get('/api/auth/me').then(res => {
        if (res.code !== 0) { logout(); }
      }).catch(() => {});
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await post('/api/auth/login', { username, password });
    if (res.code !== 0) throw new Error(res.message || '登录失败');
    const { access_token, user: u } = res.data;
    setToken(access_token);
    setUser(u);
    localStorage.setItem('mylog_user', JSON.stringify(u));
    localStorage.setItem('mylog_token', access_token);
    return u;
  }, []);

  const register = useCallback(async (username, password) => {
    const res = await post('/api/auth/register', { username, password });
    if (res.code !== 0) throw new Error(res.message || '注册失败');
    const { access_token, user: u } = res.data;
    setToken(access_token);
    setUser(u);
    localStorage.setItem('mylog_user', JSON.stringify(u));
    localStorage.setItem('mylog_token', access_token);
    return u;
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    clearToken();
    localStorage.removeItem('mylog_user');
    localStorage.removeItem('mylog_token');
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
