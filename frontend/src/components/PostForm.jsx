import { useState } from 'react';
import styles from './PostForm.module.css';

const TYPE_OPTIONS = [
  { value: 'work_log', label: '工作日志' },
  { value: 'study_log', label: '学习日志' },
  { value: 'daily_report', label: '日报' },
  { value: 'weekly_report', label: '周报' },
  { value: 'summary', label: '总结' },
];

export default function PostForm({ initial, onSubmit, onCancel }) {
  const [title, setTitle] = useState(initial?.title || '');
  const [content, setContent] = useState(initial?.content || '');
  const [postType, setPostType] = useState(initial?.post_type || 'work_log');
  const [tagsStr, setTagsStr] = useState(
    (initial?.tags || []).join(', ')
  );
  const [submitting, setSubmitting] = useState(false);

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
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
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
          <button type="button" className="btn btn-outline" onClick={onCancel}>
            取消
          </button>
        )}
      </div>
    </form>
  );
}
