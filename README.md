# Cyber Lab - Meeting Minutes AI

Sistema completo de transcrição e geração de atas de reunião com IA, incluindo:
- Backend FastAPI com autenticação JWT
- Frontend React moderno com design tecnológico
- Banco de dados PostgreSQL
- Sistema de usuários e histórico
- Dashboard administrativo

## 🚀 Tecnologias

### Backend
- FastAPI (Python)
- SQLAlchemy + PostgreSQL
- JWT Authentication
- OpenAI Whisper (transcrição)
- FFmpeg (processamento de áudio/vídeo)

### Frontend
- React 18
- React Router
- Axios
- CSS Moderno (Gradientes Cyber)

### Infraestrutura
- Docker & Docker Compose
- PostgreSQL 15

## 📋 Pré-requisitos

- Docker Desktop instalado e rodando
- Git (opcional)

## 🏃 Como Rodar

### Opção 1: Script automático (Windows)
```bash
start.bat
```

### Opção 2: Script automático (Linux/Mac)
```bash
chmod +x start.sh
./start.sh
```

### Opção 3: Manual
```bash
docker-compose up -d --build
```

### Acessar a aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Criar primeiro usuário

1. Acesse http://localhost:3000
2. Clique em "Criar Nova Conta"
3. Preencha os dados e registre-se

### Tornar usuário admin (opcional)

```bash
docker exec -it cyberlab_postgres psql -U cyber -d cyberlab -c "UPDATE users SET is_admin = true WHERE username = 'seu_usuario';"
```

## 👥 Funcionalidades

### Para Usuários
- ✅ Cadastro e login
- ✅ Upload de áudio/vídeo
- ✅ Transcrição automática com Whisper
- ✅ Geração de ata estruturada
- ✅ Histórico de atas geradas
- ✅ Download em Markdown
- ✅ Visualização detalhada

### Para Administradores
- ✅ Dashboard com estatísticas
- ✅ Gerenciamento de usuários
- ✅ Ativar/desativar usuários
- ✅ Visualizar todas as atas do sistema
- ✅ Métricas de uso

## 🎨 Interface

Interface moderna com:
- Tema dark com gradientes cyber (cyan + magenta)
- Fonte Orbitron para títulos
- Animações e efeitos glow
- Design responsivo
- Inspiração em engenharia da computação

## 🔐 Segurança

- Autenticação JWT
- Senhas hasheadas com bcrypt
- Proteção de rotas
- Validação de dados
- CORS configurado

## 📝 API Endpoints

### Autenticação
- `POST /api/auth/register` - Criar conta
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuário atual

### Atas
- `POST /api/minutes/upload` - Upload e processar
- `GET /api/minutes/` - Minhas atas
- `GET /api/minutes/{id}` - Detalhes da ata
- `DELETE /api/minutes/{id}` - Excluir ata

### Admin
- `GET /api/admin/dashboard` - Estatísticas
- `GET /api/admin/users` - Listar usuários
- `PUT /api/admin/users/{id}` - Atualizar usuário
- `DELETE /api/admin/users/{id}` - Excluir usuário

## 🐛 Troubleshooting

### Docker não inicia
```bash
docker-compose down
docker-compose up -d --build
```

### Erro no banco de dados
```bash
docker-compose down -v
docker-compose up -d
```

### Frontend não carrega
Verifique se o backend está rodando: http://localhost:8000/health

---

