# Arquitetura

## Visão Macro

```
┌─────────────────────────────────────────────────┐
│                   Usuário                        │
│  (CLI / Telegram)                               │
└────────┬────────────┬──────────────────┬────────┘
         │            │                  │
         ▼            ▼                  ▼
┌─────────────────┐ ┌──────────┐ ┌──────────────┐
│   Orquestrador  │ │  Kanban  │ │   Telegram    │
│  (Perfil IA)    │ │  Board   │ │   Monitor     │
└────────┬────────┘ └──────────┘ └──────────────┘
         │                 ▲
         ▼                 │
┌──────────────────────────┴──────────────┐
│            Workers (Perfis)              │
│                                          │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Backend │ │ Frontend │ │  Deploy  │ │
│  │ Sênior  │ │  Rápido  │ │ Pipeline │ │
│  └─────────┘ └──────────┘ └──────────┘ │
│  ┌─────────┐ ┌──────────┐              │
│  │ Backend │ │ Frontend │              │
│  │ Rápido  │ │  Sênior  │              │
│  └─────────┘ └──────────┘              │
└─────────────────────────────────────────┘
```

## Componentes

### 1. Hermes Agent (Core)

Agente de IA que orquestra todo o fluxo. Configurado via `~/.hermes/config.yaml`.

Características:
- Multi-provedor (DeepSeek como principal)
- Gateway para Telegram
- Cron jobs para pipeline
- Suporte a perfis com SOUL.md

### 2. Kanban Board

Board local SQLite que gerencia tasks e workers.

- **Dispatch:** distribui tasks para perfis automaticamente
- **Auto-decompose:** quebra tasks grandes em cards menores
- **Falhas:** tolera até 2 falhas consecutivas por task
- **Recuperação:** tasks bloqueadas podem ser reativadas via Telegram

### 3. Pipeline Automática

Script Python (`kanban-pipeline.py`) que monitora o board e encadeia tasks.

Funciona como cron job (`* * * * *`) e verifica:
1. Tasks concluídas desde a última execução
2. Aplica regras de pipeline (backend → frontend → deploy → healthcheck)
3. Cria a task seguinte automaticamente

### 4. Monitor Telegram

Script Python (`kanban-monitor.py`) que detecta tasks problemáticas.

Fluxo:
1. Query SQL no banco Kanban
2. Compara contra `seen.json` (evita notificar 2x)
3. Envia mensagem formatada via `hermes send`
4. Usuário responde com `/autorizar` ou `/ignorar`

### 5. Perfis de Worker

Cada perfil é uma configuração Hermes independente com:
- `config.yaml` — modelo, tokens, iterações
- `SOUL.md` — instruções de personalidade e comportamento

## Fluxo Completo

```
1. Usuário: "quero um sistema de estoque"
2. Orquestrador analisa → cria task "Backend: API de estoque" no Kanban
3. Worker backend-senior executa e completa
4. Pipeline detecta "Backend* completo" → cria "Frontend: UI p/ estoque"
5. Worker frontend-rapido executa
6. Se falhar → Telegram: "Frontend Rapido travou. /autorizar?"
7. Usuário autoriza → worker continua ou reinicia
8. Pipeline detecta "Frontend* completo" → cria "Deploy: estoque"
9. ... e assim por diante
```

## Otimizações

- **Cache de prompt** DeepSeek: 96-100% hit rate
- **SOUL.md enxuto:** máximo 31 linhas
- **max_turns baixo:** 5-25 dependendo do perfil
- **Cron no_agent:** zero tokens para pipeline/monitor
