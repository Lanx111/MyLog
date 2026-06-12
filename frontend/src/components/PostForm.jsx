import { useState, useEffect, useRef, useCallback } from 'react';
import styles from './PostForm.module.css';

const TYPE_OPTIONS = [
  { value: 'work_log', label: '工作日志' },
  { value: 'study_log', label: '学习日志' },
  { value: 'daily_report', label: '日报' },
  { value: 'weekly_report', label: '周报' },
  { value: 'summary', label: '总结' },
];

const DRAFT_KEY = 'mylog_draft';

export default function PostForm({ initial, onSubmit, onCancel }) {
  // ── 检查是否有草稿 ──
  const savedDraft = useRef(null);
  if (!initial && savedDraft.current === null) {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      savedDraft.current = raw ? JSON.parse(raw) : false;
    } catch {
      savedDraft.current = false;
    }
  }

  const [title, setTitle] = useState(
    initial?.title || (savedDraft.current?.title ?? '')
  );
  const [content, setContent] = useState(
    initial?.content || (savedDraft.current?.content ?? '')
  );
  const [postType, setPostType] = useState(
    initial?.post_type || savedDraft.current?.post_type || 'work_log'
  );
  const [tagsStr, setTagsStr] = useState(
    (initial?.tags || savedDraft.current?.tags || []).join(', ')
  );
  const [submitting, setSubmitting] = useState(false);
  const [draftSaved, setDraftSaved] = useState(false);
  const [showRestore, setShowRestore] = useState(
    !initial && savedDraft.current && savedDraft.current !== false
  );

  // ── 自动保存草稿（2 秒防抖）──
  const autoSave = useCallback(() => {
    if (submitting) return;
    if (!title.trim() && !content.trim()) return;

    const draft = {
      title: title.trim(),
      content: content.trim(),
      post_type: postType,
      tags: tagsStr.split(/[,，]/).map(t => t.trim()).filter(Boolean),
      savedAt: new Date().toISOString(),
    };

    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    setDraftSaved(true);
    setTimeout(() => setDraftSaved(false), 2000);
  }, [title, content, postType, tagsStr, submitting]);

  // 内容变化后 2 秒自动保存
  useEffect(() => {
    const timer = setTimeout(autoSave, 2000);
    return () => clearTimeout(timer);
  }, [autoSave]);

  // 页面关闭前最后一次保存
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (!title.trim() && !content.trim()) return;
      localStorage.setItem(DRAFT_KEY, JSON.stringify({
        title: title.trim(),
        content: content.trim(),
        post_type: postType,
        tags: tagsStr.split(/[,，]/).map(t => t.trim()).filter(Boolean),
        savedAt: new Date().toISOString(),
      }));
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [title, content, postType, tagsStr]);

  // ── 恢复草稿 ──
  const handleRestore = () => {
    if (savedDraft.current && savedDraft.current !== false) {
      const d = savedDraft.current;
      setTitle(d.title || '');
      setContent(d.content || '');
      setPostType(d.post_type || 'work_log');
      setTagsStr((d.tags || []).join(', '));
    }
    setShowRestore(false);
  };

  const handleDiscardDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    savedDraft.current = false;
    setTitle('');
    setContent('');
    setTagsStr('');
    setShowRestore(false);
  };

  // ── 提交 ──
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    const tags = tagsStr
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean);

    setSubmitting(true);
    try {
      await onSubmit({ title: title.trim(), content, post_type: postType, tags });
      // 提交成功，清草稿
      localStorage.removeItem(DRAFT_KEY);
      savedDraft.current = false;
    } finally {
      setSubmitting(false);
    }
  };

  // ── 取消 ──
  const handleCancel = () => {
    // 保留草稿，不清除
    if (onCancel) onCancel();
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      {/* 草稿恢复提示 */}
      {showRestore && (
        <div className={styles.draftBanner}>
          <span>检测到未完成的草稿（{savedDraft.current?.savedAt?.slice(0,16)?.replace('T',' ')}）</span>
          <div className={styles.draftActions}>
            <button type="button" className="btn btn-primary btn-sm" onClick={handleRestore}>
              恢复
            </button>
            <button type="button" className="btn btn-outline btn-sm" onClick={handleDiscardDraft}>
              丢弃
            </button>
          </div>
        </div>
      )}

      <div className="form-group">
        <label>类型</label>
        <select value={postType} onChange={(e) => setPostType(e.target.value)}>
          {TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>标题 *</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="输入标题..."
          maxLength={300}
          required
        />
      </div>
      <div className="form-group">
        <label>内容</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="写下你的内容..."
          rows={8}
        />
      </div>
      <div className="form-group">
        <label>标签（用逗号分隔）</label>
        <input
          type="text"
          value={tagsStr}
          onChange={(e) => setTagsStr(e.target.value)}
          placeholder="如：React, 学习笔记, 日报"
        />
      </div>
      <div className={styles.actions}>
        <button type="submit" className="btn btn-primary" disabled={submitting || !title.trim()}>
          {submitting ? '保存中...' : initial ? '更新' : '发布'}
        </button>
        {onCancel && (
          <button type="button" className="btn btn-outline" onClick={handleCancel}>
            取消
          </button>
        )}
        {draftSaved && (
          <span className={styles.draftIndicator}>草稿已保存</span>
        )}
      </div>
    </form>
  );
}
