import { useState, useEffect } from 'react';
import { get, del } from '../api';
import { useAuth } from '../AuthContext';
import styles from './AdminDashboard.module.css';

const TYPE_LABELS = {
  work_log: '工作日志',
  study_log: '学习日志',
  daily_report: '日报',
  weekly_report: '周报',
  summary: '总结',
};

export default function AdminDashboard() {
  const { user } = useAuth();
  const [tab, setTab] = useState('users'); // 'users' | 'posts'
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      get('/api/admin/users'),
      get('/api/posts?limit=100'),
    ])
      .then(([usersRes, postsRes]) => {
        setUsers(usersRes.data || []);
        setPosts(postsRes.data.items || []);
      })
      .catch((e) => {
        const msg = e?.message || e?.detail || JSON.stringify(e);
        setMessage('加载失败: ' + msg);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`确定删除用户 "${username}" 及其所有数据？此操作不可恢复！`)) return;
    try {
      await del(`/api/admin/users/${userId}`);
      showMessage(`已删除用户 ${username}`);
      setUsers(users.filter((u) => u.id !== userId));
      setPosts(posts.filter((p) => p.user_id !== userId));
    } catch (e) {
      showMessage('删除失败: ' + (e?.message || e?.detail || JSON.stringify(e)));
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('确定删除这条日志？')) return;
    try {
      await del(`/api/admin/posts/${postId}`);
      showMessage('日志已删除');
      setPosts(posts.filter((p) => p.id !== postId));
    } catch (e) {
      showMessage('删除失败: ' + (e?.message || e?.detail || JSON.stringify(e)));
    }
  };

  function formatDate(iso) {
    if (!iso) return '';
    return iso.slice(0, 16).replace('T', ' ');
  }

  if (loading) return <div className="loading">加载中...</div>;
  if (!user?.is_admin) {
    return <div className="empty-state"><h3>需要管理员权限</h3></div>;
  }

  const totalPosts = users.reduce((s, u) => s + (u.post_count || 0), 0);

  return (
    <div>
      {message && <div className={styles.toast}>{message}</div>}

      <div className={styles.tabs}>
        <button
          className={`btn btn-sm ${tab === 'users' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('users')}
        >
          用户管理 ({users.length})
        </button>
        <button
          className={`btn btn-sm ${tab === 'posts' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('posts')}
        >
          日志管理 ({posts.length})
        </button>
      </div>

      {/* ── 用户管理 ── */}
      {tab === 'users' && (
        <div>
          <div className={styles.header}>
            <h2>所有用户</h2>
            <span className={styles.subtitle}>
              共 {users.length} 个用户，{totalPosts} 条日志
            </span>
          </div>

          {users.map((u) => (
            <div key={u.id} className={`card ${styles.userCard}`}>
              <div className={styles.userInfo}>
                <div className={styles.userHeader}>
                  <strong className={styles.username}>
                    {u.profile?.name || u.username}
                    {u.is_admin && <span className={styles.adminBadge}>管理员</span>}
                  </strong>
                  <span className={styles.meta}>
                    @{u.username} · {u.profile?.title || '无职位'} · {u.post_count} 条日志
                  </span>
                </div>
                {u.profile?.bio && <p className={styles.bio}>{u.profile.bio}</p>}
                <div className={styles.userMeta}>
                  邮箱: {u.profile?.email || '-'} · GitHub: {u.profile?.github_url || '-'}
                </div>
              </div>
              <div className={styles.actions}>
                {u.id !== user.id && (
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDeleteUser(u.id, u.username)}
                  >
                    删除用户
                  </button>
                )}
              </div>
            </div>
          ))}

          {users.length === 0 && (
            <div className="empty-state"><h3>暂无用户</h3></div>
          )}
        </div>
      )}

      {/* ── 日志管理 ── */}
      {tab === 'posts' && (
        <div>
          <div className={styles.header}>
            <h2>所有日志</h2>
            <span className={styles.subtitle}>共 {posts.length} 条</span>
          </div>

          {posts.map((post) => (
            <div key={post.id} className={`card ${styles.postCard}`}>
              <div className={styles.postInfo}>
                <div className={styles.postHeader}>
                  <span className={`tag ${styles.typeTag}`}>
                    {TYPE_LABELS[post.post_type] || post.post_type}
                  </span>
                  <span className={styles.postAuthor}>@{post.author}</span>
                  <span className={styles.postDate}>{formatDate(post.created_at)}</span>
                </div>
                <strong className={styles.postTitle}>{post.title}</strong>
                <p className={styles.postContent}>
                  {post.content?.slice(0, 120)}
                  {post.content?.length > 120 ? '...' : ''}
                </p>
              </div>
              <div className={styles.actions}>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDeletePost(post.id)}
                >
                  删除
                </button>
              </div>
            </div>
          ))}

          {posts.length === 0 && (
            <div className="empty-state"><h3>暂无日志</h3></div>
          )}
        </div>
      )}
    </div>
  );
}
