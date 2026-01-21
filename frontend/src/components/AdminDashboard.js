import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { adminService } from '../services/api';
import './AdminDashboard.css';

function AdminDashboard({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashboardData, usersData] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getAllUsers()
      ]);
      setStats(dashboardData);
      setUsers(usersData);
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      await adminService.updateUser(userId, { is_active: !currentStatus });
      setUsers(users.map(u => 
        u.id === userId ? { ...u, is_active: !currentStatus } : u
      ));
    } catch (error) {
      alert('Erro ao atualizar usuário');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Tem certeza que deseja excluir este usuário?')) {
      try {
        await adminService.deleteUser(userId);
        setUsers(users.filter(u => u.id !== userId));
      } catch (error) {
        alert('Erro ao excluir usuário');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="admin-page">
        <Navbar user={user} onLogout={onLogout} />
        <div className="loading-state">
          <div className="cyber-loader"></div>
          <p>Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="admin-container">
        <div className="admin-header">
          <div className="admin-title-section">
            <img src="/logo.svg" alt="Cyber Lab" className="admin-logo" />
            <div>
              <h1 className="glow-text">PAINEL ADMINISTRATIVO</h1>
              <p className="subtitle">Gerenciamento de usuários e estatísticas do sistema</p>
            </div>
          </div>
          <div className="admin-badge-large">
            👑 ADMIN
          </div>
        </div>

        {stats && (
          <div className="admin-stats grid-4">
            <div className="stat-card-admin cyber-card animate-slide-up">
              <div className="stat-icon-admin">👥</div>
              <div className="stat-value-admin">{stats.user_stats.total_users}</div>
              <div className="stat-label-admin">Total de Usuários</div>
            </div>

            <div className="stat-card-admin cyber-card animate-slide-up" style={{animationDelay: '0.1s'}}>
              <div className="stat-icon-admin">✅</div>
              <div className="stat-value-admin">{stats.user_stats.active_users}</div>
              <div className="stat-label-admin">Usuários Ativos</div>
            </div>

            <div className="stat-card-admin cyber-card animate-slide-up" style={{animationDelay: '0.2s'}}>
              <div className="stat-icon-admin">📄</div>
              <div className="stat-value-admin">{stats.user_stats.total_minutes}</div>
              <div className="stat-label-admin">Atas Geradas</div>
            </div>

            <div className="stat-card-admin cyber-card animate-slide-up" style={{animationDelay: '0.3s'}}>
              <div className="stat-icon-admin">⏱️</div>
              <div className="stat-value-admin">{Math.round(stats.user_stats.total_processing_time / 60)}min</div>
              <div className="stat-label-admin">Tempo Total</div>
            </div>
          </div>
        )}

        <div className="admin-content">
          <div className="admin-tabs">
            <button
              className={`admin-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📊 VISÃO GERAL
            </button>
            <button
              className={`admin-tab-btn ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              👥 GERENCIAR USUÁRIOS
            </button>
          </div>

          {activeTab === 'overview' && stats ? (
            <div className="overview-section">
              <div className="recent-minutes-section cyber-card">
                <h2>📋 Atas Recentes do Sistema</h2>
                {stats.recent_minutes.length === 0 ? (
                  <p className="no-data">Nenhuma ata gerada ainda</p>
                ) : (
                  <div className="minutes-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Título</th>
                          <th>Usuário</th>
                          <th>Data</th>
                          <th>Duração</th>
                          <th>Proc.</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stats.recent_minutes.map(minute => (
                          <tr key={minute.id}>
                            <td className="title-cell">{minute.title}</td>
                            <td>{minute.user.username}</td>
                            <td>{formatDate(minute.created_at)}</td>
                            <td>{Math.round(minute.audio_duration)}s</td>
                            <td>{Math.round(minute.processing_time)}s</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="users-section cyber-card">
              <h2>👥 Gerenciamento de Usuários</h2>
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Usuário</th>
                      <th>Email</th>
                      <th>Nome</th>
                      <th>Cadastro</th>
                      <th>Status</th>
                      <th>Tipo</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.id}>
                        <td>{u.id}</td>
                        <td className="username-cell">{u.username}</td>
                        <td>{u.email}</td>
                        <td>{u.full_name || '-'}</td>
                        <td>{formatDate(u.created_at)}</td>
                        <td>
                          <span className={`status-badge ${u.is_active ? 'status-active' : 'status-inactive'}`}>
                            {u.is_active ? 'Ativo' : 'Inativo'}
                          </span>
                        </td>
                        <td>
                          {u.is_admin && <span className="admin-badge">ADMIN</span>}
                        </td>
                        <td className="actions-cell">
                          {u.id !== user.id && (
                            <>
                              <button
                                onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                className={`action-btn ${u.is_active ? 'btn-deactivate' : 'btn-activate'}`}
                                title={u.is_active ? 'Desativar' : 'Ativar'}
                              >
                                {u.is_active ? '🔒' : '🔓'}
                              </button>
                              <button
                                onClick={() => handleDeleteUser(u.id)}
                                className="action-btn btn-delete"
                                title="Excluir"
                              >
                                🗑️
                              </button>
                            </>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
