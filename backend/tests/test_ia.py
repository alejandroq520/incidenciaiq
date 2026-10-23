"""Pruebas básicas de humo para la lógica central del servicio."""

from app.services.servicio_ia import clasificar_heuristica


def test_clasificar_heuristica_access_critical():
    result = clasificar_heuristica(
        "Caída de acceso masiva",
        "Todos los usuarios no pueden iniciar sesión, error de autenticación masivo.",
    )
    assert result["categoria_sugerida"] == "Acceso"
    assert result["prioridad_sugerida"] == "Crítica"
    assert 0 <= result["confianza"] <= 1


def test_clasificar_heuristica_payment():
    result = clasificar_heuristica(
        "Pago rechazado",
        "Las transacciones con tarjeta están siendo rechazadas en el checkout.",
    )
    assert result["categoria_sugerida"] == "Pagos"


def test_clasificar_heuristica_unknown_defaults():
    result = clasificar_heuristica("Hola", "Reporte genérico sin palabras clave.")
    assert result["categoria_sugerida"] in ("Acceso", "Pagos", "Sistema", "Red", "Otros")


def test_construir_justificacion_con_resultado_heuristica():
    from app.services.servicio_ia import _construir_justificacion

    heuristic_data = clasificar_heuristica("Pago rechazado", "Falla en pasarela de pagos con tarjeta.")
    # Prueba pasando directamente el dict de clasificar_heuristica o su subdict de evidence
    justificacion = _construir_justificacion(
        fuente="heuristic",
        evidence=heuristic_data,
        ref_incidencia=None,
        similarity=0.0,
        categoria="Pagos",
    )
    assert "Clasificación por reglas" in justificacion
    assert "pago" in justificacion or "pasarela" in justificacion or "tarjeta" in justificacion


def test_respuesta_plantilla_semana_con_y_sin_incidencias():
    from app.services.servicio_ia import _respuesta_plantilla

    ctx_vacio = {
        "semana_total": 0,
        "semana_abiertas": 0,
        "semana_criticas": 0,
        "semana_cerradas": 0,
        "ultima_info": "INC-120 ('Falla en DB') el 2026-09-10",
        "total_incidencias": 120,
        "open_incidencias": 30,
        "critical_incidencias": 10,
        "pending_incidencias": 5,
        "closed_incidencias": 85,
        "avg_resolution_time": 12.5,
        "categories_breakdown": "- Sistema: 40",
    }
    resp_vacio = _respuesta_plantilla(ctx_vacio, "Resume las incidencias de esta semana")
    assert "no se registraron nuevas incidencias" in resp_vacio
    assert "INC-120" in resp_vacio

    ctx_con_datos = dict(ctx_vacio)
    ctx_con_datos["semana_total"] = 3
    ctx_con_datos["semana_abiertas"] = 2
    ctx_con_datos["semana_criticas"] = 1
    ctx_con_datos["semana_cerradas"] = 1
    ctx_con_datos["semana_resumen_titulos"] = "INC-121: 'Error de login' (23/10)"
    resp_datos = _respuesta_plantilla(ctx_con_datos, "Resume las incidencias de esta semana")
    assert "se registraron 3 incidencias" in resp_datos
    assert "INC-121" in resp_datos

