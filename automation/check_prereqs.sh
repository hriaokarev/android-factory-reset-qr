#!/usr/bin/env bash
# Show / set OTG and jig prerequisite flags.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CFG="$ROOT/automation_config.json"
EXAMPLE="$ROOT/automation_config.example.json"

if [[ ! -f "$CFG" ]]; then
  cp "$EXAMPLE" "$CFG"
  echo "created $CFG from example"
fi

cmd="${1:-status}"

python3 - "$CFG" "$cmd" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
cmd = sys.argv[2]
cfg = json.loads(path.read_text(encoding="utf-8"))
cfg.setdefault("otg", {})
cfg.setdefault("jig", {})

if cmd == "status":
    print("otg.validated =", cfg["otg"].get("validated"))
    print("jig.qr_ready  =", cfg["jig"].get("qr_ready"))
    print("device_model  =", cfg["otg"].get("device_model") or "(unset)")
    print()
    print("Docs: validate_otg.md / jig_qr_setup.md")
    print("Set:  ./check_prereqs.sh otg-ok")
    print("      ./check_prereqs.sh jig-ok")
elif cmd == "otg-ok":
    cfg["otg"]["validated"] = True
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("set otg.validated=true")
elif cmd == "jig-ok":
    cfg["jig"]["qr_ready"] = True
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("set jig.qr_ready=true")
elif cmd == "reset-flags":
    cfg["otg"]["validated"] = False
    cfg["jig"]["qr_ready"] = False
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("flags reset to false")
else:
    print("usage: check_prereqs.sh [status|otg-ok|jig-ok|reset-flags]", file=sys.stderr)
    sys.exit(1)
PY
