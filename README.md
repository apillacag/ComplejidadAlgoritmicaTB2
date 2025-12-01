Proyecto SJL - Hito3
====================

Cómo ejecutar:
1. Instala dependencias opcionales:
   pip install -r requirements.txt
   (si falla graphviz, instala Graphviz nativo desde https://graphviz.org/download/)

2. Abre carpeta en VS Code o ejecuta desde terminal:
   python main.py

3. En la GUI usa:
   - "Obtener grafo (OSM o CSV)" → te pregunta si quieres descargar OSM o cargar CSVs.
   - Ejecuta algoritmos, guarda resultados o imágenes.

Formato CSV esperado (si cargas CSV):
- grafo_sjl_osm.csv: origen,destino,distancia_metros,tiempo_minutos,nombre_calle
- nodos_sjl_osm.csv: nodo_id,latitud,longitud

Archivos generados:
- *.csv (resultados)
- *.png (imágenes de rutas/subgrafos/mst)
