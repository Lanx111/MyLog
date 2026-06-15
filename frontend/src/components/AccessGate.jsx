import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { post } from '../api';

const STORAGE_KEY = 'mylog_access_token';

export default function AccessGate({ children }) {
  const [granted, setGranted] = useState(!!sessionStorage.getItem(STORAGE_KEY));
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [search] = useSearchParams();

  // URL 带 ?code=xxx 时自动验证
  useEffect(() => {
    if (granted) return;
    const urlCode = search.get('code');
    if (urlCode) {
      verify(urlCode);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const verify = async (inputCode) => {
    setLoading(true);
    setError('');
    try {
      const res = await post('/api/auth/access', { code: inputCode });
      sessionStorage.setItem(STORAGE_KEY, res.data.access_token);
      setGranted(true);
    } catch (e) {
      setError('访问码错误，请检查后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.trim()) verify(code.trim());
  };

  if (granted) return children;

  return (
    <div style={{ textAlign: 'center', padding: '80px 16px', maxWidth: 400, margin: '0 auto' }}>
      <h2 style={{ fontSize: '1.3rem', marginBottom: 8 }}>MyLog</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: 24, lineHeight: 1.7 }}>
        这是一个私密的成长日志空间，请输入访问码继续浏览。
      </p>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="请输入访问码"
          autoFocus
          style={{
            width: '100%', padding: '10px 14px', fontSize: '1rem',
            border: '1px solid var(--color-border)', borderRadius: 6,
            marginBottom: 12, boxSizing: 'border-box',
          }}
        />
        {error && (
          <p style={{ color: '#e74c3c', fontSize: '0.85rem', marginBottom: 8 }}>{error}</p>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !code.trim()}
          style={{ width: '100%' }}
        >
          {loading ? '验证中...' : '进入'}
        </button>
      </form>
    </div>
  );
}
