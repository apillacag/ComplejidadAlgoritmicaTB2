"""
grafos/dijkstra.py
Implementación de Dijkstra que devuelve:
- distancias: dict
- caminos: dict
- stats: dict con métricas internas (nodos_explorados, aristas_relajadas, largo_camino, peso_total, tiempo_algo)
Estilo: similar a los apuntes, con instrumentación para Hito3.
"""

import heapq
import time

def Dijkstra(lag, inicio, destino=None):
    """
    lag: {u: [(v,p), ...], ...}
    inicio: nodo origen
    destino: (opcional) nodo destino para poder detener la búsqueda temprano
    Retorna: (distancias, caminos, stats)
    """
    t0 = time.time()                       # tiempo inicio (interno)
    V = len(lag)
    # inicialización
    distancias = {n: float('inf') for n in lag}
    distancias[inicio] = 0
    caminos = {n: [] for n in lag}
    caminos[inicio] = [inicio]

    # frontera: (peso_parcial, nodo, camino_parcial)
    frontera = [(0, inicio, [inicio])]
    visitados = set()
    nodos_explorados = 0
    aristas_relajadas = 0

    while frontera:
        peso, nodo, camino = heapq.heappop(frontera)
        if nodo in visitados:
            continue
        # marcar como explorado
        visitados.add(nodo)
        nodos_explorados += 1
        distancias[nodo] = peso
        caminos[nodo] = camino

        # detener temprano si llegamos al destino
        if destino is not None and nodo == destino:
            break

        # relajar aristas
        for v, w in lag.get(nodo, []):
            if v in visitados:
                continue
            nuevo = peso + w
            aristas_relajadas += 1
            if nuevo < distancias.get(v, float('inf')):
                distancias[v] = nuevo
                heapq.heappush(frontera, (nuevo, v, camino + [v]))

    t1 = time.time()
    # construir estadísticas
    stats = {
        "algoritmo": "Dijkstra",
        "V": V,
        "E_aproximado": sum(len(lag[u]) for u in lag) // 2 if V>0 else 0,
        "nodos_explorados": nodos_explorados,
        "aristas_relajadas": aristas_relajadas,
        "tiempo_algo_s": round(t1 - t0, 6),
        "complejidad_teorica": "O((V + E) log V)"
    }

    # resumen relativo a la ruta si se especificó destino y existe camino
    if destino is not None:
        if distancias.get(destino, float('inf')) < float('inf'):
            camino_dest = caminos[destino]
            stats.update({
                "origen": inicio,
                "destino": destino,
                "distancia_total": distancias[destino],
                "tiempo_estimado_min": None,  # si quieres convertir distancia->tiempo, hazlo en GUI
                "largo_camino_nodos": len(camino_dest),
                "ruta": camino_dest
            })
        else:
            stats.update({
                "origen": inicio,
                "destino": destino,
                "distancia_total": float('inf'),
                "largo_camino_nodos": 0,
                "ruta": []
            })

    return distancias, caminos, stats
