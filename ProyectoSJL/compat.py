"""
grafos/compat.py
Adaptador: provee las funciones con los nombres que tu main.py importa:
- cargar_grafo_csv(archivo_aristas, archivo_nodos) -> lista_ady
- convertir_a_lista_vecinos(lista_ady) -> {u:[(v,p),...]}
- convertir_a_diccionario_pesos(lista_ady) -> {u:{v:p,...}, ...}
- mostrar_mst(mst_list) -> dibuja y retorna ruta de imagen (usa visualizacion.plots)
- mostrar_ruta(camino) -> dibuja y retorna ruta de imagen (simple)
"""

import csv
import os
from collections import defaultdict

# importo funciones ya creadas en nuestro proyecto modular (si existen)
try:
    from grafos.loader import carga_csvs
except Exception:
    carga_csvs = None

try:
    from visualizacion.plots import dibuja_aristas_list, dibuja_subgrafo
except Exception:
    dibuja_aristas_list = None
    dibuja_subgrafo = None

def cargar_grafo_csv(aristas_csv=None, nodos_csv=None):
    """
    Interfaz esperada por tu main.py:
    cargar_grafo_csv(archivo_aristas, archivo_nodos) -> lista_ady
    Si los argumentos son None, asume los nombres por defecto en carpeta actual.
    """
    # si la función carga_csvs está disponible, la usamos
    if carga_csvs is not None:
        # si el main te pasa las rutas, las pasamos; si no, usamos por defecto
        if aristas_csv and nodos_csv:
            # la función carga_csvs espera nombres por defecto; llamamos su versión original
            lista_ady, nodos_info = carga_csvs(aristas_csv, nodos_csv)
        else:
            lista_ady, nodos_info = carga_csvs()
        return lista_ady

    # alternativa: si no existe carga_csvs, intentamos leer CSV manualmente (compatibilidad)
    if aristas_csv is None:
        aristas_csv = 'grafo_sjl_osm.csv'
    if nodos_csv is None:
        nodos_csv = 'nodos_sjl_osm.csv'

    if not os.path.exists(aristas_csv) or not os.path.exists(nodos_csv):
        raise FileNotFoundError("No se encontraron los CSVs necesarios para cargar el grafo.")

    # reconstruir lista_ady desde CSV (versión ligera)
    lista_ady = defaultdict(list)
    # leer aristas
    with open(aristas_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row['origen']) if row['origen'].isdigit() else row['origen']
            v = int(row['destino']) if row['destino'].isdigit() else row['destino']
            d = float(row['distancia_metros'])
            t = float(row['tiempo_minutos'])
            lista_ady[u].append((v, d, t))
            lista_ady[v].append((u, d, t))
    return dict(lista_ady)


def convertir_a_lista_vecinos(lista_ady):
    """
    Convierte tu lista_ady {u: [(v,d,t),...], ...} a formato {u: [(v,p),...], ...}
    usando 'distancia' como peso (compatible con Dijkstra en grafos/dijkstra.py).
    """
    out = {}
    for u, vecinos in lista_ady.items():
        out[u] = []
        for v, d, t in vecinos:
            out[u].append((v, d))  # peso = distancia_metros
    return out


def convertir_a_diccionario_pesos(lista_ady):
    """
    Convierte lista_ady a dict-of-dicts {u: {v: peso, ...}, ...}
    usado por MSTPrim / MSTKruskal adaptadas al estilo del profesor.
    Peso = distancia (metros).
    """
    out = {}
    for u, vecinos in lista_ady.items():
        if u not in out:
            out[u] = {}
        for v, d, t in vecinos:
            # si ya existe, conservar el menor
            if v not in out[u] or d < out[u][v]:
                out[u][v] = d
    return out


def mostrar_mst(mst_list):
    """
    Wrapper: recibe mst_list = [(u,v,p), ...] y si graphviz/plots existe, dibuja la imagen.
    Retorna la ruta al archivo PNG si se generó, o None.
    """
    if dibuja_aristas_list is None:
        # no hay visualización disponible
        return None
    # dibuja_aristas_list espera [(u,v,p), ...]
    try:
        img = dibuja_aristas_list(mst_list, filename='mst_custom')
        return img
    except Exception:
        return None


def mostrar_ruta(camino):
    """
    Dibuja una ruta simple: convierte camino [n1,n2,...] en lista de aristas y manda a dibujar.
    Retorna la ruta del PNG o None.
    """
    if dibuja_aristas_list is None:
        return None
    if not camino or len(camino) < 2:
        return None
    aristas = []
    for i in range(len(camino) - 1):
        u = camino[i]; v = camino[i+1]
        aristas.append((u, v, 1))  # peso simbólico 1
    try:
        img = dibuja_aristas_list(aristas, filename='ruta_camino')
        return img
    except Exception:
        return None
