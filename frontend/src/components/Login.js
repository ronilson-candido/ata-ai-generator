import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.login(username, password);
      const user = await authService.getCurrentUser();
      onLogin(user);
      navigate('/dashboard');
    } catch (err) {
      setError('Usuário ou senha incorretos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="circuit-pattern"></div>
      </div>
      
      <div className="login-card cyber-border">
        <div className="login-header">
          <img src="/logo.svg" alt="Cyber Lab" className="login-logo" />
          <p className="subtitle">IA DE ATA DE REUNIÕES</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Usuário</label>
            <input
              type="text"
              id="username"
              className="cyber-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Digite seu usuário"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              className="cyber-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="cyber-button"
            disabled={loading}
          >
            {loading ? 'ACESSANDO...' : 'ACESSAR SISTEMA'}
          </button>
        </form>

        <div className="login-footer">
          <p>Não tem uma conta?</p>
          <Link to="/register" className="register-link">
            Criar Nova Conta
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
