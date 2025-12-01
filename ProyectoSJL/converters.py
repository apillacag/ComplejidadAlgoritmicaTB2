"""
Convertidores: lista_ady -> formatos usados por algoritmos.
"""
def lista_ady_to_dict_dict(lista_ady, weight_type="distancia"):
    """
    Convierte tu lista de adyacencia:
        {u: [(v, dist, tiempo), ...]}
    a dict-of-dicts:
        {u: {v: peso}}
    Garantizando que TODOS los nodos estén presentes,
    incluso los que no tienen aristas salientes.
    """
    lag = {}

    # Crear claves vacías para todos los nodos
    for u in lista_ady:
        lag[u] = {}

    # Llenar pesos
    for u, adys in lista_ady.items():
        for triple in adys:
            if len(triple) == 3:
                v, dist, tiempo = triple
            elif len(triple) == 2:
                v, dist = triple
                tiempo = dist
            else:
                continue

            peso = dist if weight_type == "distancia" else tiempo
            lag[u][v] = peso

            # IMPORTANTE: asegurar que v exista también
            if v not in lag:
                lag[v] = {}

    return lag


def lista_ady_to_list_weighted(lista_ady, weight_type='distancia'):
    out = {}
    for u, vecinos in lista_ady.items():
        out[u] = []
        for v, d, t in vecinos:
            peso = d if weight_type=='distancia' else t
            out[u].append((v, peso))
    return out
