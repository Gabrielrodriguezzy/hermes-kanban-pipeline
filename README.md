# Hermes Kanban Pipeline

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)

Automação de pipeline DevOps com **Hermes Agent** — orquestração de workers de IA, pipeline Kanban automatizada, monitoramento via Telegram e integração contínua.

Criado para transformar ideias em software funcional com o mínimo de intervenção manual.

---

## ⚙️ Visão Geral

```
🧠 Ideia → 🤖 Orquestrador → 📋 Kanban → ⚡ Workers → 📲 Telegram
```

O fluxo é:

1. Você dá uma ideia vaga ("quero um sistema de estoque")
2. O **Orquestrador** quebra em tasks e cria cards no Kanban
3. Workers especializados executam cada task em paralelo
4. **Pipeline automática** encadeia backend → frontend → deploy → healthcheck
5. **Telegram** notifica quando algo precisa de autorização ou trava

---

## 🧠 Perfis de Worker

| Perfil | Especialidade | Iterações | Testes | SOUL.md |
|--------|--------------|-----------|--------|---------|
| **Orquestrador** | Planejamento, decomposição, delegação | 12 | - | 31 linhas |
| **Rafael (Backend Sênior)** | APIs robustas, testes unitários | 20 | Sim | 31 linhas |
| **Manuel (Backend Rápido)** | Protótipos, MVPs | 5 | Não | ~30 linhas |
| **Felipe (Frontend Rápido)** | HTML/CSS/JS puro | 5 | Não | ~30 linhas |
| **Felipe (Frontend Sênior)** | React/Vue, Vitest | 25 | Sim | ~30 linhas |

### Como funciona a seleção

O orquestrador avalia o pedido e escolhe o perfil certo:

- **"Faz uma API de clientes"** → Backend Sênior (com testes)
- **"Testa essa ideia aqui"** → Backend Rápido (sem testes)
- **"Precisa de tela bonita"** → Frontend Sênior (React/Vue)
- **"Só uma tela rápida"** → Frontend Rápido (HTML puro)

---

## 🔄 Pipeline Automática

Quando uma task é concluída, a pipeline cria automaticamente a próxima:

```
Backend* concluído → Frontend: UI para {title}
Frontend* concluído → Deploy: {title}
Deploy concluído → Healthcheck: Validar {title}
```

**Script:** `kanban-pipeline.py` — roda como cron job, detecta mudanças e encadeia tasks.

---

## 📊 Dashboard Kanban

Dashboard web rodando localmente em **http://localhost:9119**.

![Dashboard Preview](docs/images/dashboard-preview.png)

---

## 📱 Monitoramento Telegram

Workers bloqueados ou com timeout disparam notificação no Telegram:

```
⏱ Frontend Rapido (Calculadora) atingiu o limite de iterações
Deseja aumentar e continuar? Responda:
  /autorizar t_xxx  →  liberar
  /ignorar t_xxx    →  descartar
```

**Comandos rápidos:**
- `/autorizar t_xxx` — libera task bloqueada
- `/ignorar t_xxx` — arquiva sem executar

---

## 🚀 Projetos Entregues

### Encurtador de URLs
API de encurtamento com FastAPI + SQLite async.
- 9 endpoints com validação
- Colisão de hash tratada (5 tentativas)
- 9/9 testes passando
- `projetos/encurtador-url/`

### Calculadora CLI
Calculadora simples com modo argumento e interativo.
- 62 linhas, sem dependências
- Operações: `+ - * / ** %`
- `calculadora.py`

---

## 📂 Estrutura do Repositório

```
hermes-kanban-pipeline/
├── README.md                    # Este arquivo
├── docs/
│   ├── architecture.md          # Arquitetura detalhada
│   ├── profiles.md              # Perfis de worker explicados
│   ├── kanban-guide.md          # Guia de uso do Kanban
│   └── images/                  # Screenshots e diagramas
├── scripts/
│   ├── kanban-pipeline.py       # Pipeline automática
│   ├── kanban-monitor.py        # Monitor Telegram
│   └── dash-watchdog.sh         # Watchdog do dashboard
├── projetos/
│   ├── encurtador-url/          # Projeto: encurtador de URL
│   └── calculadora.py           # Projeto: calculadora CLI
├── profiles/
│   ├── orquestrador/            # SOUL.md + config
│   ├── rafael-backend-senior/
│   ├── manuel-backend-rapido/
│   ├── frontend-rapido/
│   └── frontend-senior/
└── LICENSE
```

---

## 🛠 Stack

| Camada | Tecnologia |
|--------|-----------|
| Orquestração | Hermes Agent (Nous Research) |
| LLM | DeepSeek / OpenRouter |
| Board | Kanban local |
| Notificação | Telegram Bot API |
| Terminal | WSL (Windows Subsystem for Linux) |
| Otimização | Reasoning effort low, max_turns reduzidos |

---

## ⚡ Otimização de Tokens

Perfis foram enxutos ao máximo:

- **SOUL.md** < 31 linhas por perfil
- **max_turns** reduzido (5-25 dependendo do perfil)
- **reasoning_effort: low** sempre que possível
- **Pipeline** usa cron jobs sem agente (`no_agent=True`) — zero tokens

---

## 📄 Licença

MIT — use, modifique, compartilhe.
