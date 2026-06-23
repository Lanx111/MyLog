import { useState, useEffect, useRef, useCallback } from 'react';
import { uploadFile, del } from '../api';
import styles from './PostForm.module.css';

const TYPE_OPTIONS = [
  { value: 'work_log', label: '工作日志' },
  { value: 'study_log', label: '学习日志' },
  { value: 'daily_report', label: '日报' },
  { value: 'weekly_report', label: '周报' },
  { value: 'summary', label: '总结' },
];

const DRAFT_KEY = 'mylog_draft';

/** 格式化文件大小为可读字符串 */
function formatSize(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

export default function PostForm({ initial, onSubmit, onComplete, onCancel }) {
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

  // ── 文件上传状态 ──
  const imageInputRef = useRef(null);
  const attachmentInputRef = useRef(null);
  const [imagePreviews, setImagePreviews] = useState([]);   // { name, size, url }[]
  const [attachmentInfos, setAttachmentInfos] = useState([]); // { name, size }[]
  const imageFilesRef = useRef([]);    // File 对象
  const attachmentFilesRef = useRef([]); // File 对象
  const [existingAttachments, setExistingAttachments] = useState(
    initial?.attachments || []
  );
  const [deletingAttIds, setDeletingAttIds] = useState(new Set());
  const [uploadError, setUploadError] = useState('');

  // 选择图片
  const handleImageSelect = (e) => {
    const files = Array.from(e.target.files);
    const newPreviews = files.map((f) => ({
      name: f.name,
      size: f.size,
      url: URL.createObjectURL(f),
    }));
    setImagePreviews((prev) => [...prev, ...newPreviews]);
    imageFilesRef.current = [...imageFilesRef.current, ...files];
  };

  // 移除图片
  const handleRemoveImage = (index) => {
    URL.revokeObjectURL(imagePreviews[index].url);
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
    imageFilesRef.current = imageFilesRef.current.filter((_, i) => i !== index);
  };

  // 选择附件
  const handleAttachmentSelect = (e) => {
    const files = Array.from(e.target.files);
    setAttachmentInfos((prev) => [
      ...prev,
      ...files.map((f) => ({ name: f.name, size: f.size })),
    ]);
    attachmentFilesRef.current = [...attachmentFilesRef.current, ...files];
  };

  // 移除附件
  const handleRemoveAttachment = (index) => {
    setAttachmentInfos((prev) => prev.filter((_, i) => i !== index));
    attachmentFilesRef.current = attachmentFilesRef.current.filter((_, i) => i !== index);
  };

  // 删除已有附件（编辑模式）
  const handleDeleteExisting = async (attId) => {
    setDeletingAttIds((prev) => new Set([...prev, attId]));
    try {
      await del(`/api/attachments/${attId}`);
      setExistingAttachments((prev) => prev.filter((a) => a.id !== attId));
    } catch (e) {
      setUploadError('删除附件失败: ' + e.message);
    } finally {
      setDeletingAttIds((prev) => {
        const next = new Set(prev);
        next.delete(attId);
        return next;
      });
    }
  };

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

  useEffect(() => {
    const timer = setTimeout(autoSave, 2000);
    return () => clearTimeout(timer);
  }, [autoSave]);

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

  // 清理预览 URL
  useEffect(() => {
    return () => {
      imagePreviews.forEach((p) => URL.revokeObjectURL(p.url));
    };
  }, []);

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
    setUploadError('');

    const tags = tagsStr
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean);

    setSubmitting(true);
    try {
      // 1. 创建或更新日志，获取 post_id
      let postId;
      try {
        const result = await onSubmit({ title: title.trim(), content, post_type: postType, tags });
        postId = result?.id || initial?.id;
      } catch (err) {
        setUploadError('保存日志失败: ' + err.message);
        return;
      }
      if (!postId) {
        setUploadError('无法获取日志 ID，文件上传失败');
        return;
      }

      // 2. 上传新图片
      for (const file of imageFilesRef.current) {
        try {
          await uploadFile(`/api/posts/${postId}/attachments`, file);
        } catch (err) {
          setUploadError(`图片 ${file.name} 上传失败: ${err.message}`);
        }
      }

      // 3. 上传新附件
      for (const file of attachmentFilesRef.current) {
        try {
          await uploadFile(`/api/posts/${postId}/attachments`, file);
        } catch (err) {
          setUploadError(`附件 ${file.name} 上传失败: ${err.message}`);
        }
      }

      // 提交成功，清草稿
      localStorage.removeItem(DRAFT_KEY);
      savedDraft.current = false;
      // 通知父组件完成（关闭表单、刷新列表等）
      if (onComplete) onComplete();
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
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

      {/* ── 文件上传区域 ── */}
      <div className={styles.uploadSection}>
        {/* 已有附件（编辑模式） */}
        {existingAttachments.length > 0 && (
          <div className={styles.existingFiles}>
            <label>已有附件</label>
            <ul className={styles.fileList}>
              {existingAttachments.map((att) => (
                <li key={att.id} className={styles.fileItem}>
                  <span className={styles.fileIcon}>
                    {att.file_type === 'image' ? '🖼️' : '📄'}
                  </span>
                  <a
                    href={att.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.fileLink}
                  >
                    {att.filename}
                  </a>
                  <span className={styles.fileSize}>({formatSize(att.file_size)})</span>
                  <button
                    type="button"
                    className={`btn btn-sm btn-danger ${styles.deleteBtn}`}
                    onClick={() => handleDeleteExisting(att.id)}
                    disabled={deletingAttIds.has(att.id)}
                  >
                    {deletingAttIds.has(att.id) ? '删除中...' : '×'}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 图片上传 */}
        <div className="form-group">
          <label>图片</label>
          <input
            ref={imageInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            multiple
            onChange={handleImageSelect}
            className={styles.fileInput}
          />
          {imagePreviews.length > 0 && (
            <div className={styles.imageGrid}>
              {imagePreviews.map((img, i) => (
                <div key={i} className={styles.imageThumb}>
                  <img src={img.url} alt={img.name} />
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={() => handleRemoveImage(i)}
                    title="移除"
                  >
                    ×
                  </button>
                  <span className={styles.imageName}>{img.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 附件上传 */}
        <div className="form-group">
          <label>附件（支持 .md / .txt / .pdf / .doc / .docx / .xlsx / .zip）</label>
          <input
            ref={attachmentInputRef}
            type="file"
            accept=".md,.txt,.pdf,.doc,.docx,.xlsx,.zip"
            multiple
            onChange={handleAttachmentSelect}
            className={styles.fileInput}
          />
          {attachmentInfos.length > 0 && (
            <ul className={styles.fileList}>
              {attachmentInfos.map((f, i) => (
                <li key={i} className={styles.fileItem}>
                  <span className={styles.fileIcon}>📄</span>
                  <span className={styles.fileLink}>{f.name}</span>
                  <span className={styles.fileSize}>({formatSize(f.size)})</span>
                  <button
                    type="button"
                    className={`btn btn-sm btn-danger ${styles.deleteBtn}`}
                    onClick={() => handleRemoveAttachment(i)}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {uploadError && <div className={styles.uploadError}>{uploadError}</div>}

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
