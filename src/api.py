from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from typing import Optional
import uvicorn

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
NEO4J_URI      = "neo4j://127.0.0.1:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "bigdata2025"

app = FastAPI(
    title="API - Caso Penal Colombia",
    description="""
    API REST para consultar entidades y relaciones del caso de acceso carnal violento agravado
    extraídas desde la audiencia del Tribunal Superior de Bogotá (24 Oct 2025).

    **Radicado:** 110016721202000054
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# CONEXIÓN A NEO4J
# ─────────────────────────────────────────────
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_query(query: str, params: dict = {}):
    with driver.session() as session:
        result = session.run(query, params)
        return [dict(record) for record in result]

# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    return {
        "mensaje": "API del Caso Penal - Tribunal Superior de Bogotá",
        "radicado": "110016721202000054",
        "audiencia": "24 de octubre de 2025",
        "documentacion": "/docs"
    }


@app.get("/entidades", tags=["Entidades"])
def listar_entidades(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: Persona, Organización, Lugar, Delito, Norma, Prueba, Actuación, Jurisprudencia, Pena")
):
    """
    Retorna todas las entidades del caso.
    Opcionalmente puedes filtrar por tipo usando el parámetro **tipo**.
    """
    if tipo:
        query = """
            MATCH (n {label: $tipo})
            RETURN n.nodeId AS id, n.label AS tipo, n.nombre AS nombre,
                   n.rol AS rol, n.descripcion AS descripcion,
                   n.fecha AS fecha, n.identificacion AS identificacion
            ORDER BY n.nodeId
        """
        resultado = run_query(query, {"tipo": tipo})
    else:
        query = """
            MATCH (n)
            WHERE n.nodeId IS NOT NULL
            RETURN n.nodeId AS id, n.label AS tipo, n.nombre AS nombre,
                   n.rol AS rol, n.descripcion AS descripcion,
                   n.fecha AS fecha, n.identificacion AS identificacion
            ORDER BY n.label, n.nodeId
        """
        resultado = run_query(query)

    if not resultado:
        raise HTTPException(status_code=404, detail=f"No se encontraron entidades{' de tipo ' + tipo if tipo else ''}.")

    return {
        "total": len(resultado),
        "filtro_tipo": tipo or "todos",
        "entidades": resultado
    }


@app.get("/entidades/tipos", tags=["Entidades"])
def listar_tipos():
    """
    Retorna los tipos de entidades disponibles y cuántas hay de cada uno.
    """
    query = """
        MATCH (n)
        WHERE n.label IS NOT NULL
        RETURN n.label AS tipo, count(n) AS cantidad
        ORDER BY cantidad DESC
    """
    resultado = run_query(query)
    return {
        "tipos": resultado
    }


@app.get("/entidades/buscar", tags=["Entidades"])
def buscar_entidad(
    nombre: str = Query(..., description="Nombre o parte del nombre de la entidad a buscar")
):
    """
    Busca entidades cuyo nombre contenga el texto ingresado (búsqueda parcial, sin distinción de mayúsculas).
    """
    query = """
        MATCH (n)
        WHERE toLower(n.nombre) CONTAINS toLower($nombre)
        RETURN n.nodeId AS id, n.label AS tipo, n.nombre AS nombre,
               n.rol AS rol, n.descripcion AS descripcion
        ORDER BY n.label, n.nombre
    """
    resultado = run_query(query, {"nombre": nombre})

    if not resultado:
        raise HTTPException(status_code=404, detail=f"No se encontró ninguna entidad con el nombre '{nombre}'.")

    return {
        "total": len(resultado),
        "busqueda": nombre,
        "entidades": resultado
    }


@app.get("/entidades/{id}", tags=["Entidades"])
def obtener_entidad(id: str):
    """
    Retorna el detalle completo de una entidad por su ID (ej: P001, O001, L001, D001).
    """
    query = """
        MATCH (n {nodeId: $id})
        RETURN n.nodeId AS id, n.label AS tipo, n.nombre AS nombre,
               n.rol AS rol, n.descripcion AS descripcion,
               n.fecha AS fecha, n.identificacion AS identificacion,
               n.correo AS correo, n.telefono AS telefono,
               n.direccion AS direccion, n.tipo AS subtipo
    """
    resultado = run_query(query, {"id": id})

    if not resultado:
        raise HTTPException(status_code=404, detail=f"No se encontró la entidad con ID '{id}'.")

    return resultado[0]


@app.get("/entidades/{id}/relaciones", tags=["Relaciones"])
def obtener_relaciones(
    id: str,
    direccion: Optional[str] = Query("ambas", description="Dirección: 'salientes', 'entrantes' o 'ambas'")
):
    """
    Retorna todas las relaciones de una entidad por su ID.
    Puedes filtrar por dirección: **salientes**, **entrantes** o **ambas** (por defecto).
    """
    # Verificar que la entidad existe
    check = run_query("MATCH (n {nodeId: $id}) RETURN n.nodeId AS id", {"id": id})
    if not check:
        raise HTTPException(status_code=404, detail=f"No se encontró la entidad con ID '{id}'.")

    if direccion == "salientes":
        query = """
            MATCH (origen {nodeId: $id})-[r]->(destino)
            RETURN
                origen.nodeId AS origen_id,
                origen.nombre AS origen_nombre,
                origen.label AS origen_tipo,
                r.tipo AS relacion,
                r.descripcion AS descripcion_relacion,
                r.fecha AS fecha,
                destino.nodeId AS destino_id,
                destino.nombre AS destino_nombre,
                destino.label AS destino_tipo
            ORDER BY r.tipo
        """
    elif direccion == "entrantes":
        query = """
            MATCH (origen)-[r]->(destino {nodeId: $id})
            RETURN
                origen.nodeId AS origen_id,
                origen.nombre AS origen_nombre,
                origen.label AS origen_tipo,
                r.tipo AS relacion,
                r.descripcion AS descripcion_relacion,
                r.fecha AS fecha,
                destino.nodeId AS destino_id,
                destino.nombre AS destino_nombre,
                destino.label AS destino_tipo
            ORDER BY r.tipo
        """
    else:  # ambas
        query = """
            MATCH (origen)-[r]->(destino)
            WHERE origen.nodeId = $id OR destino.nodeId = $id
            RETURN
                origen.nodeId AS origen_id,
                origen.nombre AS origen_nombre,
                origen.label AS origen_tipo,
                r.tipo AS relacion,
                r.descripcion AS descripcion_relacion,
                r.fecha AS fecha,
                destino.nodeId AS destino_id,
                destino.nombre AS destino_nombre,
                destino.label AS destino_tipo
            ORDER BY r.tipo
        """

    resultado = run_query(query, {"id": id})

    if not resultado:
        raise HTTPException(status_code=404, detail=f"La entidad '{id}' no tiene relaciones en dirección '{direccion}'.")

    return {
        "entidad_id": id,
        "direccion": direccion,
        "total_relaciones": len(resultado),
        "relaciones": resultado
    }


@app.get("/entidades/{id}/vecinos", tags=["Relaciones"])
def obtener_vecinos(id: str):
    """
    Retorna todas las entidades directamente conectadas a la entidad con el ID dado,
    junto con el tipo de relación que las une.
    """
    check = run_query("MATCH (n {nodeId: $id}) RETURN n.nodeId AS id", {"id": id})
    if not check:
        raise HTTPException(status_code=404, detail=f"No se encontró la entidad con ID '{id}'.")

    query = """
        MATCH (n {nodeId: $id})-[r]-(vecino)
        RETURN DISTINCT
            vecino.nodeId AS id,
            vecino.nombre AS nombre,
            vecino.label AS tipo,
            vecino.rol AS rol,
            collect(DISTINCT r.tipo) AS tipos_relacion
        ORDER BY vecino.label, vecino.nombre
    """
    resultado = run_query(query, {"id": id})

    return {
        "entidad_id": id,
        "total_vecinos": len(resultado),
        "vecinos": resultado
    }


@app.get("/relaciones", tags=["Relaciones"])
def listar_relaciones(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de relación, ej: ACUSADO_DE, VICTIMIZO_A, TESTIGO_EN")
):
    """
    Retorna todas las relaciones del grafo.
    Opcionalmente filtra por tipo de relación con el parámetro **tipo**.
    """
    if tipo:
        query = """
            MATCH (a)-[r {tipo: $tipo}]->(b)
            RETURN
                a.nodeId AS origen_id, a.nombre AS origen_nombre, a.label AS origen_tipo,
                r.tipo AS relacion, r.descripcion AS descripcion, r.fecha AS fecha,
                b.nodeId AS destino_id, b.nombre AS destino_nombre, b.label AS destino_tipo
            ORDER BY a.nodeId
        """
        resultado = run_query(query, {"tipo": tipo})
    else:
        query = """
            MATCH (a)-[r]->(b)
            RETURN
                a.nodeId AS origen_id, a.nombre AS origen_nombre, a.label AS origen_tipo,
                r.tipo AS relacion, r.descripcion AS descripcion, r.fecha AS fecha,
                b.nodeId AS destino_id, b.nombre AS destino_nombre, b.label AS destino_tipo
            ORDER BY r.tipo, a.nodeId
        """
        resultado = run_query(query)

    if not resultado:
        raise HTTPException(status_code=404, detail="No se encontraron relaciones.")

    return {
        "total": len(resultado),
        "filtro_tipo": tipo or "todas",
        "relaciones": resultado
    }


@app.get("/relaciones/tipos", tags=["Relaciones"])
def listar_tipos_relaciones():
    """
    Retorna todos los tipos de relaciones disponibles en el grafo y cuántas hay de cada uno.
    """
    query = """
        MATCH ()-[r]->()
        RETURN r.tipo AS tipo, count(r) AS cantidad
        ORDER BY cantidad DESC
    """
    resultado = run_query(query)
    return {
        "tipos_relacion": resultado
    }


@app.get("/estadisticas", tags=["General"])
def estadisticas():
    """
    Retorna estadísticas generales del grafo del caso.
    """
    total_nodos = run_query("MATCH (n) RETURN count(n) AS total")[0]["total"]
    total_rels  = run_query("MATCH ()-[r]->() RETURN count(r) AS total")[0]["total"]
    por_tipo    = run_query("MATCH (n) WHERE n.label IS NOT NULL RETURN n.label AS tipo, count(n) AS cantidad ORDER BY cantidad DESC")
    por_rel     = run_query("MATCH ()-[r]->() RETURN r.tipo AS tipo, count(r) AS cantidad ORDER BY cantidad DESC LIMIT 10")

    return {
        "total_entidades": total_nodos,
        "total_relaciones": total_rels,
        "entidades_por_tipo": por_tipo,
        "top_10_relaciones": por_rel
    }


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)