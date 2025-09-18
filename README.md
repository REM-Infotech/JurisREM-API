# JurisREM API

API REST para gerenciamento de processos jurídicos e CRM advocatício.

## Descrição

O JurisREM API é uma aplicação Flask que fornece endpoints RESTful para gerenciamento completo de processos jurídicos, incluindo:

- Gestão de clientes (pessoas físicas e jurídicas)
- Cadastro e controle de advogados
- Acompanhamento de processos jurídicos
- Sistema de andamentos processuais
- Dashboard com estatísticas e relatórios
- Autenticação JWT para segurança

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-CORS**: Configuração de CORS
- **Marshmallow**: Serialização de dados
- **SQLite**: Banco de dados (desenvolvimento)

## Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passos para Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/REM-Infotech/JurisREM-APi.git
cd JurisREM-APi
```

2. **Crie e ative um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Initialize o banco de dados:**
```bash
flask init-db
flask create-admin
```

6. **Execute a aplicação:**
```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## Estrutura do Projeto

```
JurisREM-APi/
├── app/
│   ├── __init__.py          # Factory da aplicação Flask
│   ├── models/              # Modelos do banco de dados
│   │   ├── __init__.py      # Modelo base
│   │   ├── usuario.py       # Modelo de usuário
│   │   ├── cliente.py       # Modelo de cliente
│   │   ├── advogado.py      # Modelo de advogado
│   │   └── processo.py      # Modelos de processo e andamento
│   ├── routes/              # Rotas da API
│   │   ├── auth.py          # Autenticação
│   │   ├── clientes.py      # Gestão de clientes
│   │   ├── advogados.py     # Gestão de advogados
│   │   ├── processos.py     # Gestão de processos
│   │   ├── dashboard.py     # Dashboard e relatórios
│   │   └── errors.py        # Tratamento de erros
│   ├── services/            # Serviços e regras de negócio
│   │   └── __init__.py      # Serviços de dashboard e relatórios
│   └── schemas/             # Schemas de validação
│       └── __init__.py      # Schemas Marshmallow
├── tests/                   # Testes automatizados
├── config.py               # Configurações da aplicação
├── app.py                  # Arquivo principal
└── requirements.txt        # Dependências Python
```

## Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login do usuário
- `POST /api/auth/registro` - Registro de novo usuário
- `GET /api/auth/perfil` - Obter perfil do usuário
- `PUT /api/auth/perfil` - Atualizar perfil do usuário

### Clientes
- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Criar cliente
- `GET /api/clientes/{id}` - Obter cliente específico
- `PUT /api/clientes/{id}` - Atualizar cliente
- `DELETE /api/clientes/{id}` - Excluir cliente

### Advogados
- `GET /api/advogados/` - Listar advogados
- `POST /api/advogados/` - Criar advogado
- `GET /api/advogados/{id}` - Obter advogado específico
- `PUT /api/advogados/{id}` - Atualizar advogado
- `DELETE /api/advogados/{id}` - Excluir advogado

### Processos
- `GET /api/processos/` - Listar processos
- `POST /api/processos/` - Criar processo
- `GET /api/processos/{id}` - Obter processo específico
- `PUT /api/processos/{id}` - Atualizar processo
- `GET /api/processos/{id}/andamentos` - Listar andamentos
- `POST /api/processos/{id}/andamentos` - Criar andamento

### Dashboard
- `GET /api/dashboard/estatisticas` - Estatísticas gerais
- `GET /api/dashboard/processos-recentes` - Processos recentes
- `GET /api/dashboard/advogados-produtividade` - Produtividade
- `POST /api/dashboard/relatorio-periodo` - Relatório por período
- `GET /api/dashboard/clientes-sem-processos` - Clientes sem processos

## Autenticação

A API utiliza autenticação JWT (JSON Web Tokens). Para acessar endpoints protegidos:

1. Faça login via `POST /api/auth/login`
2. Inclua o token no header: `Authorization: Bearer {token}`

## Comandos CLI

```bash
# Inicializar banco de dados
flask init-db

# Criar usuário administrador
flask create-admin

# Popular com dados de exemplo
flask seed-data
```

## Testes

Execute os testes automatizados:

```bash
pytest
```

## Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença CC0 1.0 Universal. Veja `LICENSE` para mais informações.

## Contato

REM Infotech - [GitHub](https://github.com/REM-Infotech)
