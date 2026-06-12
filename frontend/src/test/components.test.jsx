import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

// ═══════════════════════════════════════════════
//  测试 1：PostCard 组件 — 渲染日志卡片
// ═══════════════════════════════════════════════

import PostCard from '../components/PostCard';

describe('PostCard', () => {
  const mockPost = {
    id: 1,
    user_id: 1,
    author: 'lanxin',
    title: 'React Hooks 学习笔记',
    content: '学习了 useState 和 useEffect 的用法',
    post_type: 'study_log',
    tags: ['React', '前端'],
    created_at: '2026-06-12T10:00:00',
  };

  it('渲染标题', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    expect(screen.getByText('React Hooks 学习笔记')).toBeInTheDocument();
  });

  it('渲染作者名', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    expect(screen.getByText('@lanxin')).toBeInTheDocument();
  });

  it('渲染类型标签（中文）', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    expect(screen.getByText('学习日志')).toBeInTheDocument();
  });

  it('渲染标签', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('前端')).toBeInTheDocument();
  });

  it('点击标题跳转到详情页', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    const link = screen.getByText('React Hooks 学习笔记');
    expect(link.closest('a')).toHaveAttribute('href', '/posts/1');
  });

  it('点击作者跳转到用户详情', () => {
    render(
      <MemoryRouter>
        <PostCard post={mockPost} />
      </MemoryRouter>
    );
    const authorLink = screen.getByText('@lanxin');
    expect(authorLink.closest('a')).toHaveAttribute('href', '/profile/1');
  });

  it('预览截断超过 150 字的内容', () => {
    const longPost = {
      ...mockPost,
      content: 'A'.repeat(200),
    };
    render(
      <MemoryRouter>
        <PostCard post={longPost} />
      </MemoryRouter>
    );
    const preview = screen.getByText(/^A{150}\.{3}$/);
    expect(preview).toBeInTheDocument();
  });
});


// ═══════════════════════════════════════════════
//  测试 2：PostForm 组件 — 表单交互
// ═══════════════════════════════════════════════

import PostForm from '../components/PostForm';

describe('PostForm', () => {
  it('提交时调用 onSubmit 回调并传递表单数据', async () => {
    const onSubmit = vi.fn();  // 创建一个"假函数"来记录调用
    const user = userEvent.setup();

    render(<PostForm onSubmit={onSubmit} />);

    // 填写标题
    await user.type(screen.getByPlaceholderText('输入标题...'), '测试日志');

    // 填写内容
    await user.type(
      screen.getByPlaceholderText('写下你的内容...'),
      '这是一条测试日志的内容'
    );

    // 点击发布
    await user.click(screen.getByRole('button', { name: '发布' }));

    // 断言：onSubmit 被调用了一次，参数正确
    expect(onSubmit).toHaveBeenCalledTimes(1);

    // 获取调用时的参数
    const callArg = onSubmit.mock.calls[0][0];
    expect(callArg.title).toBe('测试日志');
    expect(callArg.content).toBe('这是一条测试日志的内容');
    expect(callArg.post_type).toBe('work_log');   // 默认类型
    expect(callArg.tags).toEqual([]);
  });

  it('标题为空时不允许提交', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();

    render(<PostForm onSubmit={onSubmit} />);

    // 不填标题，直接点发布
    const submitBtn = screen.getByRole('button', { name: '发布' });
    expect(submitBtn).toBeDisabled();

    // 即使尝试点击，onSubmit 也不应该被调用
    await user.click(submitBtn);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('编辑模式时按钮显示"更新"', () => {
    const initial = {
      title: '旧标题',
      content: '旧内容',
      post_type: 'study_log',
      tags: ['学习'],
    };

    render(<PostForm initial={initial} onSubmit={vi.fn()} />);

    // 表单应该预填了初始值
    expect(screen.getByDisplayValue('旧标题')).toBeInTheDocument();
    expect(screen.getByDisplayValue('旧内容')).toBeInTheDocument();
    // 按钮文字应该是"更新"
    expect(screen.getByRole('button', { name: '更新' })).toBeInTheDocument();
  });
});
