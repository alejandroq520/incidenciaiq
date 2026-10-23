"""Test suite integral para verificar todos los endpoints y flujos de IncidenciaIQ."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_creacion_y_analisis_automatico_incidencia():
    payload = {
        "titulo": "Caída del enlace de red principal",
        "descripcion": "Se ha caído el enlace de fibra principal en el datacenter. Pérdida total de conectividad y paquetes.",
        "categoria_id": 4,  # Red
        "prioridad_id": 4,  # Crítica
        "creado_por": "Analista QA",
    }
    res = client.post("/api/incidencias", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["titulo"] == payload["titulo"]
    assert data["estado"]["name"] == "Abierta"

    # Verificar que el análisis IA se ejecutó automáticamente y no es None
    analisis = data.get("analisis_ia")
    assert analisis is not None
    assert analisis["categoria_sugerida"] in ("Red", "Sistema", "Otros")
    assert analisis["prioridad_sugerida"] in ("Crítica", "Alta", "Media", "Baja")
    assert 0 <= analisis["confianza"] <= 1
    assert analisis["confirmado"] is False
    assert len(analisis["resumen"]) > 0


def test_listar_y_filtrar_incidencias():
    # 1. Paginación y listado base
    res = client.get("/api/incidencias?skip=0&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) <= 10

    # 2. Búsqueda por texto (en título o descripción)
    res_search = client.get("/api/incidencias?search=enlace")
    assert res_search.status_code == 200
    items = res_search.json()["items"]
    assert any("enlace" in i["titulo"].lower() for i in items)

    # 3. Filtrar por estado
    res_estado = client.get("/api/incidencias?estado_id=1")
    assert res_estado.status_code == 200
    assert all(i["estado"] == "Abierta" for i in res_estado.json()["items"])


def test_detalle_y_actualizacion_incidencia():
    # Crear una incidencia para el flujo completo
    payload = {
        "titulo": "Incidencia para prueba de actualización",
        "descripcion": "Descripción detallada para probar cambios de estado e historial.",
        "categoria_id": 3,
        "prioridad_id": 2,
        "creado_por": "Tester",
    }
    creada = client.post("/api/incidencias", json=payload).json()
    inc_id = creada["id"]

    # 1. Obtener detalle
    res_det = client.get(f"/api/incidencias/{inc_id}")
    assert res_det.status_code == 200
    det = res_det.json()
    assert det["id"] == inc_id
    assert len(det["historial"]) >= 1

    # 2. Actualizar prioridad y notas
    res_up = client.put(
        f"/api/incidencias/{inc_id}",
        json={"prioridad_id": 3, "notas": "Nota de prueba", "creado_por": "Admin"},
    )
    assert res_up.status_code == 200
    actualizada = res_up.json()
    assert actualizada["prioridad"]["id"] == 3
    assert actualizada["notas"] == "Nota de prueba"

    # 3. Marcar como resuelta (cerrada, estado_id = 3) y verificar cálculo de tiempo de resolución
    res_close = client.put(
        f"/api/incidencias/{inc_id}",
        json={"estado_id": 3, "creado_por": "Admin"},
    )
    assert res_close.status_code == 200
    cerrada = res_close.json()
    assert cerrada["estado"]["name"] == "Cerrada"
    assert cerrada["tiempo_resolucion_minutos"] is not None
    assert cerrada["resuelto_en"] is not None

    # 4. Confirmar análisis IA
    res_conf = client.put(
        f"/api/incidencias/{inc_id}/analisis-ia/confirmar",
        json={"confirmado": True},
    )
    assert res_conf.status_code == 200
    confirmada = res_conf.json()
    assert confirmada["analisis_ia"]["confirmado"] is True


def test_endpoints_analitica():
    # Métricas generales
    res_m = client.get("/api/analitica/metricas?period=30d")
    assert res_m.status_code == 200
    m = res_m.json()
    assert "total_incidencias" in m
    assert "opened_incidencias" in m
    assert "closed_incidencias" in m
    assert "sla_compliance_percentage" in m

    # Por categoría
    res_c = client.get("/api/analitica/por-categoria?period=30d")
    assert res_c.status_code == 200
    assert "categorias" in res_c.json()

    # Tendencia
    res_t = client.get("/api/analitica/tendencia?period=30d")
    assert res_t.status_code == 200
    assert "data" in res_t.json()

    # Tiempo de resolución
    res_r = client.get("/api/analitica/tiempo-resolucion?period=30d")
    assert res_r.status_code == 200
    assert "por_categoria" in res_r.json()


def test_endpoints_ia():
    # 1. Asistente de preguntas
    res_p = client.post("/api/ia/preguntar", json={"pregunta": "¿Cuántas incidencias críticas están abiertas?"})
    assert res_p.status_code == 200
    data_p = res_p.json()
    assert "respuesta" in data_p
    assert len(data_p["respuesta"]) > 0

    # 2. Perspectivas automáticas
    res_persp = client.get("/api/ia/perspectivas?period=30d")
    assert res_persp.status_code == 200
    assert "perspectivas" in res_persp.json()

    # 3. Evaluación del clasificador
    res_eval = client.get("/api/ia/evaluacion")
    assert res_eval.status_code == 200
    data_eval = res_eval.json()
    assert "precision" in data_eval
    assert "cobertura" in data_eval
    assert "por_fuente" in data_eval
    assert "por_categoria" in data_eval


def test_servicio_spa_frontend():
    # Ruta raíz
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "<html" in res_root.text.lower() or "<!doctype" in res_root.text.lower()

    # Ruta SPA interna (debe devolver el index.html)
    res_spa = client.get("/incidencias")
    assert res_spa.status_code == 200
    assert "<html" in res_spa.text.lower() or "<!doctype" in res_spa.text.lower()
