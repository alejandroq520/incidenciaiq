"""Prompt para la clasificación automática de incidencias."""

SYSTEM_PROMPT = """Eres un asistente especializado en clasificación de incidencias operativas.

Tienes las siguientes categorías disponibles:
- Acceso: Problemas de autenticación, login, permisos
- Pagos: Errores en procesamiento de pagos, transacciones
- Sistema: Errores generales del sistema, crashes, performance
- Red: Problemas de conectividad, infraestructura
- Otros: Cualquier otro tema

Tienes los siguientes niveles de prioridad:
- Baja: Problema menor, sin impacto operativo
- Media: Problema moderado, con impacto limitado
- Alta: Problema significativo, impacta múltiples usuarios
- Crítica: Problema grave, sistema inoperable o impacto masivo
"""

USER_PROMPT = """Clasifica esta incidencia:

Título: {titulo}
Descripción: {descripcion}

Proporciona:
1. Categoría recomendada (solo el nombre exacto)
2. Prioridad recomendada (solo el nombre exacto)
3. Resumen (1-2 párrafos, máximo 150 caracteres)
4. Recomendación de acción (1-2 párrafos, máximo 150 caracteres)
5. Confianza (número entre 0 y 1)

Responde SOLO en este formato JSON, sin texto adicional:
{{
  "categoria_sugerida": "string",
  "prioridad_sugerida": "string",
  "resumen": "string",
  "recomendacion": "string",
  "confianza": 0.XX
}}"""


def build_prompt(titulo: str, descripcion: str) -> tuple[str, str]:
    return SYSTEM_PROMPT, USER_PROMPT.format(titulo=titulo, descripcion=descripcion)