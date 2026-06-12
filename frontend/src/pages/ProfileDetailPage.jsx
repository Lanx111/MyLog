import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { get } from '../api';
import PostCard from '../components/PostCard';
import styles from './ProfileDetailPage.module.css';

export default function ProfileDetailPage() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      get('/api/profiles'),
      get(`/api/posts?user_id=${userId}&limit=50`),
    ])
      .then(([profilesRes, postsRes]) => {
        const p = (profilesRes.data || []).find((p) => p.user_id === Number(userId));
        setProfile(p || null);
        setPosts(postsRes.data.items || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div className="loading">加载中...</div>;
  if (!profile) return <div className="empty-state"><h3>用户不存在</h3><Link to="/">返回首页</Link></div>;

  return (
    <div>
      <Link to="/" className={styles.back}>← 返回首页</Link>

      <div className="card">
        <div className={styles.profile}>
          <div className={styles.header}>
            {profile.avatar_url && (
              <img className={styles.avatar} src={profile.avatar_url} alt={profile.name} />
            )}
            <div>
              <h1 className={styles.name}>{profile.name || profile.username}</h1>
              <p className={styles.username}>@{profile.username}</p>
              {profile.title && <p className={styles.title}>{profile.title}</p>}
            </div>
          </div>

          {profile.bio && (
            <div className={styles.section}>
              <h3>个人简介</h3>
              <p>{profile.bio}</p>
            </div>
          )}

          {profile.skills && profile.skills.length > 0 && (
            <div className={styles.section}>
              <h3>技术方向</h3>
              <div className={styles.tags}>
                {profile.skills.map((s) => (
                  <span key={s} className="tag">{s}</span>
                ))}
              </div>
            </div>
          )}

          {profile.learning_goals && (
            <div className={styles.section}>
              <h3>学习目标</h3>
              <p>{profile.learning_goals}</p>
            </div>
          )}

          <div className={styles.section}>
            <h3>联系方式</h3>
            <div className={styles.contactGrid}>
              {profile.email && (
                <div className={styles.contactItem}>
                  <span className={styles.label}>邮箱</span>
                  <a href={`mailto:${profile.email}`}>{profile.email}</a>
                </div>
              )}
              {profile.github_url && (
                <div className={styles.contactItem}>
                  <span className={styles.label}>GitHub</span>
                  <a href={profile.github_url} target="_blank" rel="noopener noreferrer">
                    {profile.github_url}
                  </a>
                </div>
              )}
              {profile.blog_url && (
                <div className={styles.contactItem}>
                  <span className={styles.label}>博客</span>
                  <a href={profile.blog_url} target="_blank" rel="noopener noreferrer">
                    {profile.blog_url}
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 该用户的日志列表 */}
      <div className={styles.postsSection}>
        <h2 className={styles.postsTitle}>
          {profile.name || profile.username} 的日志
          <span className={styles.postCount}>{posts.length} 条</span>
        </h2>
        {posts.length === 0 ? (
          <div className="empty-state">
            <p>暂无日志</p>
          </div>
        ) : (
          posts.map((post) => <PostCard key={post.id} post={post} />)
        )}
      </div>
    </div>
  );
}
