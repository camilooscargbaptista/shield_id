"""T-FIX-03 — prova de regressão fail-closed dos guards de invariante (rule 04/I1, rule 13).

Roda CADA guard via subprocess a partir de um cwd temporário SEM `src/` (reproduz o cenário /tmp
que expôs o fail-open do `no_raw_biometric`), passando por argumento um arquivo com violação plantada
→ exit DEVE ser 1. O caso limpo → exit 0.

Os payloads de violação são montados a partir de fragmentos para que ESTE arquivo de teste não
dispare os próprios guards no pre-commit (que escaneiam os arquivos versionados, inclusive tests/).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUARDS = REPO / "scripts" / "guards"

# Violações montadas por concatenação: contíguas no ARQUIVO escrito, NÃO no source deste teste.
RAW_BIO_VIOLATION = "raw_" + "face = open('f.jpg', 'rb').read()\n"          # I1: persiste bytes crus
CPF_VIOLATION = "record," + "%03d.%03d.%03d-%02d\n" % (123, 456, 789, 0)     # I2: CPF real-looking
SECRET_VIOLATION = "api_" + "key = " + repr("A" * 24) + "\n"                 # segredo commitado
HARDCODED_VIOLATION = "thre" + "shold = 0.5\n"                               # rule 32

RAW_BIO_CLEAN = "feature_vector = derive(face_image)  # derived only (I1 ok)\n"
DATA_CLEAN = "record,synthetic-000\n"
SECRET_CLEAN = "x = 1\n"
HARDCODED_CLEAN = "threshold = cfg.decision_threshold  # from config (rule 32 ok)\n"


def _run(guard: str, argfile: Path, cwd: Path):
    return subprocess.run(
        [sys.executable, str(GUARDS / guard), str(argfile)],
        cwd=str(cwd), capture_output=True, text=True,
    )


# ---------- no_raw_biometric (o guard com o defeito corrigido) ----------
def test_no_raw_biometric_blocks_violation_from_foreign_cwd(tmp_path):
    bad = tmp_path / "leak.py"                 # tmp_path NÃO tem src/ — cenário do fail-open
    bad.write_text(RAW_BIO_VIOLATION)
    r = _run("no_raw_biometric.py", bad, tmp_path)
    assert r.returncode == 1, f"esperado BLOCK (1), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


def test_no_raw_biometric_clean_passes_from_foreign_cwd(tmp_path):
    good = tmp_path / "ok.py"
    good.write_text(RAW_BIO_CLEAN)
    r = _run("no_raw_biometric.py", good, tmp_path)
    assert r.returncode == 0, f"esperado OK (0), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


def test_no_raw_biometric_missing_arg_warns_not_silent(tmp_path):
    # arquivo pedido que não existe → aviso no stderr (não silêncio); sem violação real → exit 0
    r = _run("no_raw_biometric.py", tmp_path / "does_not_exist.py", tmp_path)
    assert r.returncode == 0
    assert "WARNING" in r.stderr and "not found" in r.stderr, f"stderr sem aviso: {r.stderr!r}"


# ---------- no_real_pii (irmão — sem defeito, aqui documentado) ----------
def test_no_real_pii_blocks_violation_from_foreign_cwd(tmp_path):
    bad = tmp_path / "people.csv"
    bad.write_text(CPF_VIOLATION)
    r = _run("no_real_pii.py", bad, tmp_path)
    assert r.returncode == 1, f"esperado BLOCK (1), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


def test_no_real_pii_clean_passes_from_foreign_cwd(tmp_path):
    good = tmp_path / "people.csv"
    good.write_text(DATA_CLEAN)
    r = _run("no_real_pii.py", good, tmp_path)
    assert r.returncode == 0, f"esperado OK (0), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


# ---------- secret_scan (irmão — sem defeito) ----------
def test_secret_scan_blocks_violation_from_foreign_cwd(tmp_path):
    bad = tmp_path / "conf.py"
    bad.write_text(SECRET_VIOLATION)
    r = _run("secret_scan.py", bad, tmp_path)
    assert r.returncode == 1, f"esperado BLOCK (1), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


def test_secret_scan_clean_passes_from_foreign_cwd(tmp_path):
    good = tmp_path / "conf.py"
    good.write_text(SECRET_CLEAN)
    r = _run("secret_scan.py", good, tmp_path)
    assert r.returncode == 0, f"esperado OK (0), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


# ---------- no_hardcoded (irmão — referência do padrão correto) ----------
def test_no_hardcoded_blocks_violation_from_foreign_cwd(tmp_path):
    bad = tmp_path / "detector.py"             # nome não-config, não-test → escaneado
    bad.write_text(HARDCODED_VIOLATION)
    r = _run("no_hardcoded.py", bad, tmp_path)
    assert r.returncode == 1, f"esperado BLOCK (1), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"


def test_no_hardcoded_clean_passes_from_foreign_cwd(tmp_path):
    good = tmp_path / "detector.py"
    good.write_text(HARDCODED_CLEAN)
    r = _run("no_hardcoded.py", good, tmp_path)
    assert r.returncode == 0, f"esperado OK (0), veio {r.returncode}\nOUT:{r.stdout}\nERR:{r.stderr}"
