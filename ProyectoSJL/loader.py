"""
grafos/loader.py
Loader avanzado (OSM + CSV). Provee:
- construir_desde_osm(place_name, network_type) -> (lista_ady, nodos_info, grafo_osm)
- carga_csvs(aristas_csv, nodos_csv) -> (lista_ady, nodos_info)
- guarda_csvs(lista_ady, nodos_info, aristas_csv, nodos_csv)
"""

import csv, os
from collections import deque

# osmnx es opcional; si no está, las funciones OSM fallarán con RuntimeError
try:
    import osmnx as ox
except Exception:
    ox = None

VELOCIDAD_KMH = 30.0

def metros_a_minutos(dist_m):
    distancia_km = dist_m / 1000.0
    minutos = (distancia_km / VELOCIDAD_KMH) * 60.0
    return round(minutos, 2)

def construir_desde_osm(place_name="San Juan de Lurigancho, Lima, Peru", network_type='drive'):
    if ox is None:
        raise RuntimeError("osmnx no está instalado; instala osmnx o usa CSV.")
    G = ox.graph_from_place(place_name, network_type=network_type, simplify=True)
    lista_ady = {}
    nodos_info = {}
    # nodos
    for nodo, data in G.nodes(data=True):
        x = data.get('x', 0.0); y = data.get('y', 0.0)
        nodos_info[nodo] = (x, y)
        lista_ady[nodo] = []
    # aristas
    for u, v, key, data in G.edges(data=True, keys=True):
        length = data.get('length', 100.0)
        tiempo = metros_a_minutos(length)
        lista_ady[u].append((v, float(length), tiempo))
        oneway = data.get('oneway', None)
        if oneway in (False, 'false', 'False', 0, None):
            lista_ady[v].append((u, float(length), tiempo))
    return lista_ady, nodos_info, G

def carga_csvs(aristas_csv='grafo_sjl_osm.csv', nodos_csv='nodos_sjl_osm.csv'):
    if not os.path.exists(aristas_csv) or not os.path.exists(nodos_csv):
        raise FileNotFoundError(f"CSV no encontrado: {aristas_csv} o {nodos_csv}")
    nodos_info = {}
    lista_ady = {}
    with open(nodos_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodo = int(row['nodo_id']) if row['nodo_id'].isdigit() else row['nodo_id']
            lat = float(row['latitud']); lon = float(row['longitud'])
            nodos_info[nodo] = (lon, lat)
            lista_ady[nodo] = []
    with open(aristas_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row['origen']) if row['origen'].isdigit() else row['origen']
            v = int(row['destino']) if row['destino'].isdigit() else row['destino']
            d = float(row.get('distancia_metros', 0.0))
            t = float(row.get('tiempo_minutos', 0.0))
            if u not in lista_ady: lista_ady[u] = []
            if v not in lista_ady: lista_ady[v] = []
            lista_ady[u].append((v, d, t))
            lista_ady[v].append((u, d, t))
    return lista_ady, nodos_info

def guarda_csvs(lista_ady, nodos_info, aristas_csv='grafo_sjl_osm_out.csv', nodos_csv='nodos_sjl_osm_out.csv'):
    seen = set(); rows = []
    for u, vecinos in lista_ady.items():
        for v, d, t in vecinos:
            par = (u, v) if u <= v else (v, u)
            if par in seen: continue
            seen.add(par)
            rows.append({'origen': par[0], 'destino': par[1], 'distancia_metros': d, 'tiempo_minutos': t, 'nombre_calle': 'Sin nombre'})
    with open(aristas_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origen','destino','distancia_metros','tiempo_minutos','nombre_calle'])
        writer.writeheader()
        for r in rows: writer.writerow(r)
    with open(nodos_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['nodo_id','latitud','longitud'])
        writer.writeheader()
        for nodo, (x,y) in nodos_info.items():
            writer.writerow({'nodo_id': nodo, 'latitud': y, 'longitud': x})
