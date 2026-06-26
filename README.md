<p align="center">
  <img src="https://img.shields.io/badge/status-active-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/stack-Hermes%20Agent-22d3ee?style=for-the-badge" alt="Stack">
  <img src="https://img.shields.io/badge/ottimizado%20token-%E2%9C%94-34d399?style=for-the-badge" alt="Tokens">
</p>

<div align="center">
  <h1>Hermes Kanban Pipeline</h1>
  <p><strong>Orquestração autônoma de IA — Workers especializados + Pipeline automatizada + Monitoramento via Telegram</strong></p>
  <p>Transforme ideias em software funcional com o mínimo de intervenção manual.</p>
  <br>
  <a href="docs/architecture.html">📐 Arquitetura</a> ·
  <a href="docs/profiles.md">🧠 Perfis</a> ·
  <a href="docs/pipeline.md">🔄 Pipeline</a> ·
  <a href="docs/guide.md">📖 Guia</a>
</div>

---

## ✨ Destaques

| | |
|---|---|
| **🤖 5 Perfis de Worker** | Orquestrador · Backend Sênior · Backend Rápido · Frontend Sênior · Frontend Rápido |
| **⚡ Pipeline Automática** | Cron-driven: detecta conclusões e encadeia tasks (backend→frontend→deploy→healthcheck) |
| **📲 Monitor Telegram** | Notificações em tempo real + comandos `/autorizar` e `/ignorar` |
| **🔋 Token-Otimizado** | SOUL.md < 31 linhas, perfis com max_turns 5-25, cron `no_agent` = zero tokens |

---

## 🏗️ Visão Geral da Arquitetura

```
                    ┌──────────────┐
                    │    Usuário   │
                    │ CLI · Telegram│
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  ORQUESTRADOR│
                    │  (Planejador)│
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  Kanban   │ │ Pipeline │ │ Telegram │
       │  Board    │ │ Cron Job │ │  Monitor │
       └──────────┘ └──────────┘ └──────────┘
              │            │
              ▼            ▼
       ┌──────────────────────────┐
       │     AUTONOMOUS WORKERS   │
       │                          │
       │  Backend · Frontend ·    │
       │  Rapid · Senior · Deploy │
       └──────────────────────────┘
```

> 📐 [Abra o diagrama de arquitetura interativo](docs/architecture.html) para uma visualização completa e detalhada.

---

## 🧠 Perfis de Worker

| Perfil | Nome | Especialidade | Iterações | Testes | Stack |
|--------|------|---------------|:---------:|:------:|-------|
| **🎯 Orquestrador** | — | Planejamento, decomposição, delegação | 12 | — | Hermes Agent |
| **👨‍💻 Backend Sênior** | Rafael | APIs robustas, código limpo | 20 | ✅ Unit. | Python · FastAPI |
| **⚡ Backend Rápido** | Manuel | Protótipos, MVPs, validar ideias | 5 | ❌ | Python puro |
| **🎨 Frontend Rápido** | Felipe | Telas simples, HTML/CSS puro | 5 | ❌ | HTML · CSS · JS |
| **🏗️ Frontend Sênior** | Felipe | Apps completas com framework | 25 | ✅ Vitest | React · Vue · Tailwind |

Cada perfil possui seu próprio **config.yaml** (modelo, limites) e **SOUL.md** (instruções de personalidade). Os arquivos estão em [`profiles/`](profiles/).

---

## 🔄 Pipeline Automática

A pipeline roda como cron job (`* * * * *`) e orquestra o fluxo completo:

```
Backend concluído   →   Frontend: "UI para {title}"
Frontend concluído  →   Deploy: "{title}"
Deploy concluído    →   Healthcheck: "Validar {title}"
```

**Scripts:**

| Arquivo | Função |
|---------|--------|
| [`scripts/kanban-pipeline.py`](scripts/kanban-pipeline.py) | Pipeline principal — detecta conclusões, encadeia tasks |
| [`scripts/kanban-monitor.py`](scripts/kanban-monitor.py) | Monitor Telegram — detecta travamentos, notifica |

> Ambos operam em modo `no_agent` — **zero consumo de tokens** por execução.

---

## 📱 Monitoramento em Tempo Real

