import { useState, useEffect } from 'react';
import { get } from '../api';
import styles from './ProfileCard.module.css';

export default function ProfileCard() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get('/api/profile')
      .then((res) => setProfile(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">加载中...</div>;
  if (!profile) return <div className="empty-state"><h3>暂无个人信息</h3></div>;

  return (
    <div className="card">
      <div className={styles.profile}>
        <div className={styles.header}>
          {profile.avatar_url && (
            <img className={styles.avatar} src={profile.avatar_url} alt={profile.name} />
          )}
          <div>
            <h1 className={styles.name}>{profile.name}</h1>
            <p className={styles.title}>{profile.title}</p>
          </div>
        </div>

        {profile.bio && <p className={styles.bio}>{profile.bio}</p>}

        {profile.skills && profile.skills.length > 0 && (
          <div className={styles.section}>
            <h3>技术方向</h3>
            <div>
              {profile.skills.map((s) => (
                <span key={s} className="tag">{s}</span>
              ))}
            </div>
          </div>
        )}

        {profile.learning_goals && (
          <div className={styles.section}>
            <h3>学习目标</h3>
            <p className={styles.goals}>{profile.learning_goals}</p>
          </div>
        )}

        <div className={styles.links}>
          {profile.github_url && (
            <a href={profile.github_url} target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
          )}
          {profile.blog_url && (
            <a href={profile.blog_url} target="_blank" rel="noopener noreferrer">
              博客
            </a>
          )}
          {profile.email && (
            <a href={`mailto:${profile.email}`}>邮箱</a>
          )}
        </div>
      </div>
    </div>
  );
}
