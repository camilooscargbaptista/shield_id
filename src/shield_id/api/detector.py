"""Interface `Detector` + `MockDetector` determinístico (D11 — sem GPU, sem modelo real).

A interface espelha a forma do detector real `TextForgeryDetector.predict_proba`
(`Sequence[str] -> List[float]`, cada valor = P(entrada é sintética/forjada), o
`artifact_score`). Assim o detector real pluga aqui depois SEM mudar a API.
"""
from __future__ import annotations

import hashlib
from typing import List, Protocol, Sequence, runtime_checkable


@runtime_checkable
class Detector(Protocol):
    """Forma mínima que a API exige de qualquer detector (real ou mock).

    Espelha `TextForgeryDetector.predict_proba`. O score é P(entrada é forjada/
    sintética) em [0,1] — quanto maior, MENOR a confiança.
    """

    def predict_proba(self, texts: Sequence[str]) -> List[float]:
        """Retorna P(forjado) para cada texto, em [0,1], na mesma ordem da entrada."""
        ...


class MockDetector:
    """Detector determinístico para teste (D11).

    O score vem de um hash estável do texto — NÃO aleatório — para que os testes
    de contrato sejam reprodutíveis. Não treina, não usa GPU, não persiste nada
    (I1/rule 04: o texto é consumido em memória e descartado).
    """

    def predict_proba(self, texts: Sequence[str]) -> List[float]:
        return [self._stable_score(t) for t in texts]

    @staticmethod
    def _stable_score(text: str) -> float:
        """Mapeia o texto para [0,1) de forma determinística via SHA-256.

        Hash one-way: o score derivado NÃO permite reconstruir o texto (I1/rule 04).
        """
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # 6 bytes -> inteiro -> normalizado para [0,1). Estável entre execuções/máquinas.
        bucket = int.from_bytes(digest[:6], "big")
        return bucket / float(1 << 48)
