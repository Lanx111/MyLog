import { useState, useEffect } from 'react';
import { get, put, post, del } from '../api';
import PostForm from '../components/PostForm';
import styles from './AdminPage.module.css';

export default function AdminPage() {
  const [tab, setTab] = useState('posts'); // 'profile' | 'posts'
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [editingPost, setEditingPost] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  // profile form state
  const [profileForm, setProfileForm] = useState({
    name: '', title: '', bio: '', skillsStr: '',
    github_url: '', blog_url: '', email: '', learning_goals: '',
  });

  useEffect(() => {
    Promise.all([get('/api/profile'), get('/api/posts?limit=50')])
      .then(([profileRes, postsRes]) => {
        const p = profileRes.data;
        if (p) {
          setProfile(p);
          setProfileForm({
            name: p.name || '',
            title: p.title || '',
            bio: p.bio || '',
            skillsStr: (p.skills || []).join(', '),
            github_url: p.github_url || '',
            blog_url: p.blog_url || '',
            email: p.email || '',
            learning_goals: p.learning_goals || '',
          });
        }
        setPosts(postsRes.data.items);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleProfileSave = async (e) => {
    e.preventDefault();
    const skills = profileForm.skillsStr
      .split(/[,，]/)
      .map((s) => s.trim())
      .filter(Boolean);
    const body = {
      ...profileForm,
      skills,
    };
    delete body.skillsStr;
    try {
      const res = await put('/api/profile', body);
      setProfile(res.data);
      showMessage('个人信息已更新');
    } catch (e) {
      showMessage('保存失败');
    }
  };

  const handlePostCreate = async (data) => {
    try {
      await post('/api/posts', data);
      setShowForm(false);
      showMessage('日志已发布');
      // refetch
      const res = await get('/api/posts?limit=50');
      setPosts(res.data.items);
    } catch (e) {
      showMessage('发布失败');
    }
  };

  const handlePostUpdate = async (data) => {
    try {
      await put(`/api/posts/${editingPost.id}`, data);
      setEditingPost(null);
      showMessage('日志已更新');
      const res = await get('/api/posts?limit=50');
      setPosts(res.data.items);
    } catch (e) {
      showMessage('更新失败');
    }
  };

  const handlePostDelete = async (postId) => {
    if (!window.confirm('确定删除？')) return;
    try {
      await del(`/api/posts/${postId}`);
      showMessage('日志已删除');
      setPosts(posts.filter((p) => p.id !== postId));
    } catch (e) {
      showMessage('删除失败');
    }
  };

  if (loading) return <div className="loading">加载中...</div>;

  return (
    <div>
      {message && <div className={styles.toast}>{message}</div>}

      <div className={styles.tabs}>
        <button
          className={`btn btn-sm ${tab === 'posts' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('posts')}
        >
          日志管理
        </button>
        <button
          className={`btn btn-sm ${tab === 'profile' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setTab('profile')}
        >
          编辑资料
        </button>
      </div>

      {tab === 'profile' && (
        <div className="card">
          <h2 className={styles.sectionTitle}>编辑个人信息</h2>
          <form onSubmit={handleProfileSave}>
            <div className="form-group">
              <label>姓名</label>
              <input value={profileForm.name} onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>职位</label>
              <input value={profileForm.title} onChange={(e) => setProfileForm({ ...profileForm, title: e.target.value })} />
            </div>
            <div className="form-group">
              <label>个人简介</label>
              <textarea rows={3} value={profileForm.bio} onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })} />
            </div>
            <div className="form-group">
              <label>技能（逗号分隔）</label>
              <input value={profileForm.skillsStr} onChange={(e) => setProfileForm({ ...profileForm, skillsStr: e.target.value })} />
            </div>
            <div className="form-group">
              <label>GitHub URL</label>
              <input value={profileForm.github_url} onChange={(e) => setProfileForm({ ...profileForm, github_url: e.target.value })} />
            </div>
            <div className="form-group">
              <label>博客 URL</label>
              <input value={profileForm.blog_url} onChange={(e) => setProfileForm({ ...profileForm, blog_url: e.target.value })} />
            </div>
            <div className="form-group">
              <label>邮箱</label>
              <input value={profileForm.email} onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })} />
            </div>
            <div className="form-group">
              <label>学习目标</label>
              <textarea rows={2} value={profileForm.learning_goals} onChange={(e) => setProfileForm({ ...profileForm, learning_goals: e.target.value })} />
            </div>
            <button type="submit" className="btn btn-primary">保存</button>
          </form>
        </div>
      )}

      {tab === 'posts' && (
        <div>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>日志管理</h2>
            {!showForm && !editingPost && (
              <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}>
                + 写日志
              </button>
            )}
          </div>

          {(showForm || editingPost) && (
            <div className="card">
              <PostForm
                initial={editingPost}
                onSubmit={editingPost ? handlePostUpdate : handlePostCreate}
                onCancel={() => { setShowForm(false); setEditingPost(null); }}
              />
            </div>
          )}

          {posts.length === 0 ? (
            <div className="empty-state">
              <h3>暂无日志</h3>
              <p>点击"写日志"创建第一条内容</p>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className={`card ${styles.postItem}`}>
                <div className={styles.postInfo}>
                  <span className={styles.postTitle}>{post.title}</span>
                  <span className={styles.postMeta}>
                    {post.post_type} · {post.created_at?.slice(0, 10)}
                  </span>
                </div>
                <div className={styles.postActions}>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => { setEditingPost(post); setShowForm(false); }}
                  >
                    编辑
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handlePostDelete(post.id)}
                  >
                    删除
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
