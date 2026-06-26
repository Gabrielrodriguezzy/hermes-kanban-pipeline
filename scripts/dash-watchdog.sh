#!/usr/bin/env bash
# Watchdog do Dashboard Kanban — restart automático se cair
# Uso: adicionar como cron job a cada 30min

if ! ss -tlnp | grep -q 9119; then
  hermes dashboard --port 9119 --host 127.0.0.1 &
  echo "dashboard restarted at $(date)"
fi
