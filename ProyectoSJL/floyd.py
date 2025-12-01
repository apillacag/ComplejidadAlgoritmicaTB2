"""
grafos/floyd.py
Floyd–Warshall instrumentado:
- devuelve dist, next_hop, nodes, stats (tiempo, V, complejidad)
"""

import time

def floyd_warshall(lista_ady, weight_type='distancia'):
    t0 = time.time()
    nodes = sorted(list(lista_ady.keys()))
    V = len(nodes)
    # inicialización
    dist = {u: {v: float('inf') for v in nodes} for u in nodes}
    next_hop = {u: {v: None for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 0
        next_hop[u][u] = u
    # cargar pesos
    for u, vecinos in lista_ady.items():
        for v, d, t in vecinos:
            peso = d if weight_type == 'distancia' else t
            if peso < dist[u][v]:
                dist[u][v] = peso
                next_hop[u][v] = v
    # algoritmo principal
    for k in nodes:
        if V == 0:
            break
        for i in nodes:
            if dist[i][k] == float('inf'):
                continue
            for j in nodes:
                if dist[k][j] == float('inf'):
                    continue
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_hop[i][j] = next_hop[i][k]
    t1 = time.time()
    stats = {
        "algoritmo": "Floyd-Warshall",
        "V": V,
        "matriz_generada": (V, V),
        "tiempo_algo_s": round(t1 - t0, 6),
        "complejidad_teorica": "O(V^3)"
    }
    return dist, next_hop, nodes, stats

def reconstruir_camino(next_hop, u, v):
    if u not in next_hop or v not in next_hop[u]:
        return []
    if next_hop[u][v] is None:
        return []
    camino = [u]
    cur = u
    while cur != v:
        cur = next_hop[cur][v]
        if cur is None:
            return []
        camino.append(cur)
    return camino
