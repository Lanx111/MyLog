import { Link } from 'react-router-dom';
import styles from './PostCard.module.css';

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

export default function PostCard({ post }) {
  return (
    <div className="card">
      <div className={styles.card}>
        <div className={styles.meta}>
          <span className={`tag ${styles.typeTag}`}>
            {TYPE_LABELS[post.post_type] || post.post_type}
          </span>
          <span className={styles.date}>{formatDate(post.created_at)}</span>
        </div>
        <Link to={`/posts/${post.id}`} className={styles.title}>
          {post.title}
        </Link>
        <p className={styles.preview}>
          {post.content?.slice(0, 150)}
          {post.content?.length > 150 ? '...' : ''}
        </p>
        {post.tags && post.tags.length > 0 && (
          <div className={styles.tags}>
            {post.tags.map((t) => (
              <span key={t} className="tag">{t}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
