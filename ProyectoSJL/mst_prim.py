"""
grafos/mst_prim.py
Prim instrumentado: mantiene contador de aristas consideradas y tiempo.
Entrada: grafo dict-of-dicts {u: {v: peso}}
Salida: mst_list (tripletas), costoTotal, stats
"""

import heapq
import time
try:
    from graphviz import Graph
except Exception:
    Graph = None

class MSTPrim:
    def __init__(self, grafo_dict_dict):
        self.grafo = grafo_dict_dict
        self.mst = []
        self.costoTotal = 0

    def Prim(self):
        t0 = time.time()
        if not self.grafo:
            stats = {"algoritmo": "Prim", "V":0, "E_aprox":0, "aristas_consideradas":0, "tiempo_algo_s":0, "complejidad_teorica":"O(E log V)"}
            return self.mst, self.costoTotal, stats

        nodoInicial = next(iter(self.grafo))
        visitados = set([nodoInicial])
        aristas = [(peso, nodoInicial, vecino) for vecino, peso in self.grafo[nodoInicial].items()]
        heapq.heapify(aristas)
        aristas_consideradas = 0
        while aristas:
            peso, u, v = heapq.heappop(aristas)
            aristas_consideradas += 1
            if v not in visitados:
                visitados.add(v)
                self.mst.append((u, v, peso))
                self.costoTotal += peso
                for vv, pp in self.grafo[v].items():
                    if vv not in visitados:
                        heapq.heappush(aristas, (pp, v, vv))
        t1 = time.time()
        V = len(self.grafo)
        E_aprox = sum(len(self.grafo[u]) for u in self.grafo) // 2
        stats = {
            "algoritmo": "Prim",
            "V": V,
            "E_aprox": E_aprox,
            "aristas_consideradas": aristas_consideradas,
            "aristas_en_mst": len(self.mst),
            "costo_total": self.costoTotal,
            "tiempo_algo_s": round(t1 - t0, 6),
            "complejidad_teorica": "O(E log V)"
        }
        return self.mst, self.costoTotal, stats

    def getMST(self):
        return self.mst

    def getCostoTotal(self):
        return self.costoTotal

    def dibujaMST(self, filename='mst_prim'):
        if Graph is None:
            raise RuntimeError("graphviz no disponible")
        g = Graph('mst_prim', format='png')
        g.graph_attr['rankdir'] = 'LR'
        for u, v, p in self.mst:
            g.edge(str(u), str(v), label=str(p))
        g.render(filename, format='png', cleanup=True)
        return f'{filename}.png'
