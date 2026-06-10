import { NavLink } from 'react-router-dom';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className="app-header">
      <span className="logo">MyLog</span>
      <nav>
        <NavLink to="/" end>首页</NavLink>
        <NavLink to="/posts">日志</NavLink>
        <NavLink to="/admin">管理</NavLink>
      </nav>
    </header>
  );
}
