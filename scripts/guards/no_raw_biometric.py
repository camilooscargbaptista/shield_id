#!/usr/bin/env python3
"""I1 (rule 04): block raw-biometric persistence. Scans given files (or staged) for patterns
that persist raw face/voice/document bytes. Derived feature vectors are allowed.
Exit 1 = BLOCK."""
import sys, re
from pathlib import Path

# Suspicious: a persisted column/field that stores raw biometric bytes/base64/blob.
PERSIST_PATTERNS = [
    r"(face|voice|fingerprint|iris|biometric)[_a-z0-9]*\s*[:=]\s*(Column|Field|BYTEA|LargeBinary|BinaryField|blob)",
    r"(raw_?(face|voice|biometric|image|audio))\s*[:=]",
    r"\.(save|write|insert|persist)\([^)]*(raw_?(face|voice|biometric|image|audio))",
    r"Column\([^)]*name\s*=\s*['\"](face|voice|biometric)[_a-z]*['\"]",
]
ALLOW = re.compile(r"(derived|feature_vector|embedding|hash|cadence|timing)", re.I)

# False-positive exclusions (do NOT weaken I1 — these surfaces never PERSIST a biometric):
#  - Markdown docs legitimately SHOW the forbidden pattern as a ❌ teaching example (rule 04).
#  - The guards' own source enumerates the patterns / prints the guard name ("raw_biometric:").
# All real code (.py/.sql/schemas/etc.) is still fully scanned — persistence lives there, not in docs.
def _excluded(path: str) -> bool:
    norm = path.replace("\\", "/")
    return norm.endswith(".md") or "scripts/guards/" in norm

def scan(files):
    hits = []
    for f in files:
        if _excluded(str(f)): continue
        p = Path(f)
        if not p.is_file(): continue
        try: text = p.read_text(errors="ignore")
        except Exception: continue
        for i, line in enumerate(text.splitlines(), 1):
            if ALLOW.search(line): continue
            for pat in PERSIST_PATTERNS:
                if re.search(pat, line, re.I):
                    hits.append((f, i, line.strip()[:100]))
    return hits

def main():
    args = sys.argv[1:]
    # FIX (T-FIX-03): parentetiza o fallback. O bug de precedência anterior —
    #   args or [glob] if Path("src").exists() else []
    # é avaliado como  (args or [glob]) if Path("src").exists() else []  → de um cwd SEM src/,
    # files=[] MESMO com arquivos passados por argumento → o guard não escaneava nada e saía 0
    # (fail-OPEN de um invariante CRÍTICO, I1). no_hardcoded.py já estava correto (referência).
    files = args or ([str(p) for p in Path("src").rglob("*.py")] if Path("src").exists() else [])
    # Fail-closed na seleção: um caminho pedido explicitamente mas ausente NÃO pode ser ignorado em
    # silêncio (esconderia um scan que o chamador pediu). Aviso no stderr; um arquivo inexistente não
    # tem bytes a vazar, então o exit continua governado pelo scan dos arquivos que existem.
    if args:
        for f in args:
            if not Path(f).is_file():
                print(f"no_raw_biometric: WARNING — requested path not found, not scanned: {f}", file=sys.stderr)
    elif not files:
        print("no_raw_biometric: WARNING — no files passed and no src/ tree; nothing to scan.", file=sys.stderr)
    hits = scan(files)
    if hits:
        print("BLOCKED — I1 raw-biometric persistence (rule 04). Use derived feature vectors only:")
        for f, i, l in hits: print(f"  {f}:{i}: {l}")
        raise SystemExit(1)
    print("no_raw_biometric: OK"); raise SystemExit(0)

if __name__ == "__main__": main()
