"""
Monitora tasks timed_out/blocked e notifica no Telegram.
Uso (no_agent=True): o cron job roda esse script a cada 30s.
"""
import json, os, sqlite3, subprocess, sys, time, re
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
SEEN_FILE = HERMES_HOME / ".kanban_monitor_seen.json"
CONFIG_FILE = HERMES_HOME / "config.yaml"

# Carrega chat_id da sessão do Telegram
def get_telegram_chat_id():
    sess_file = HERMES_HOME / "sessions" / "sessions.json"
    if sess_file.exists():
        try:
            data = json.loads(sess_file.read_text())
            # Pode ser dict (chave = session_key) ou lista
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, dict):
                        plat = val.get("platform") or val.get("origin", {}).get("platform", "")
                        if "telegram" in str(plat).lower():
                            cid = val.get("chat_id") or val.get("origin", {}).get("chat_id")
                            if cid:
                                return str(cid)
            elif isinstance(data, list):
                for s in data:
                    if s.get("platform") == "telegram":
                        return str(s.get("chat_id"))
        except Exception as e:
            print(f"[monitor] sessions.json parse error: {e}", file=sys.stderr)
    return None

def get_kanban_db_path():
    """Procura o banco SQLite do Kanban."""
    for p in [
        HERMES_HOME / "kanban.db",
        HERMES_HOME / "kanban" / "default.db",
    ]:
        if p.exists():
            return p
    return None

def get_blocked_or_timed_out():
    """Busca tasks timed_out ou blocked."""
    db_path = get_kanban_db_path()
    if not db_path:
        print("[monitor] Kanban DB not found", file=sys.stderr)
        return []

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, title, status, assignee, max_retries, max_runtime_seconds, "
            "consecutive_failures as retry_count "
            "FROM tasks "
            "WHERE status IN ('timed_out', 'blocked') "
            "ORDER BY id DESC"
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"[monitor] DB error: {e}", file=sys.stderr)
        return []

def send_telegram(chat_id, text):
    """Envia mensagem via hermes send."""
    try:
        target = f"telegram:{chat_id}"
        result = subprocess.run(
            ["hermes", "send", text, "--to", target],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return True
        print(f"[monitor] send error: {result.stderr.strip()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[monitor] send error: {e}", file=sys.stderr)
        return False

def promote_task(task_id):
    """Promove a task de timed_out pra ready pra rodar de novo."""
    subprocess.run(
        ["hermes", "kanban", "promote", task_id],
        capture_output=True, text=True, timeout=15,
    )

def load_seen():
    if SEEN_FILE.exists():
        try:
            return json.loads(SEEN_FILE.read_text())
        except Exception:
            pass
    return {}

def save_seen(seen):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen, indent=2) + "\n")

def run_once():
    chat_id = get_telegram_chat_id()
    if not chat_id:
        print("[monitor] No Telegram chat_id found", file=sys.stderr)
        return

    seen = load_seen()
    tasks = get_blocked_or_timed_out()

    for t in tasks:
        tid = t["id"]
        if tid in seen:
            continue

        who = t.get("assignee") or "um agente"
        title = t.get("title") or "(sem título)"
        status = t.get("status", "unknown")

        if status == "timed_out":
            who_display = who.replace("-", " ").title()
            msg = (
                f"⏱ {who_display} ({title[:60]}) atingiu o limite de iterações\n"
                f"Deseja aumentar e continuar? Responda:\n"
                f"  /autorizar {tid}  —  sim, liberar\n"
                f"  /ignorar {tid}    —  não, descartar"
            )
        elif status == "blocked":
            who_display = who.replace("-", " ").title()
            msg = (
                f"⏸ {who_display} ({title[:60]}) está bloqueado\n"
                f"Deseja autorizar? Responda:\n"
                f"  /autorizar {tid}  —  sim, liberar\n"
                f"  /ignorar {tid}    —  não, descartar"
            )
        else:
            continue

        ok = send_telegram(chat_id, msg)
        if ok:
            seen[tid] = int(time.time())
        save_seen(seen)

def main():
    if "--once" in sys.argv:
        run_once()
        return
    print("[monitor] Watching for timed_out/blocked tasks every 30s...")
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[monitor] Error: {e}", file=sys.stderr)
        time.sleep(30)

if __name__ == "__main__":
    main()
