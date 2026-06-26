# 📖 Guia de Uso

## Kanban CLI

### Criar task
```bash
hermes kanban create "API de clientes" \
  --body "CRUD completo com autenticação JWT"
```

### Listar board
```bash
hermes kanban list
```

### Ver detalhes
```bash
hermes kanban show t_abc123
```

### Avançar task
```bash
hermes kanban promote t_abc123
```

### Mover para qualquer status
```bash
hermes kanban move t_abc123 --to executing
```

**Status disponíveis:** triagem → a-fazer → pronto → executando → revisao → concluido

---

## Dashboard Web

```bash
hermes dashboard --port 9119 --host 127.0.0.1
```

Acesse: [http://localhost:9119](http://localhost:9119)

---

## Telegram Remoto

### Comandos

| Comando | Ação |
|---------|------|
| `/autorizar t_abc123` | Libera task bloqueada (aumenta iterações) |
| `/ignorar t_abc123` | Arquiva task sem executar |

### Exemplo de notificação

```
⏱ Frontend Rapido (Calculadora) atingiu o limite de iterações
Deseja aumentar e continuar? Responda:
  /autorizar t_abc123  →  liberar
  /ignorar t_abc123    →  descartar
```

---

## Fluxo de Trabalho Diário

```
1. 🧠 → "Quero um sistema de encurtar URLs"
2. 🎯 Orquestrador planeja
3. 📋 Kanban: "Backend: API de encurtamento"
4. 👨‍💻 Backend Sênior executa → 9/9 testes ✅
5. 🔄 Pipeline detecta conclusão
6. 📋 Kanban: "Frontend: UI para encurtamento"
7. 🎨 Frontend Rápido executa ✅
8. 🔄 Pipeline detecta → encerra (sem deploy configurado)
9. ✅ Projeto completo
```

---

## Dicas e Boas Práticas

- **Nomes de tasks começando com `Backend*` ou `Frontend*` disparam a pipeline** automaticamente
- **2 falhas consecutivas** bloqueiam a task e notificam Telegram
- **Tasks sem match na pipeline** apenas concluem sem criar sucessoras
- **Orquestrador também cria tasks** diretamente — não precisa manual
