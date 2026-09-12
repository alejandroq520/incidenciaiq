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