"""Recomendación basada en casos usando TF-IDF puro en Python + similitud de coseno.

Sin librerías externas de ML/vectores: el corpus lo componen incidencias reales
resueltas (estado "Cerrada") más incidencias cuyo análisis IA fue confirmado por
una analista (confirmado=True). Cada resultado es trazable a una incidencia real
(incidencia_referencia_id) y a un valor real de similitud.
"""

import math
import re
from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import AnalisisIA, Incidencia, Estado

TOKEN_RE = re.compile(r"[a-záéíóúüñ0-9]+")

# Umbral mínimo de similitud de coseno para considerar válido un caso de referencia.
CASE_SIMILARITY_THRESHOLD = 0.30


def _tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall((text or "").lower()) if len(t) > 1]


class IndiceCasos:
    """Índice TF-IDF en memoria sobre incidencias históricas."""

    def __init__(self, cases: Iterable[Incidencia]):
        self.cases = list(cases)
        self.docs = [
            {
                "incidencia": inc,
                "tokens": _tokenize(f"{inc.titulo} {inc.descripcion}"),
                "categoria": inc.categoria.name if inc.categoria else "Otros",
            }
            for inc in self.cases
        ]
        vocab: set[str] = set()
        for doc in self.docs:
            vocab.update(doc["tokens"])
        self.vocab = sorted(vocab)
        self.idf = self._compute_idf()
        self.vectors = [self._vector(doc["tokens"]) for doc in self.docs]
        self.norms = [self._norm(v) for v in self.vectors]

    def _compute_idf(self) -> dict[str, float]:
        n = max(len(self.docs), 1)
        idf: dict[str, float] = {}
        for term in self.vocab:
            df = sum(1 for doc in self.docs if term in doc["tokens"])
            idf[term] = math.log((1 + n) / (1 + df)) + 1.0
        return idf

    @staticmethod
    def _vector(tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        n = len(tokens)
        return {term: count / n for term, count in counts.items()}

    @staticmethod
    def _norm(vector: dict[str, float]) -> float:
        return math.sqrt(sum(x * x for x in vector.values())) or 1.0

    def similarity(self, text: str) -> float:
        query = self._vector(_tokenize(text))
        qnorm = self._norm(query)
        best = 0.0
        for i, vector in enumerate(self.vectors):
            dot = sum(query.get(term, 0.0) * vector.get(term, 0.0) for term in query)
            sim = dot / (qnorm * self.norms[i])
            if sim > best:
                best = sim
        return best

    def most_similar(self, text: str) -> tuple[float, Incidencia | None]:
        query = self._vector(_tokenize(text))
        qnorm = self._norm(query)
        scored: list[tuple[float, dict]] = []
        for i, vector in enumerate(self.vectors):
            dot = sum(query.get(term, 0.0) * vector.get(term, 0.0) for term in query)
            sim = dot / (qnorm * self.norms[i])
            scored.append((sim, self.docs[i]))
        scored.sort(key=lambda item: item[0], reverse=True)
        if not scored:
            return 0.0, None
        sim, doc = scored[0]
        ref_incidencia = doc["incidencia"]
        return sim, ref_incidencia if sim >= CASE_SIMILARITY_THRESHOLD else None


def construir_indice_casos(db: Session, exclude_incidencia_id: int | None = None) -> IndiceCasos:
    """Indexa incidencias resueltas/confirmadas como casos de referencia (datos reales)."""
    candidates: dict[int, Incidencia] = {}
    closed_ids = db.scalars(
        select(Estado.id).where(func.lower(Estado.name) == "cerrada")
    ).all()

    for incidencia in db.scalars(
        select(Incidencia)
        .where(
            Incidencia.id != (exclude_incidencia_id or -1),
            Incidencia.estado_id.in_(closed_ids),
        )
        .options(selectinload(Incidencia.categoria))
    ).all():
        candidates[incidencia.id] = incidencia

    for analisis_id in db.scalars(select(AnalisisIA.incidencia_id).where(
        AnalisisIA.confirmado.is_(True)
    )).all():
        if analisis_id not in candidates:
            incidencia = db.get(Incidencia, analisis_id)
            if incidencia:
                candidates[analisis_id] = incidencia

    return IndiceCasos(candidates.values())


def buscar_caso_referencia(
    db: Session, titulo: str, descripcion: str, incidencia_id: int | None = None
) -> tuple[float, Incidencia | None, str | None]:
    index = construir_indice_casos(db, exclude_incidencia_id=incidencia_id)
    sim, ref = index.most_similar(f"{titulo} {descripcion}")
    if ref is None:
        return 0.0, None, None
    categoria = ref.categoria.name if ref.categoria else "Otros"
    return sim, ref, categoria