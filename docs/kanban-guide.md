# Guia do Kanban

## Como Usar

### Criar uma task manualmente

```bash
hermes kanban create "Título da task" --body "Descrição"
```

### Ver board

```bash
hermes kanban list
```

### Ver detalhes de uma task

```bash
hermes kanban show t_xxx
```

### Promover task (mudar status)

```bash
hermes kanban promote t_xxx
```

### Dashboard Web

O dashboard roda em `http://localhost:9119`.

Para iniciar:

```bash
hermes dashboard --port 9119 --host 127.0.0.1
```

## Pipeline Automática

Quando o cron job detecta uma task concluída, ele cria a próxima task automaticamente:

| Task concluída | Nova task criada |
|----------------|-----------------|
| `Backend*`, `API*`, `CRUD*` | `Frontend: UI para {title}` |
| `Frontend*`, `Interface*`, `UI*` | `Deploy: {title}` |
| `Deploy*`, `Docker*` | `Healthcheck: Validar {title}` |

## Monitoramento Telegram

Tasks que travam disparam notificação:

```
⏱ Frontend Rapido (Calculadora) atingiu o limite de iterações
Deseja aumentar? /autorizar t_xxx  ou  /ignorar t_xxx
```

### Comandos do Telegram

| Comando | Ação |
|---------|------|
| `/autorizar t_xxx` | Libera task bloqueada |
| `/ignorar t_xxx` | Arquiva task |

## Dicas

- Tasks com nome começando com `backend*` disparam pipeline automaticamente
- `consecutive_failures >= 2` bloqueia a task
- Use quick commands no Telegram para autorizar
- Orquestrador também pode criar tasks a partir de ideias vagas
