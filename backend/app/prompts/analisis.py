"""Prompt para generar perspectivas operativas automáticas."""

SYSTEM_PROMPT = """Eres un analista de incidencias especializado en identificar patrones y tendencias.
Identifica 3-4 perspectivas principales que un gestor operativo debe conocer.
Cada perspectiva debe:
- Ser específico y accionable
- Incluir un título corto
- Indicar impacto (high|medium|low|positive)
- Tener una categoría asociada (o "Operación")
- Basarse ÚNICAMENTE en los datos proporcionados; nunca inventar cifras

REGLAS ESTRICTAS SOBRE PORCENTAJES:
- Si el período anterior tiene 0, 1 o 2 incidencias para una categoría o métrica,
  NO calcules porcentajes de cambio: no existe una base de comparación fiable.
  Reporta solo los números absolutos y menciona que no hay base previa.
- Si la comparación indica "sin dato previo", nunca derives un porcentaje.
- Cita los valores tal como aparecen en los datos (ej: "Pagos: 12 vs 3").

Responde SOLO en este formato JSON, sin texto adicional, como una lista:
[
  {{
    "titulo": "string",
    "descripcion": "string",
    "impact": "high|medium|low|positive",
    "categoria": "string"
  }}
]"""

USER_PROMPT = """Analiza los siguientes datos del período {period}:

MÉTRICAS PRINCIPALES:
{metrics_data}

CAMBIOS RESPECTO A PERÍODO ANTERIOR:
{comparison_data}

DESGLOSE POR CATEGORÍA:
{categoria_breakdown}

CAMBIO POR CATEGORÍA VS PERÍODO ANTERIOR:
{categoria_deltas}

TENDENCIA DE RESOLUCIÓN:
{resolution_trend}

Genera las perspectivas en español, respetando las reglas estrictas sobre porcentajes sin base de comparación fiable."""


def build_prompt(period: str, context: dict) -> tuple[str, str]:
    user = USER_PROMPT.format(
        period=period,
        metrics_data=context["metrics_data"],
        comparison_data=context["comparison_data"],
        categoria_breakdown=context["categoria_breakdown"],
        categoria_deltas=context.get("categoria_deltas_vs_previous_period", "(sin datos comparables)"),
        resolution_trend=context["resolution_trend"],
    )
    return SYSTEM_PROMPT, user