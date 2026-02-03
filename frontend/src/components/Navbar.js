import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          <img src="/logo.svg" alt="Cyber Lab" className="navbar-logo" />
        </Link>

        <div className="navbar-menu">
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
          <Link to="/live" className="nav-link">Reunião em Tempo Real</Link>
          <Link to="/upload" className="nav-link">Reunião Gravada</Link>
          <Link to="/history" className="nav-link">Histórico</Link>
          {user.is_admin && (
            <Link to="/admin" className="nav-link admin-link">Admin</Link>
          )}
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">{user.username}</span>
            {user.is_admin && <span className="admin-badge">ADMIN</span>}
          </div>
          <button onClick={onLogout} className="cyber-button-secondary btn-small">
            SAIR
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
