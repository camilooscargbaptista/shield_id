"""T-FIX-01 — split disjunto train/held-out do conjunto de controle (I4/D8, rule 05/07/32).

Prova que nenhuma amostra de controle (label=0) aparece simultaneamente no treino e no held-out,
que o split e deterministico (hash, sem RNG) e que a verificacao defensiva recusa um split contaminado.
"""
import pytest

from shield_id.layers.layer1_detection.config import TextDetectorConfig
from shield_id.training.train_text_detector import (
    split_cross_generator,
    _split_controls,
    _control_bucket,
)
from shield_id.data.redteam import (
    generate_batch,
    split_for_cross_generator,
    _shard_controls,
)


def _rows():
    """Synthetic rows: controles variados + ataques de gerador de treino + ataques do held-out."""
    rows = []
    for i in range(40):
        rows.append({"text": f"legit document number {i}", "label": 0,
                     "generator": "control", "segment": "seg-1"})
    for i in range(20):
        rows.append({"text": f"chatgpt attack {i}", "label": 1,
                     "generator": "chatgpt", "segment": "seg-1"})
    for i in range(20):
        rows.append({"text": f"gpt4 attack {i}", "label": 1,
                     "generator": "gpt4", "segment": "seg-2"})
    return rows


# ---- (a) disjuncao: nenhum texto de controle nos dois lados ----
def test_controls_disjoint_between_train_and_heldout():
    cfg = TextDetectorConfig()
    train, heldout = split_cross_generator(_rows(), cfg)
    train_ctrl = {r["text"] for r in train if r["label"] == 0}
    held_ctrl = {r["text"] for r in heldout if r["label"] == 0}
    assert train_ctrl, "esperado controle no treino (fraction=0.7, 40 controles)"
    assert held_ctrl, "esperado controle no held-out"
    assert train_ctrl.isdisjoint(held_ctrl)                       # nenhum controle nos dois lados (I4/D8)
    # e, no geral, nenhum texto e compartilhado entre os dois lados
    assert {r["text"] for r in train}.isdisjoint({r["text"] for r in heldout})


def test_split_controls_partitions_all_without_loss():
    controls = [{"text": f"c{i}", "label": 0} for i in range(200)]
    train_c, held_c = _split_controls(controls, 0.7)
    assert len(train_c) + len(held_c) == len(controls)            # particao total (sem perda)
    assert {r["text"] for r in train_c}.isdisjoint({r["text"] for r in held_c})


def test_control_bucket_in_range_and_stable():
    b = _control_bucket("hello")
    assert 0.0 <= b < 1.0
    assert _control_bucket("hello") == b                          # rule 07: estavel


# ---- (b) determinismo: duas chamadas produzem splits identicos ----
def test_split_is_deterministic():
    cfg = TextDetectorConfig()
    rows = _rows()
    t1, h1 = split_cross_generator(rows, cfg)
    t2, h2 = split_cross_generator(rows, cfg)
    assert [r["text"] for r in t1] == [r["text"] for r in t2]
    assert [r["text"] for r in h1] == [r["text"] for r in h2]


# ---- (c) ValueError na verificacao defensiva com fixture forjada ----
def test_defensive_check_raises_on_forged_overlap():
    cfg = TextDetectorConfig()
    # o MESMO texto aparece como ataque de gerador de treino E como ataque do held-out
    # -> cai nos dois lados -> a verificacao defensiva deve recusar (nomeando I4).
    forged = [
        {"text": "DUP", "label": 1, "generator": "chatgpt", "segment": "seg-1"},
        {"text": "DUP", "label": 1, "generator": "gpt4", "segment": "seg-1"},
    ]
    with pytest.raises(ValueError, match="I4"):
        split_cross_generator(forged, cfg)


# ---- (d) redteam: nenhum sample_id em dois grupos + sem dupla contagem ----
def test_redteam_control_shards_are_disjoint():
    samples = generate_batch(["A", "B"], n_per_gen=30,
                             seg_dist={"seg-1": 0.5, "seg-2": 0.5}, seed=7)
    controls = [s for s in samples if s.label == 0]
    groups = ["A", "B", "C"]
    shards = _shard_controls(controls, groups)
    all_ids = [s.sample_id for shard in shards.values() for s in shard]
    assert sorted(all_ids) == sorted(s.sample_id for s in controls)   # particao (sem perda)
    assert len(all_ids) == len(set(all_ids))                          # disjunto (nenhum id em 2 grupos)


def test_redteam_split_no_double_count_of_controls():
    samples = generate_batch(["A", "B"], n_per_gen=30, seg_dist={"seg-1": 1.0}, seed=7)
    scores, labels = split_for_cross_generator(samples, ["A", "B"], "C")
    assert set(scores) == {"A", "B", "C"}
    total_ctrl = sum(sum(1 for y in labels[g] if y == 0) for g in labels)
    n_controls = sum(1 for s in samples if s.label == 0)
    assert total_ctrl == n_controls   # cada controle aparece 1x no total (antes: n_controls * 3)
