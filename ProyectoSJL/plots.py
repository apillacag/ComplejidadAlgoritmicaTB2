"""
visualizacion/plots.py
Dibujo con osmnx si está disponible (mapa real), fallback a graphviz.
"""

try:
    import osmnx as ox
    import matplotlib.pyplot as plt
    OSMNX_AVAILABLE = True
except Exception:
    OSMNX_AVAILABLE = False

try:
    from graphviz import Graph
    GRAPHVIZ_AVAILABLE = True
except Exception:
    Graph = None
    GRAPHVIZ_AVAILABLE = False

def dibuja_aristas_list(aristas, filename='aristas'):
    if not GRAPHVIZ_AVAILABLE:
        raise RuntimeError('graphviz no disponible')
    g = Graph('aristas', format='png'); g.graph_attr['rankdir'] = 'LR'
    for u,v,p in aristas:
        g.edge(str(u), str(v), label=str(p))
    g.render(filename, format='png', cleanup=True); return f'{filename}.png'

def dibuja_subgrafo(sub_ady, nodos_info=None, filename='subgrafo'):
    if OSMNX_AVAILABLE and nodos_info:
        xs=[]; ys=[]; labs=[]
        for u in sub_ady:
            if u in nodos_info:
                x,y = nodos_info[u]; xs.append(x); ys.append(y); labs.append(str(u))
        fig, ax = plt.subplots(figsize=(8,8)); ax.scatter(xs, ys, s=10)
        for i,lab in enumerate(labs): ax.annotate(lab, (xs[i], ys[i]), fontsize=6)
        out = f'{filename}.png'; fig.savefig(out, dpi=200); plt.close(fig); return out
    else:
        if not GRAPHVIZ_AVAILABLE:
            raise RuntimeError('Ni osmnx ni graphviz disponibles')
        g = Graph('sub', format='png'); g.graph_attr['rankdir']='LR'
        added=set()
        for u in sub_ady: g.node(str(u))
        for u in sub_ady:
            for v,d,t in sub_ady[u]:
                par = (u,v) if str(u)<=str(v) else (v,u)
                if par in added: continue
                added.add(par)
                g.edge(str(par[0]), str(par[1]), label=str(int(d))+'m')
        g.render(filename, format='png', cleanup=True); return f'{filename}.png'

def mostrar_mst(mst_list):
    try: return dibuja_aristas_list(mst_list, filename='mst_plot')
    except Exception: return None

def mostrar_ruta(camino):
    try:
        if not camino or len(camino)<2: return None
        aristas = [(camino[i], camino[i+1], 1) for i in range(len(camino)-1)]
        return dibuja_aristas_list(aristas, filename='ruta_plot')
    except Exception:
        return None
