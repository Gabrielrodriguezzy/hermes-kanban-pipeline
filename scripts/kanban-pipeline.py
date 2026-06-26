"""
Automated Kanban pipeline — watches for completed tasks and creates
the next step based on workflow rules.

Usage:
  python3 ~/.hermes/scripts/kanban-pipeline.py       # watch mode (every 30s)
  python3 ~/.hermes/scripts/kanban-pipeline.py --once # single run
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERMES = os.environ.get("HERMES_BIN", "hermes")
SEEN_FILE = Path.home() / ".hermes" / ".pipeline_seen.json"

# ── Workflow rules ──────────────────────────────────────────────────────
# Each rule: when a task whose title matches `trigger_pattern` completes,
# create a follow-up task with `title`, `assignee`, `body`.
# `pre_requisite` = True means: only create if no follow-up already exists for this chain.

WORKFLOWS: list[dict] = [
    {
        "trigger_pattern": r"^(backend|API|CRUD|API REST)",
        "title_template": "Frontend: UI para {title}",
        "assignee": "frontend",
        "body": (
            "## Contexto\n"
            "O backend foi concluído e está no ar. Agora precisa de interface.\n\n"
            "## Objetivo\n"
            "Criar interface web para consumir a API do backend.\n\n"
            "## Detalhamento\n"
            "React/Next.js com Tailwind. Telas: listagem, formulário de criação,\n"
            "ediçao e exclusão. Feedback visual (loading, erro, sucesso).\n"
            "Consumir os endpoints da API via fetch/axios.\n\n"
            "## Restrições\n"
            "Nenhuma autenticação por enquanto. Apenas o CRUD funcional."
        ),
        "assignee_if_missing": "frontend",
    },
    {
        "trigger_pattern": r"^(frontend|interface|UI|tela)",
        "title_template": "Deploy: {title}",
        "assignee": "backend-senior",
        "body": (
            "## Contexto\n"
            "Frontend concluído. Agora precisa subir em produção.\n\n"
            "## Objetivo\n"
            "Criar Docker multi-stage (backend + frontend) e docker-compose.\n\n"
            "## Detalhamento\n"
            "Dockerfile para o backend (uvicorn). Dockerfile para o frontend (build estático + nginx).\n"
            "docker-compose.yml com rede compartilhada. .env.example com variáveis.\n"
            "Testar local com docker compose up."
        ),
        "assignee_if_missing": "backend-senior",
    },
    {
        "trigger_pattern": r"^(deploy|docker|Docker)",
        "title_template": "Healthcheck: Validar {title}",
        "assignee": "backend-senior",
        "body": (
            "## Contexto\n"
            "Deploy concluído. Validar se está tudo no ar.\n\n"
            "## Objetivo\n"
            "Fazer healthcheck: acessar endpoints, verificar se retornam 200,\n"
            "testar fluxo completo (criar + consultar). Relatar resultado."
        ),
        "assignee_if_missing": "backend-senior",
    },
]


def _hermes_json(*args: str) -> list[dict] | dict | None:
    """Run hermes command and parse JSON output."""
    cmd = [HERMES] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"[pipeline] hermes error: {result.stderr.strip()}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[pipeline] non-JSON output: {result.stdout[:200]}", file=sys.stderr)
        return None


def get_completed_tasks() -> list[dict]:
    """Fetch all done tasks."""
    data = _hermes_json("kanban", "list", "--status", "done", "--json")
    if isinstance(data, list):
        return data
    return []


def load_seen() -> dict:
    """Load mapping: triggered_task_id -> followup_task_id."""
    if SEEN_FILE.exists():
        raw = SEEN_FILE.read_text().strip()
        return json.loads(raw) if raw else {}
    return {}


def save_seen(seen: dict):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen, indent=2) + "\n")


def create_task(title: str, assignee: str, body: str) -> str | None:
    """Create a kanban task. Returns task ID or None."""
    cmd = [
        HERMES, "kanban", "create", title,
        "--assignee", assignee,
        "--body", "-",
    ]
    result = subprocess.run(
        cmd, input=body, capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        m = re.search(r"(t_\w+)", result.stdout)
        new_id = m.group(1) if m else "unknown"
        print(f"[pipeline] Created {new_id}: {title}")
        return new_id
    else:
        print(f"[pipeline] create failed: {result.stderr.strip()}", file=sys.stderr)
        return None


def run_once():
    seen = load_seen()
    tasks = get_completed_tasks()

    for task in tasks:
        task_id = task.get("id", "")
        if not task_id or task_id in seen:
            continue

        title = task.get("title", "")
        assignee = task.get("assignee", "")

        # Find matching workflow
        for wf in WORKFLOWS:
            if re.search(wf["trigger_pattern"], title, re.IGNORECASE):
                new_title = wf["title_template"].format(title=title)
                new_assignee = assignee if assignee else "backend-senior"
                new_body = wf["body"]

                print(f"[pipeline] {title} -> {new_title} ({new_assignee})")
                new_id = create_task(new_title, new_assignee, new_body)
                if new_id:
                    seen[task_id] = new_id
                break

    if seen != load_seen():
        save_seen(seen)


def main():
    if "--once" in sys.argv:
        run_once()
        return

    print("[pipeline] Watching for completed tasks every 30s...")
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[pipeline] Error: {e}", file=sys.stderr)
        time.sleep(30)


if __name__ == "__main__":
    main()
