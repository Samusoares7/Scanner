# 🔐 Scanner
### Plataforma de Auditoria de Segurança Web

> Encontre brechas na sua infraestrutura antes que outros encontrem.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-brightgreen)
![Deploy](https://img.shields.io/badge/deploy-Render%20%2B%20Vercel-purple)

**🌐 Acesse agora:** [scanner-pro-beta.vercel.app](https://scanner-pro-beta.vercel.app)

---

## 📌 Sobre o Projeto

Scanner é uma ferramenta web de auditoria de segurança focada em ambientes próprios. Foi desenvolvida pensando em um problema real: desenvolvedores que constroem sistemas rapidamente muitas vezes com auxílio de IA e acabam deixando brechas de configuração que um atacante poderia explorar.

Diferente de ferramentas como Nmap, o Scanner não exige conhecimento técnico avançado. O resultado é apresentado em português, com contexto explicativo e classificação visual de risco tornando a auditoria de segurança acessível para qualquer desenvolvedor.

---

## 🎯 Problema que Resolve

Um desenvolvedor que sobe uma API para produção em um fim de semana provavelmente não sabe que:

- Deixou o Redis sem senha e acessível externamente
- O endpoint `/actuator` está exposto com dados da aplicação
- Não configurou nenhum header de segurança HTTP
- O painel `/admin` está acessível sem autenticação

O Scanner identifica essas brechas e explica o que cada uma significa — sem jargão técnico.

---

## ✨ Funcionalidades

- 🔍 **Varredura de portas TCP** com classificação de risco em três níveis: Critical, Attention e Common
- 🌐 **HTTP Checks** — verifica endpoints sensíveis expostos como `/.env`, `/admin`, `/.git`, `/actuator`
- 🛡️ **Análise de headers de segurança** — detecta ausência de HSTS, CSP, X-Frame-Options e outros
- 🔎 **Banner Grabbing** — identifica versão e tipo de serviço em portas abertas
- 🧱 **Detecção de WAF/CDN** — identifica Cloudflare, Sucuri, Akamai e sinaliza quando resultados podem ser mascarados
- ✅ **Baseline Comparison** — elimina falsos positivos de servidores com soft 404
- 📊 **Dashboard** — histórico de scans por alvo com distribuição de risco visual
- 📄 **Relatório PDF** — exporta resultado completo com sumário executivo e detalhamento por alvo
- 🔐 **Autenticação JWT** — acesso protegido por token
- 🗑️ **Limpar histórico** — apaga todos os scans com confirmação

---

## 🛠️ Stack Tecnológica

### Backend
| Tecnologia | Função |
|---|---|
| Python 3.10+ | Linguagem principal |
| FastAPI | Framework da API REST |
| SQLAlchemy | ORM para banco de dados |
| SQLite | Banco de dados local |
| JWT (python-jose) | Autenticação |
| Passlib + Bcrypt | Hash de senhas |
| ReportLab | Geração de PDF |
| Threading | Scan paralelo de portas |
| Socket | Conexões TCP |

### Frontend
| Tecnologia | Função |
|---|---|
| Vue.js 3 | Framework frontend |
| Vite | Build tool |
| Vue Router | Navegação entre páginas |
| Axios | Requisições HTTP |

### Deploy
| Plataforma | Serviço |
|---|---|
| Render | Backend FastAPI |
| Vercel | Frontend Vue.js |
| GitHub | Versionamento |

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.10+
- Node.js 22+
- Git

### Backend

```bash
# Clone o repositório
git clone https://github.com/Samusoares7/Scanner.git
cd Scanner/backend

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
python -m uvicorn app.main:app --reload
```

API disponível em: http://127.0.0.1:8000
Documentação: http://127.0.0.1:8000/docs

### Frontend

```bash
cd Scanner/frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

Frontend disponível em: http://localhost:5173

### Credenciais padrão
Usuário: admin
Senha:   admin123

---

## 📁 Estrutura do Projeto
```text
Scanner/
├── backend/
│   ├── app/
│   │   ├── main.py          # Entrada da aplicação + CORS
│   │   ├── database.py      # Configuração SQLite
│   │   ├── models.py        # ORM ScanResult
│   │   ├── auth.py          # JWT + autenticação
│   │   ├── pdf_report.py    # Geração de relatório PDF
│   │   ├── api/
│   │   │   └── routes.py    # Endpoints da API
│   │   ├── schemas/
│   │   │   └── scan_schema.py
│   │   └── scanner/
│   │       ├── scan.py      # Engine de varredura
│   │       ├── ports.py     # Dicionário de portas e HTTP checks
│   │       └── reports.py   # Formatação de resultados
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   └── HomeView.vue
│   │   ├── services/
│   │   │   └── api.js       # Comunicação com backend
│   │   ├── router/
│   │   │   └── index.js     # Rotas + proteção JWT
│   │   └── App.vue
│   └── package.json
└── README.md
```

---

## 🔌 Endpoints da API
| Método | Endpoint | Descrição | Auth |
|---|---|---|---|
| POST | /token | Login e geração de JWT | ❌ |
| POST | /scan | Executa varredura em um alvo | ✅ |
| GET | /scans | Retorna histórico de scans | ✅ |
| GET | /scans/{id} | Retorna scan específico | ✅ |
| DELETE | /scans | Limpa histórico | ✅ |
| GET | /report/pdf | Exporta relatório PDF | ✅ |

---

## ⚠️ Uso Responsável
Scanner-Pro foi desenvolvido para auditoria de ambientes próprios ou com autorização explícita do proprietário. A varredura de sistemas sem autorização é crime no Brasil Lei 12.737/2012 (Lei Carolina Dieckmann).
Use apenas em:
1. Servidores e infraestrutura própria
2. Ambientes de laboratório e estudo
3. Sistemas de terceiros com autorização por escrito

---

## 👨‍💻 Autor
**Samuel Soares**

- GitHub: [@Samusoares7](https://github.com/Samusoares7)
- LinkedIn: [samuele-soares](https://linkedin.com/in/samuele-soares)

---