Workers que atingem o limite de iterações disparam notificação no Telegram:

```
⏱ Frontend Rapido (Calculadora) atingiu o limite de iterações
Deseja aumentar e continuar?

/autorizar t_xxx  →  liberar task
/ignorar t_xxx    →  arquivar task sem execução
```

**Funciona 100% off — sem precisar abrir terminal.**

---

## 📦 Projetos Entregues

### 🔗 URL Shortener API
`projetos/encurtador-url/`

API REST de encurtamento de URLs com **FastAPI + SQLite async**.

- 9 endpoints com validação completa
- Tratamento de colisão de hash (5 tentativas)
- **9/9 testes passando**
- Código modular: `main.py` + `database.py` + `models.py`

### 🧮 Calculator CLI
`projetos/calculadora.py`

Calculadora minimalista com dois modos de operação.

- **62 linhas**, zero dependências
- Modo argumento: `calculadora.py 2 + 3`
- Modo interativo: `calculadora.py`
- Operações: `+ - * / ** %`

---

## ⚡ Otimização de Tokens

Um dos pilares do projeto. Cada perfil foi espremido ao máximo:

| Técnica | Detalhe |
|---------|---------|
| SOUL.md enxuto | Máximo **31 linhas** por perfil |
| max_turns reduzido | 5 (rápido) a 25 (sênior) |
| reasoning_effort | `low` sempre que possível |
| Cron no_agent | Pipeline e monitor rodam sem LLM |
| DeepSeek cache hit | 96-100% em prompts reutilizados |

---

## 🛠️ Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| **Orquestração** | Hermes Agent (Nous Research) |
| **LLM Principal** | DeepSeek via OpenRouter |
| **Board** | Kanban SQLite local |
| **Notificação** | Telegram Bot API |
| **Pipeline** | Python cron jobs |
| **Workers** | Perfis Hermes independentes |
| **Ambiente** | WSL (Windows Subsystem for Linux) |
| **Versionamento** | Git + GitHub |

---

## 🚀 Como Usar

```bash
# 1. Criar uma task
hermes kanban create "API de clientes" --body "CRUD completo com FastAPI"

# 2. O orquestrador planeja e delega automaticamente
# 3. Workers executam em paralelo
# 4. Pipeline encadeia backend → frontend → deploy
# 5. Você recebe notificações no Telegram

# Ver board
hermes kanban list

# Dashboard web
hermes dashboard --port 9119
```

---

## 📂 Estrutura do Repositório

```
📁 hermes-kanban-pipeline/
├── 📄 README.md                    ← Você está aqui
├── 📁 docs/
│   ├── 📄 architecture.html       ← Diagrama interativo da arquitetura
│   ├── 📄 profiles.md             ← Perfis de worker detalhados
│   ├── 📄 pipeline.md             ← Fluxo da pipeline
│   └── 📄 guide.md                ← Guia de uso
├── 📁 scripts/
│   ├── 🐍 kanban-pipeline.py      ← Pipeline automática
│   └── 🐍 kanban-monitor.py       ← Monitor Telegram
├── 📁 profiles/
│   ├── 📁 orquestrador/           ← SOUL.md + config.yaml
│   ├── 📁 rafael-backend-senior/  ← SOUL.md + config.yaml
│   ├── 📁 manuel-backend-rapido/  ← SOUL.md + config.yaml
│   ├── 📁 frontend-rapido/        ← SOUL.md
│   └── 📁 frontend-senior/        ← SOUL.md
├── 📁 projetos/
│   ├── 📁 encurtador-url/         ← FastAPI URL Shortener
│   └── 🐍 calculadora.py          ← CLI Calculator
└── 📄 LICENSE
```

---

## 👤 Sobre

Criado como portfólio de automação com IA, demonstrando:

- **Orquestração multi-agente** com perfis especializados
- **Pipeline DevOps autônoma** sem intervenção humana
- **Integração com mensageria** (Telegram) para supervisão remota
- **Otimização agressiva de custos** (tokens, iterações, reasoning)
- **Entrega de software funcional** : de ideia a código rodando

---

<p align="center">
  <sub>Feito com 🤖 · Hermes Agent · WSL · Python</sub>
</p>
