"""Prompt para el asistente de IA que responde preguntas."""

SYSTEM_PROMPT = """Eres un asistente IA especializado en monitoreo y análisis de incidencias operativas.

Responde de manera clara, concisa y basada ÚNICAMENTE en los datos proporcionados en el contexto.
Si no tienes información suficiente para responder con precisión, indícalo honestamente.
Responde en español. Si la pregunta pide datos numéricos, cita los números del contexto."""

USER_PROMPT = """Tienes acceso a los siguientes datos actualizados:

RESUMEN DE INCIDENCIAS:
- Total: {total_incidencias}
- Abiertas: {open_incidencias}
- Pendientes: {pending_incidencias}
- Cerradas: {closed_incidencias}
- Críticas: {critical_incidencias}
- Promedio de resolución: {avg_resolution_time}h

INCIDENCIAS POR CATEGORÍA:
{categories_breakdown}

INCIDENCIAS RECIENTES (máximo 10):
{recent_incidencias_list}

PREGUNTA DEL USUARIO:
{user_pregunta}

Responde en español, de forma clara y accionable."""


def build_prompt(context: dict, pregunta: str) -> tuple[str, str]:
    user = USER_PROMPT.format(
        total_incidencias=context["total_incidencias"],
        open_incidencias=context["open_incidencias"],
        pending_incidencias=context["pending_incidencias"],
        closed_incidencias=context["closed_incidencias"],
        critical_incidencias=context["critical_incidencias"],
        avg_resolution_time=context["avg_resolution_time"],
        categories_breakdown=context["categories_breakdown"],
        recent_incidencias_list=context["recent_incidencias_list"],
        user_pregunta=pregunta,
    )
    return SYSTEM_PROMPT, user