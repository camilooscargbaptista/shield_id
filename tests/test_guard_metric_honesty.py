"""T-FIX-02 — prova de regressão do hardening do `metric_honesty` (rules 05/07/15).

Roda o guard via subprocess contra cada fixture e afere o exit code. Prova bidirecional:
- os fixtures de DEFEITO (fração, 1 dígito, circularidade, threshold-sweep) → exit 1;
- os fixtures LIMPOS (o clean canônico do PORT-2 e o clean com negação) → exit 0.
Também reexecuta o par canônico PORT-2 (experiment_defect → 1, eval_report_clean → 0).
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GUARD = REPO / "scripts" / "guards" / "metric_honesty.py"
FX = REPO / "tests" / "fixtures" / "guards"
PORT2 = REPO / "tests" / "fixtures" / "port2"


def _run(fixture: Path):
    return subprocess.run(
        [sys.executable, str(GUARD), "--require-cross-generator", str(fixture)],
        cwd=str(REPO), capture_output=True, text=True,
    )


DEFECTS = [
    ("mh_fraction_defect.md", "cross-generator"),        # fração sem cross-generator
    ("mh_onedigit_defect.md", "cross-generator"),        # % de 1 dígito sem cross-generator
    ("mh_circularity_defect.md", "circularity"),         # held-out no treino
    ("mh_threshold_sweep_defect.md", "held-out"),        # threshold tunado no held-out
]

CLEANS = ["mh_clean_negation.md"]


@pytest.mark.parametrize("name,needle", DEFECTS)
def test_defect_fixtures_block(name, needle):
    r = _run(FX / name)
    assert r.returncode == 1, f"{name} deveria BLOQUEAR (1), veio {r.returncode}\n{r.stdout}\n{r.stderr}"
    assert needle.lower() in r.stdout.lower(), f"{name}: mensagem não nomeia '{needle}':\n{r.stdout}"


@pytest.mark.parametrize("name", CLEANS)
def test_clean_fixtures_pass(name):
    r = _run(FX / name)
    assert r.returncode == 0, f"{name} deveria PASSAR (0), veio {r.returncode}\n{r.stdout}\n{r.stderr}"


def test_port2_defect_blocks_naming_all_three():
    """O par canônico PORT-2: o defeito plantado (que passava 22 dias) agora bloqueia nomeando
    circularidade E threshold-sweep E métrica."""
    r = _run(PORT2 / "experiment_defect.md")
    assert r.returncode == 1, f"experiment_defect deveria BLOQUEAR:\n{r.stdout}\n{r.stderr}"
    out = r.stdout.lower()
    assert "circularity" in out                     # circularidade
    assert "held-out" in out and "threshold" in out # threshold-sweep
    assert "metric" in out                          # métrica detectada


def test_port2_clean_passes():
    r = _run(PORT2 / "eval_report_clean.md")
    assert r.returncode == 0, f"eval_report_clean deveria PASSAR:\n{r.stdout}\n{r.stderr}"


def test_missing_file_is_not_an_error(tmp_path):
    """Arquivo inexistente não é erro de parse: nada a escanear → exit 0 (comportamento correto)."""
    r = _run(tmp_path / "nope.md")
    assert r.returncode == 0


def test_read_error_blocks_not_failopen(tmp_path):
    """Erro de LEITURA deve BLOQUEAR (fail-closed), nunca exit 0 silencioso (anti-fail-open)."""
    import os, stat
    bad = tmp_path / "unreadable.md"
    # payload dishonesto montado por fragmentos: contíguo no arquivo escrito, NÃO no source deste
    # teste (senão o próprio metric_honesty flagaria este .py na varredura do repo — auto-trip).
    bad.write_text("rec" + "all = 0." + "99\n")
    os.chmod(bad, 0)
    try:
        if os.access(str(bad), os.R_OK):  # ainda legível (ex.: root) → caminho não exercitável
            pytest.skip("arquivo permaneceu legível; caminho de read-error não testável neste ambiente")
        r = _run(bad)
        assert r.returncode == 1, f"read-error deveria BLOQUEAR (1), veio {r.returncode}\n{r.stdout}\n{r.stderr}"
        assert "fail-closed" in (r.stdout + r.stderr).lower()
    finally:
        os.chmod(bad, stat.S_IRUSR | stat.S_IWUSR)   # restaura p/ cleanup do tmp_path
