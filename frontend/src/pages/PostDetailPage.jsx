import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { get, del } from '../api';
import { useAuth } from '../AuthContext';
import styles from './PostDetailPage.module.css';

const TYPE_LABELS = {
  work_log: '工作日志',
  study_log: '学习日志',
  daily_report: '日报',
  weekly_report: '周报',
  summary: '总结',
};

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function PostDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get(`/api/posts/${id}`)
      .then((res) => setPost(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('确定要删除这条日志吗？')) return;
    try {
      await del(`/api/posts/${id}`);
      navigate('/admin');
    } catch (e) {
      alert('删除失败: ' + e.message);
    }
  };

  const isOwner = user && post && user.id === post.user_id;

  if (loading) return <div className="loading">加载中...</div>;
  if (!post) return <div className="empty-state"><h3>日志不存在</h3><Link to="/posts">返回列表</Link></div>;

  return (
    <div className="card">
      <div className={styles.detail}>
        <div className={styles.meta}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className={`tag ${styles.typeTag}`}>
              {TYPE_LABELS[post.post_type] || post.post_type}
            </span>
            <span className={styles.author}>@{post.author}</span>
          </div>
          <span className={styles.date}>{formatDate(post.created_at)}</span>
        </div>
        <h1 className={styles.title}>{post.title}</h1>
        <div className={styles.content}>{post.content}</div>
        {post.tags && post.tags.length > 0 && (
          <div className={styles.tags}>
            {post.tags.map((t) => (
              <span key={t} className="tag">{t}</span>
            ))}
          </div>
        )}
        <div className={styles.actions}>
          <Link to="/posts" className="btn btn-outline btn-sm">返回列表</Link>
          {isOwner && (
            <button className="btn btn-danger btn-sm" onClick={handleDelete}>删除</button>
          )}
        </div>
      </div>
    </div>
  );
}
