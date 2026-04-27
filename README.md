<div align="center">
  <img width="558" height="447" alt="nexus-logo" src="https://github.com/user-attachments/assets/ea53e544-21cc-45a1-8b98-e6d2395cd7fb" />
</div>

# Nexus-Tracker

API para gerenciamento de chamados (incidents), permitindo que usuários registrem ocorrências relacionadas a produtos e que técnicos realizem o atendimento, acompanhamento e resolução desses chamados.

---

##  Arquitetura

A aplicação segue uma arquitetura baseada em serviços containerizados:

```
Cliente (Frontend)
        ↓
     Nginx (Proxy Reverso)
        ↓
     FastAPI (Backend)
        ↓
     Banco de Dados
```

* **Nginx** atua como proxy reverso, centralizando requisições e tratamento de erros.
* **FastAPI** fornece a API principal.
* **Docker** garante isolamento e comunicação entre serviços.

---

##  Funcionalidades

* Registro e gerenciamento de chamados
* Autenticação baseada em cookies HttpOnly
* Controle de acesso por tipo de usuário (usuário, técnico, supervisor)
* Histórico detalhado de chamados
* Métricas de desempenho por técnico
* Geração de gráficos analíticos

---

##  Tecnologias Utilizadas

| Tecnologia           | Descrição                                  |
| :------------------- | :----------------------------------------- |
| **Python (FastAPI)** | Framework principal para construção da API |
| **SQLAlchemy**       | ORM para manipulação do banco de dados     |
| **Alembic**          | Controle de migrações do banco             |
| **Argon2**           | Hash seguro de senhas                      |
| **Pandas**           | Processamento de dados para métricas       |
| **Matplotlib**       | Geração de gráficos                        |
| **Pytest**           | Testes automatizados                       |
| **Nginx**            | Proxy reverso                              |
| **Docker**           | Containerização da aplicação               |

---

##  Autenticação

A autenticação é baseada em **cookies HttpOnly**, garantindo maior segurança contra ataques XSS.

### Fluxo:

1. Usuário realiza login
2. Backend retorna cookie seguro
3. Requisições subsequentes utilizam o cookie automaticamente

---

##  Endpoints

###  Monitoring

* `GET /api/v1/health`
  Verifica a saúde da aplicação e conexão com o banco.

---

###  Users

* `POST /api/v1/users` → Criação de usuário
* `POST /api/v1/login` → Autenticação
* `POST /api/v1/logout` → Logout
* `GET /api/v1/user_incidents` → Lista chamados do usuário autenticado
* `POST /api/v1/users/disable` → Desativa a própria conta

---

###  Incidents

* `POST /api/v1/incidents` → Criação de chamado
* `GET /api/v1/incidents` → Busca com filtros (status, data, prioridade, etc.)
* `GET /api/v1/incidents/history/{id_incident}` → Histórico de um chamado
* `DELETE /api/v1/incidents/{id_incident}` → Exclusão de chamado

---

###  Technicians

* `PUT /api/v1/incident/{id_incident}` → Resolver chamado
* `GET /api/v1/tech/history_incident` → Histórico de atendimentos
* `GET /api/v1/metrics/me` → Métricas e gráficos
* `GET /api/v1/users/{id_user}` → Buscar usuário (Supervisor)
* `PUT /api/v1/disable/user/or/worker/{id_user}` → Desativar contas (Supervisor)

---

##  Métricas

O sistema gera métricas baseadas nos chamados resolvidos pelos técnicos, incluindo:

* Quantidade de chamados resolvidos
* Visualização em gráfico (gerado via Matplotlib)

---

##  Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=sua_url_do_banco
SECRET_KEY=sua_chave
```

---

##  Como Executar

### Pré-requisitos

* Docker
* Docker Compose

### Passos

1. Clone o repositório:

```bash
git clone https://github.com/vitorhugo8899o-lgtm/Incident-Tracker-with-FastAPI
```

2. Acesse a pasta do projeto:

```bash
cd Incident-Tracker-with-FastAPI
```

3. Suba os containers:

```bash
docker compose up --build
```

---

###  Acesso

* API: http://localhost
* Documentação Swagger: http://localhost/docs

---

##  Frontend

O frontend está disponível em:

https://github.com/vitorhugo8899o-lgtm/WEB-IncidentTracker

### Executar frontend:

```bash
npm install
npm run dev
```

---

##  Observações

* A API segue padrão REST
* Estrutura modular para escalabilidade
* Preparada para deploy com Docker + Nginx

---
