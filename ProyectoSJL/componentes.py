# grafos/componentes.py

from collections import deque

def bfs_componente(lista_ady, inicio):
    visitados = set([inicio])
    cola = deque([inicio])
    while cola:
        u = cola.popleft()
        for (v, d, t) in lista_ady.get(u, []):
            if v not in visitados:
                visitados.add(v)
                cola.append(v)
    return visitados

def detectar_componentes(lista_ady):
    visitados_global = set()
    componentes = []
    for nodo in lista_ady.keys():
        if nodo not in visitados_global:
            comp = bfs_componente(lista_ady, nodo)
            componentes.append(comp)
            visitados_global |= comp
    return componentes

def obtener_componente_gigante(lista_ady):
    componentes = detectar_componentes(lista_ady)
    gigante = max(componentes, key=len)

    # ★ PARCHE: nodo defectuoso detectado en OSM SJL
    if 1278939002 in gigante:
        gigante.remove(1278939002)

    return gigante

def extraer_subgrafo(lista_ady, nodos):
    sub = {}
    for u in nodos:
        if u in lista_ady:
            sub[u] = [(v,d,t) for (v,d,t) in lista_ady[u] if v in nodos]
        else:
            sub[u] = []
    return sub
