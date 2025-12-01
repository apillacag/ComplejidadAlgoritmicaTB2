"""
grafos/mst_kruskal.py
Kruskal instrumentado con Union-Find. Devuelve MST y estadísticas
"""

import time

class ConjuntoDisjunto:
    def __init__(self, vertices):
        self.padre = {v: v for v in vertices}
        self.altura = {v: 0 for v in vertices}

    def find(self, e):
        if self.padre[e] != e:
            self.padre[e] = self.find(self.padre[e])
        return self.padre[e]

    def union(self, nodo1, nodo2):
        rnodo1 = self.find(nodo1)
        rnodo2 = self.find(nodo2)
        if rnodo1 == rnodo2:
            return False
        if self.altura[rnodo1] > self.altura[rnodo2]:
            self.padre[rnodo2] = rnodo1
        elif self.altura[rnodo1] < self.altura[rnodo2]:
            self.padre[rnodo1] = rnodo2
        else:
            self.padre[rnodo2] = rnodo1
            self.altura[rnodo1] += 1
        return True

class MSTKruskal:
    def __init__(self, grafo_dict_dict):
        self.grafo = grafo_dict_dict
        self.mst = []
        self.costoTotal = 0

    def Kruskal(self):
        t0 = time.time()
        aristas = []
        seen = set()
        for u, vecinos in self.grafo.items():
            for v, peso in vecinos.items():
                par = tuple(sorted((u, v)))
                if par in seen:
                    continue
                seen.add(par)
                aristas.append((peso, u, v))
        aristas.sort()
        uf = ConjuntoDisjunto(self.grafo.keys())
        ciclos_omitidos = 0
        for peso, u, v in aristas:
            if uf.find(u) != uf.find(v):
                uf.union(u, v)
                self.mst.append((u, v, peso))
                self.costoTotal += peso
            else:
                ciclos_omitidos += 1
        t1 = time.time()
        V = len(self.grafo)
        E_aprox = len(aristas)
        stats = {
            "algoritmo": "Kruskal",
            "V": V,
            "E_aprox": E_aprox,
            "aristas_en_mst": len(self.mst),
            "ciclos_omitidos": ciclos_omitidos,
            "costo_total": self.costoTotal,
            "tiempo_algo_s": round(t1 - t0, 6),
            "complejidad_teorica": "O(E log E)"
        }
        return self.mst, self.costoTotal, stats

    def getMST(self):
        return self.mst

    def getCostoTotal(self):
        return self.costoTotal

    def dibujaMST(self, filename='mst_kruskal'):
        try:
            from graphviz import Graph
        except Exception:
            raise RuntimeError("graphviz no disponible")
        g = Graph('mst_kruskal', format='png')
        g.graph_attr['rankdir'] = 'LR'
        for u, v, p in self.mst:
            g.edge(str(u), str(v), label=str(p))
        g.render(filename, format='png', cleanup=True)
        return f'{filename}.png'
