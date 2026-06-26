# 🌟 Pipeline Automática

## Conceito

A pipeline converte conclusões de tasks em novas tasks automaticamente. Zero intervenção manual.

## Como funciona

Um cron job (`* * * * *`) executa o script `kanban-pipeline.py` a cada minuto. Ele:

1. **Verifica** tasks concluídas desde a última execução
2. **Aplica regras** de pipeline baseadas no título da task
3. **Cria** a próxima task no Kanban
4. **Notifica** o Telegram se algo travar

## Regras de Pipeline

| Task concluída | Nova task criada |
|----------------|------------------|
| `Backend*`, `API*`, `CRUD*` | `Frontend: UI para {title}` |
| `Frontend*`, `UI*`, `Interface*` | `Deploy: {title}` |
| `Deploy*`, `Release*` | `Healthcheck: Validar {title}` |
| Qualquer outra | Pipeline encerra |

## Fluxo Completo

```
🧠 Ideia: "Sistema de estoque"
    │
    ├── 🎯 Orquestrador planeja
    │       │
    │       └── 📋 Kanban: "Backend: API de estoque"
    │               │
    │               ├── 👨‍💻 Backend Sênior executa (20 iterações)
    │               │       │
    │               │       └── ✅ Concluído → Pipeline detecta
    │               │               │
    │               │               └── 📋 Kanban: "Frontend: UI para estoque"
    │               │                       │
    │               │                       ├── 🏗️ Frontend Sênior executa (25 iterações)
    │               │                       │       │
    │               │                       │       ├── ✅ Concluído
    │               │                       │       │       └── 📋 Kanban: "Deploy: estoque"
    │               │                       │       │               │
    │               │                       │       │               └── ...
    │               │                       │       │
    │               │                       │       └── ⛔ Falha (limite)
    │               │                       │               │
    │               │                       │               └── 📲 Telegram: "Autorizar?"
    │               │                       │                       │
    │               │                       │                       └── /autorizar → continua
    │               │                       │
    │               │                       └── Pipeline encerra (sem correspondência)
    │               │
    │               └── ⛔ Falha (limite)
    │                       │
    │                       └── 📲 Telegram: "Autorizar?"
    │                               │
    │                               └── /autorizar → continua
    │
    └── ✅ Sistema de estoque completo!

```

## Scripts

### `kanban-pipeline.py`

- **Trigger:** Cron job `* * * * *` (a cada minuto)
- **Modo:** `no_agent=True` — zero tokens
- **O que faz:** Consulta o banco Kanban, detecta tasks concluídas, cria próximas tasks
- **Config:** `context_from` encadeia com `kanban-monitor.py`

### `kanban-monitor.py`

- **Trigger:** Cron job a cada 30 minutos
- **Modo:** `no_agent=True` — zero tokens  
- **O que faz:** Busca tasks com `consecutive_failures >= 2`, notifica via Telegram
- **Dedup:** Mantém `seen.json` para não notificar a mesma task duas vezes

## Dashboard Web

O board visual roda em `http://localhost:9119`.

```bash
hermes dashboard --port 9119 --host 127.0.0.1
```
