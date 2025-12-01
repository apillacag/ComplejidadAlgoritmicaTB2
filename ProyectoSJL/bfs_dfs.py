"""
grafos/bfs_dfs.py
BFS y DFS instrumentados. DFS devuelve métricas como:
- total_nodos_visitados, profundidad_maxima, grafo_conectado (estimado), tiempo_algo
"""

from collections import deque
import time

def BFS(lista_ady, inicio):
    """BFS simple (sin stats extendidas)."""
    visitados = set([inicio])
    q = deque([inicio])
    orden = []
    while q:
        u = q.popleft()
        orden.append(u)
        for v, d, t in lista_ady.get(u, []):
            if v not in visitados:
                visitados.add(v)
                q.append(v)
    return orden

def DFS(lista_ady, inicio):
    """
    DFS iterativa instrumentada:
    Retorna: (orden, stats)
    stats contiene: total_visitados, profundidad_maxima_aproximada, grafo_conectado(por componente), tiempo_algo_s
    """
    t0 = time.time()
    pila = [(inicio, 0)]   # (nodo, profundidad)
    visitados = set()
    orden = []
    profundidad_max = 0
    while pila:
        u, prof = pila.pop()
        if u in visitados:
            continue
        visitados.add(u)
        orden.append(u)
        if prof > profundidad_max:
            profundidad_max = prof
        # añadimos vecinos (no visitados)
        for v, d, t in lista_ady.get(u, []):
            if v not in visitados:
                pila.append((v, prof + 1))
    t1 = time.time()

    # estimación de conectividad: si visitamos todos los nodos => conectado (para el componente usado)
    total_nodos = len(lista_ady)
    grafo_conectado = (len(visitados) == total_nodos)

    stats = {
        "algoritmo": "DFS",
        "total_nodos_visitados": len(visitados),
        "profundidad_maxima": profundidad_max,
        "grafo_conectado": grafo_conectado,
        "tiempo_algo_s": round(t1 - t0, 6),
        "complejidad_teorica": "O(V + E)"
    }
    return orden, stats
