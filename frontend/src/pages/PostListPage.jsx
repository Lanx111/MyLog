import { useState, useEffect, useCallback } from 'react';
import { get } from '../api';
import PostCard from '../components/PostCard';
import styles from './PostListPage.module.css';

const TYPE_OPTIONS = [
  { value: '', label: '全部' },
  { value: 'work_log', label: '工作日志' },
  { value: 'study_log', label: '学习日志' },
  { value: 'daily_report', label: '日报' },
  { value: 'weekly_report', label: '周报' },
  { value: 'summary', label: '总结' },
];

export default function PostListPage() {
  const [posts, setPosts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [postType, setPostType] = useState('');
  const [q, setQ] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [loading, setLoading] = useState(true);
  const limit = 10;

  const fetchPosts = useCallback(async (p, type, keyword) => {
    setLoading(true);
    const params = new URLSearchParams();
    params.set('page', p);
    params.set('limit', limit);
    if (type) params.set('post_type', type);
    if (keyword) params.set('q', keyword);

    try {
      const res = await get(`/api/posts?${params}`);
      setPosts(res.data.items);
      setTotal(res.data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPosts(page, postType, q);
  }, [page, postType, q, fetchPosts]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    setQ(searchInput);
  };

  const handleTypeChange = (type) => {
    setPostType(type);
    setPage(1);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <div className={styles.filters}>
        <div className={styles.types}>
          {TYPE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`btn btn-sm ${postType === opt.value ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => handleTypeChange(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <form className={styles.search} onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="搜索标题或内容..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-sm">搜索</button>
        </form>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <h3>没有找到日志</h3>
          <p>尝试更换筛选条件或搜索关键词</p>
        </div>
      ) : (
        <>
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}

          {totalPages > 1 && (
            <div className="pagination">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
                上一页
              </button>
              <span className="page-info">
                {page} / {totalPages}
              </span>
              <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
