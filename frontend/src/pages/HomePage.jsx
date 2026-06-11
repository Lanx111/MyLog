import { useState, useEffect } from 'react';
import { get } from '../api';
import PostCard from '../components/PostCard';
import { Link, useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';

export default function HomePage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('members'); // 'members' | 'posts'
  const [profiles, setProfiles] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      get('/api/profiles'),
      get('/api/posts?limit=20'),
    ])
      .then(([profilesRes, postsRes]) => {
        setProfiles(profilesRes.data || []);
        setPosts(postsRes.data.items || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">加载中...</div>;

  return (
    <div>
      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`btn btn-sm ${tab === 'members' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('members')}
        >
          成员 ({profiles.length})
        </button>
        <button
          className={`btn btn-sm ${tab === 'posts' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('posts')}
        >
          日志 ({posts.length})
        </button>
      </div>

      {/* ── 成员列表 ── */}
      {tab === 'members' && (
        <div className={styles.memberGrid}>
          {profiles.length === 0 ? (
            <div className="empty-state">
              <h3>还没有用户</h3>
              <p>注册成为第一个用户吧</p>
            </div>
          ) : (
            profiles.map((profile) => (
              <div
                key={profile.id}
                className={`card ${styles.memberCard}`}
                onClick={() => navigate(`/profile/${profile.user_id}`)}
              >
                <div className={styles.memberHeader}>
                  {profile.avatar_url ? (
                    <img src={profile.avatar_url} alt="" className={styles.avatar} />
                  ) : (
                    <div className={styles.avatarPlaceholder}>
                      {(profile.name || profile.username)[0]}
                    </div>
                  )}
                  <div className={styles.memberInfo}>
                    <strong className={styles.memberName}>
                      {profile.name || profile.username}
                    </strong>
                    <span className={styles.memberTitle}>
                      {profile.title || '@' + profile.username}
                    </span>
                  </div>
                </div>
                {profile.bio && (
                  <p className={styles.memberBio}>
                    {profile.bio.slice(0, 60)}
                    {profile.bio.length > 60 ? '...' : ''}
                  </p>
                )}
                {profile.skills && profile.skills.length > 0 && (
                  <div className={styles.memberSkills}>
                    {profile.skills.slice(0, 4).map((s) => (
                      <span key={s} className="tag">{s}</span>
                    ))}
                    {profile.skills.length > 4 && (
                      <span className={styles.moreTag}>+{profile.skills.length - 4}</span>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* ── 日志列表 ── */}
      {tab === 'posts' && (
        <div>
          <div className={styles.sectionHeader}>
            <h2>近期日志</h2>
            <Link to="/posts" className="btn btn-outline btn-sm">筛选搜索</Link>
          </div>

          {posts.length === 0 ? (
            <div className="empty-state">
              <h3>暂无日志</h3>
              <p>登录后去管理页创建你的第一条日志吧</p>
            </div>
          ) : (
            posts.map((post) => <PostCard key={post.id} post={post} />)
          )}
        </div>
      )}
    </div>
  );
}
