import { useState, useEffect } from 'react';
import { get } from '../api';
import ProfileCard from '../components/ProfileCard';
import PostCard from '../components/PostCard';
import { Link } from 'react-router-dom';
import styles from './HomePage.module.css';

export default function HomePage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get('/api/posts?limit=5')
      .then((res) => setPosts(res.data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <ProfileCard />

      <div className={styles.sectionHeader}>
        <h2>近期日志</h2>
        <Link to="/posts" className="btn btn-outline btn-sm">查看全部</Link>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <h3>暂无日志</h3>
          <p>去管理页创建你的第一条日志吧</p>
        </div>
      ) : (
        posts.map((post) => <PostCard key={post.id} post={post} />)
      )}
    </div>
  );
}
