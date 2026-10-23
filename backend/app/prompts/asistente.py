"""Prompt para el asistente de IA que responde preguntas."""

SYSTEM_PROMPT = """Eres un asistente IA especializado en monitoreo y análisis de incidencias operativas.

Responde de manera clara, concisa y basada ÚNICAMENTE en los datos proporcionados en el contexto.
Presta especial atención a las fechas y períodos de tiempo:
- Si el usuario pregunta por "esta semana" o los "últimos días", básate en la sección de "INCIDENCIAS DE ESTA SEMANA" y las fechas reales.
- Si no hay incidencias en ese período, acláralo honestamente (por ejemplo: "No se registraron incidencias en los últimos 7 días; las incidencias registradas corresponden a fechas anteriores").
- No confundas el total histórico acumulado con las incidencias de esta semana.
Responde en español. Si la pregunta pide datos numéricos, cita los números del contexto."""

USER_PROMPT = """FECHA ACTUAL DEL SISTEMA: {fecha_actual}

INCIDENCIAS DE ESTA SEMANA (ÚLTIMOS 7 DÍAS):
- Total creadas esta semana: {semana_total}
- Abiertas esta semana: {semana_abiertas}
- Críticas esta semana: {semana_criticas}
- Cerradas esta semana: {semana_cerradas}
Detalle de la semana:
{semana_detalle}

RESUMEN HISTÓRICO GLOBAL (TODO EL HISTORIAL):
- Total histórico acumulado: {total_incidencias}
- Abiertas totales: {open_incidencias}
- Pendientes totales: {pending_incidencias}
- Cerradas totales: {closed_incidencias}
- Críticas totales: {critical_incidencias}
- Promedio de resolución histórico: {avg_resolution_time}h

INCIDENCIAS POR CATEGORÍA (HISTÓRICO):
{categories_breakdown}

ÚLTIMAS INCIDENCIAS REGISTRADAS (CON FECHA):
{recent_incidencias_list}

PREGUNTA DEL USUARIO:
{user_pregunta}

Responde en español, de forma clara, accionable y precisa con las fechas."""


def build_prompt(context: dict, pregunta: str) -> tuple[str, str]:
    user = USER_PROMPT.format(
        fecha_actual=context.get("fecha_actual", "Desconocida"),
        semana_total=context.get("semana_total", 0),
        semana_abiertas=context.get("semana_abiertas", 0),
        semana_criticas=context.get("semana_criticas", 0),
        semana_cerradas=context.get("semana_cerradas", 0),
        semana_detalle=context.get("semana_detalle", "(sin incidencias esta semana)"),
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
