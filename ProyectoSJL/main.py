"""
main.py
Aplicativo Tkinter - Opción B (un solo botón híbrido que pregunta OSM o CSV)
Estilo: claro, comentarios didácticos, integrable con los módulos en /grafos y /visualizacion.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time, os
import math

# módulos del proyecto
from grafos.componentes import obtener_componente_gigante, extraer_subgrafo
from grafos.loader import construir_desde_osm, carga_csvs, guarda_csvs
from utils.converters import lista_ady_to_list_weighted, lista_ady_to_dict_dict
from grafos.dijkstra import Dijkstra
from grafos.bfs_dfs import DFS, BFS
from grafos.floyd import floyd_warshall, reconstruir_camino
from grafos.mst_prim import MSTPrim
from grafos.mst_kruskal import MSTKruskal
from visualizacion.plots import dibuja_subgrafo, mostrar_mst, mostrar_ruta


import math

def formatea_resumen(stats):
    """
    Recibe un diccionario 'stats' y retorna una cadena formateada humanamente.
    """
    lines = []
    alg = stats.get("algoritmo", "ALGORITMO")
    lines.append("="*45)
    lines.append(f"ALGORITMO: {alg}")
    lines.append("="*45)

    # campos comunes
    if "origen" in stats:
        lines.append(f"• Nodo origen: {stats.get('origen')}")
    if "destino" in stats:
        lines.append(f"• Nodo destino: {stats.get('destino')}")
    if "V" in stats:
        lines.append(f"• Nodos totales (V): {stats.get('V')}")
    if "E_aprox" in stats:
        lines.append(f"• Aristas aproximadas (E): {stats.get('E_aprox')}")
    if "distancia_total" in stats:
        d = stats.get("distancia_total")
        if d == float('inf'):
            lines.append("• Distancia total: ∞ (no alcanzable)")
        else:
            lines.append(f"• Distancia total: {round(d,2)} metros")
    if "tiempo_estimado_min" in stats and stats.get("tiempo_estimado_min") is not None:
        lines.append(f"• Tiempo estimado: {round(stats.get('tiempo_estimado_min'),2)} minutos")
    if "largo_camino_nodos" in stats:
        lines.append(f"• Longitud del camino: {stats.get('largo_camino_nodos')} nodos")
    if "nodos_explorados" in stats:
        lines.append(f"• Nodos explorados: {stats.get('nodos_explorados')}")
    if "aristas_relajadas" in stats:
        lines.append(f"• Aristas relajadas: {stats.get('aristas_relajadas')}")
    if "aristas_consideradas" in stats:
        lines.append(f"• Aristas consideradas: {stats.get('aristas_consideradas')}")
    if "aristas_en_mst" in stats:
        lines.append(f"• Aristas en MST: {stats.get('aristas_en_mst')}")
    if "costo_total" in stats:
        lines.append(f"• Costo total (suma pesos): {round(stats.get('costo_total'),2)}")
    if "ciclos_omitidos" in stats:
        lines.append(f"• Ciclos detectados/omitidos: {stats.get('ciclos_omitidos')}")
    if "total_nodos_visitados" in stats:
        lines.append(f"• Total de nodos visitados: {stats.get('total_nodos_visitados')}")
    if "profundidad_maxima" in stats:
        lines.append(f"• Profundidad máxima: {stats.get('profundidad_maxima')}")
    if "grafo_conectado" in stats:
        lines.append(f"• ¿Grafo conectado?: {'Sí' if stats.get('grafo_conectado') else 'No'}")

    # tiempo y complejidad
    if "tiempo_algo_s" in stats:
        lines.append(f"• Tiempo de ejecución (algoritmo): {stats.get('tiempo_algo_s')} s")
    if "tiempo_ejecucion_gui" in stats:
        lines.append(f"• Tiempo total (GUI medido): {round(stats.get('tiempo_ejecucion_gui'),6)} s")
    if "complejidad_teorica" in stats:
        lines.append(f"• Complejidad aproximada: {stats.get('complejidad_teorica')}")

    # ruta si existe
    ruta = stats.get("ruta", None)
    if ruta:
        # mostrar hasta 15 nodos y truncar en medio si es muy largo
        if len(ruta) <= 15:
            lines.append("Ruta encontrada:")
            lines.append(" → ".join(map(str, ruta)))
        else:
            pref = " → ".join(map(str, ruta[:7]))
            suf = " → ".join(map(str, ruta[-7:]))
            lines.append("Ruta encontrada (truncada):")
            lines.append(pref + " → ... → " + suf)

    return "\n".join(lines)

# --------------------------------------------------------
# Interfaz principal
# --------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title('Hito3 - Proyecto SJL (OSM/CSV híbrido)')
        root.geometry('1000x700')

        # datos del grafo
        self.lista_ady = None   # {u: [(v,d,t), ...], ...}
        self.nodos_info = None  # {u: (lon,lat), ...}
        self.grafo_osm = None   # objeto de osmnx si se usó
        self.last_image = None
        # backups para restaurar grafo original
        self._lista_ady_backup = None
        self._nodos_info_backup = None


        # layout
        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_w = 24
        ttk.Button(left, text='Obtener grafo (OSM o CSV)', width=btn_w, command=self.obtain_grafo).pack(pady=6)
        ttk.Button(left, text='Usar componente gigante', width=btn_w, command=self.usar_componente_gigante).pack(pady=6)
        ttk.Button(left, text='Restaurar grafo original', width=btn_w, command=self.restaurar_grafo_original).pack(pady=6)
        ttk.Button(left, text='Dijkstra', width=btn_w, command=self.panel_dijkstra).pack(pady=6)
        ttk.Button(left, text='Floyd-Warshall', width=btn_w, command=self.panel_floyd).pack(pady=6)
        ttk.Button(left, text='Prim (MST)', width=btn_w, command=self.panel_prim).pack(pady=6)
        ttk.Button(left, text='Kruskal (MST)', width=btn_w, command=self.panel_kruskal).pack(pady=6)
        ttk.Button(left, text='DFS', width=btn_w, command=self.panel_dfs).pack(pady=6)
        ttk.Button(left, text='Guardar grafo actual a CSV', width=btn_w, command=self.save_csvs).pack(pady=6)
        ttk.Button(left, text='Ver última imagen', width=btn_w, command=self.show_last_image).pack(pady=6)
        ttk.Button(left, text='Salir', width=btn_w, command=root.quit).pack(side=tk.BOTTOM, pady=12)

        # panel de resultados y dinámico
        self.title_lbl = ttk.Label(right, text='Panel de resultados', font=('Helvetica',14,'bold'))
        self.title_lbl.pack(anchor='w', pady=(4,10))
        self.dynamic = ttk.Frame(right, relief=tk.RIDGE, padding=8)
        self.dynamic.pack(fill=tk.BOTH, expand=True)
        bottom = ttk.Frame(right)
        bottom.pack(fill=tk.X, pady=(8,0))
        ttk.Label(bottom, text='Salida:').pack(anchor='w')
        self.text_out = tk.Text(bottom, height=10, wrap='word')
        self.text_out.pack(fill=tk.X, padx=4, pady=4)

    # ---------------- utilities ----------------
    def log(self, msg):
        ts = time.strftime('%H:%M:%S')
        self.text_out.insert(tk.END, f'[{ts}] {msg}\n')
        self.text_out.see(tk.END)

    # ---------------- obtener grafo (BOTÓN HÍBRIDO) ----------------
    def obtain_grafo(self):
        """
        Botón híbrido: pregunta al usuario si desea descargar desde OSM.
        Si sí: descarga (requiere osmnx). Si no: abre diálogo para seleccionar CSVs.
        """
        answer = messagebox.askyesno('Obtener grafo', '¿Deseas descargar el grafo desde OpenStreetMap (OSM)?\n\n'
                                                      'Si NO, seleccionarás archivos CSV (grafo_sjl_osm.csv y nodos_sjl_osm.csv).')
        if answer:
            # intentar descarga desde OSM
            try:
                self.log('Descargando grafo desde OSM (San Juan de Lurigancho)...')
                lista_ady, nodos_info, G = construir_desde_osm()
                self.lista_ady = lista_ady
                self.nodos_info = nodos_info
                self.grafo_osm = G
                self.log(f'Descarga OSM completada. Nodos: {len(nodos_info)}. Usa "Guardar grafo actual a CSV" si deseas exportar.')
                messagebox.showinfo('OSM', 'Descarga completada.')
            except Exception as e:
                self.log(f'Error descargando OSM: {e}')
                messagebox.showerror('Error OSM', str(e))
        else:
            # cargar desde CSVs
            try:
                aristas = filedialog.askopenfilename(title='Seleccione grafo_sjl_osm.csv', filetypes=[('CSV','*.csv'),('All','*.*')])
                nodos = filedialog.askopenfilename(title='Seleccione nodos_sjl_osm.csv', filetypes=[('CSV','*.csv'),('All','*.*')])
                if not aristas or not nodos:
                    self.log('Carga CSV cancelada por usuario.')
                    return
                self.log('Cargando CSVs seleccionados...')
                lista_ady, nodos_info = carga_csvs(aristas, nodos)
                self.lista_ady = lista_ady
                self.nodos_info = nodos_info
                self.grafo_osm = None
                self.log(f'CSV cargados. Nodos: {len(nodos_info)}')
                messagebox.showinfo('Carga CSV', 'Carga completada.')
            except Exception as e:
                self.log(f'Error cargando CSVs: {e}')
                messagebox.showerror('Error CSV', str(e))

    # ---------------- guardar CSVs ----------------
    def save_csvs(self):
        if not self.lista_ady or not self.nodos_info:
            messagebox.showwarning('No data', 'No hay grafo cargado para guardar.')
            return
        try:
            guarda_csvs(self.lista_ady, self.nodos_info)
            self.log('Graos guardados: grafo_sjl_osm_out.csv / nodos_sjl_osm_out.csv')
            messagebox.showinfo('Guardar', 'CSVs guardados en carpeta actual.')
        except Exception as e:
            self.log(f'Error guardando CSVs: {e}')
            messagebox.showerror('Error', str(e))

    # ---------------- COMPONENTE GIGANTE ----------------
    def usar_componente_gigante(self):
        """
        Extrae la componente gigante del grafo actual y reemplaza self.lista_ady.
        Hace backup con deepcopy la primera vez. Verifica aplicando DFS corto.
        """
        from copy import deepcopy
        from grafos.componentes import detectar_componentes, obtener_componente_gigante, extraer_subgrafo
        if self.lista_ady is None:
            messagebox.showwarning("Sin grafo", "Primero carga un grafo (CSV u OSM).")
            return

        # Backup seguro (deep copy) la primera vez
        if self._lista_ady_backup is None:
            try:
                self._lista_ady_backup = deepcopy(self.lista_ady)
                self._nodos_info_backup = deepcopy(self.nodos_info) if self.nodos_info is not None else None
                self.log("Backup del grafo original creado.")
            except Exception as e:
                # fallback a copia superficial si deepcopy falla por tamaño
                self._lista_ady_backup = dict(self.lista_ady)
                self._nodos_info_backup = dict(self.nodos_info) if self.nodos_info else None
                self.log(f"Backup superficial creado (deepcopy falló): {e}")

        # --- Información previa: contar componentes y tamaños ---
        try:
            comps = detectar_componentes(self.lista_ady)
            comp_count = len(comps)
            sizes = sorted([len(c) for c in comps], reverse=True)
            self.log(f"Componentes detectadas: {comp_count} (tamaños top: {sizes[:5]})")
        except Exception as e:
            self.log(f"No se pudo calcular componentes antes de extraer: {e}")
            comps = []
            comp_count = None

        # Obtener componente gigante
        gigante = obtener_componente_gigante(self.lista_ady)
        if not gigante:
            messagebox.showerror("Error", "No se encontró componente gigante.")
            return

        # Extraer subgrafo
        sub = extraer_subgrafo(self.lista_ady, gigante)

        # Reemplazar grafo activo
        self.lista_ady = sub
        if self.nodos_info:
            self.nodos_info = {n: self.nodos_info[n] for n in gigante if n in self.nodos_info}

        self.log(f"Se aplicó la componente gigante: {len(gigante)} nodos (grafo activo reemplazado).")

        # --- Verificación definitiva: ejecutar DFS rápido sobre el subgrafo en memoria ---
        # --- Verificación definitiva: ejecutar DFS rápido sobre el subgrafo en memoria ---
        try:
            nodo_prueba = next(iter(gigante))
            orden, stats = DFS(self.lista_ady, nodo_prueba)
            visited = stats.get("total_nodos_visitados", None)

            # ★★★ LÍNEAS NUEVAS: detectar exactamente el nodo faltante ★★★
            orden_set = set(orden)
            missing = gigante - orden_set
            self.log(f"Nodos no alcanzados por DFS: {missing}")

            self.log(f"Verificación DFS sobre subgrafo: nodos visitados = {visited}, tamaño subgrafo = {len(gigante)}")
            if visited == len(gigante):
                self.log("VERIFICACIÓN OK: el subgrafo es conectado y se aplicó correctamente.")
                messagebox.showinfo("Componente gigante", f"Componente gigante aplicada correctamente ({len(gigante)} nodos).")
            else:
                self.log("ALERTA: después de aplicar la componente gigante, la DFS no visitó todos los nodos del subgrafo.")
                self.log(f"Falta(n) nodo(s): {missing}")
                messagebox.showwarning("Componente gigante", f"Aplicada, pero DFS no visitó todos los nodos ({visited} != {len(gigante)}). Revisa la consola.")
        except Exception as e:
            self.log(f"No se pudo verificar con DFS: {e}")
            # aún así confirmamos al usuario que se aplicó
            messagebox.showinfo("Componente gigante", f"Componente gigante aplicada ({len(gigante)} nodos). No se pudo verificar con DFS: {e}")



    def restaurar_grafo_original(self):
        """
        Restaura el grafo original desde el backup.
        """
        if self._lista_ady_backup is None:
            messagebox.showwarning("Restaurar", "Aún no has usado la componente gigante.")
            return

        self.lista_ady = dict(self._lista_ady_backup)
        if self._nodos_info_backup:
            self.nodos_info = dict(self._nodos_info_backup)

        self.log("Grafo original restaurado.")
        messagebox.showinfo("Restaurado", "Se restauró el grafo original completo.")


    # ---------------- paneles de algoritmos (similares a lo que ya trabajaste) ----------------
    def clear_dynamic(self):
        for w in self.dynamic.winfo_children():
            w.destroy()

    def panel_dijkstra(self):
        self.clear_dynamic()
        ttk.Label(self.dynamic, text='Dijkstra (distancia)', font=('Helvetica',12,'bold')).pack(anchor='w')
        frm = ttk.Frame(self.dynamic, padding=6); frm.pack(anchor='w')
        ttk.Label(frm, text='Nodo origen:').grid(row=0,column=0, sticky='w')
        e_or = ttk.Entry(frm, width=30); e_or.grid(row=0,column=1,padx=8,pady=4)
        ttk.Label(frm, text='Destino (opcional):').grid(row=1,column=0, sticky='w')
        e_dest = ttk.Entry(frm, width=30); e_dest.grid(row=1,column=1,padx=8,pady=4)
        def run():
            if self.lista_ady is None:
                messagebox.showwarning('No hay grafo','Carga el grafo primero (OSM o CSV).'); return
            origen_raw = e_or.get().strip() or next(iter(self.lista_ady))
            destino_raw = e_dest.get().strip()
            try:
                origen = int(origen_raw) if str(origen_raw).isdigit() else origen_raw
                destino = int(destino_raw) if destino_raw!='' and str(destino_raw).isdigit() else (destino_raw or None)
            except:
                origen, destino = origen_raw, (destino_raw or None)
            self.log(f'Ejecutando Dijkstra desde {origen} destino {destino}...')
            t0 = time.time()
            lag_list = lista_ady_to_list_weighted(self.lista_ady, 'distancia')
            dist, cams, stats_algo = Dijkstra(lag_list, origen, destino)
            t1 = time.time()
            stats_algo["tiempo_ejecucion_gui"] = round(t1 - t0, 6)
            # si queremos tiempo_estimado en minutos (usando 30 km/h)
            if "distancia_total" in stats_algo and stats_algo["distancia_total"] != float('inf'):
                velocidad_kmh = 30.0
                minutos = (stats_algo["distancia_total"]/1000.0) / velocidad_kmh * 60.0
                stats_algo["tiempo_estimado_min"] = round(minutos, 2)
            # mostrar resumen en text_out
            resumen = formatea_resumen(stats_algo)
            self.text_out.delete(1.0, tk.END)
            self.text_out.insert(tk.END, resumen + "\n")
            # guardar CSV de resultados parcial (opcional)
            fname = f'dijkstra_desde_{origen}.csv'
            import csv as _csv
            with open(fname,'w',newline='',encoding='utf-8') as f:
                w = _csv.writer(f); w.writerow(['dest','dist','camino'])
                for k in dist:
                    w.writerow([k, dist[k] if dist[k]<float('inf') else 'inf', '->'.join(map(str,cams[k]))])
            self.log(f'Dijkstra finalizado. Resultados guardados en {fname}')
            # generar imagen de ruta si se pidió destino y hay ruta
            if destino is not None and stats_algo.get("ruta"):
                img = mostrar_ruta(stats_algo.get("ruta"))
                if img:
                    self.last_image = img
                    self.log(f'Imagen ruta: {img}')
            messagebox.showinfo('Dijkstra','Proceso finalizado.')



        ttk.Button(frm, text='Ejecutar Dijkstra', command=run).grid(row=2,column=0,columnspan=2,pady=8)

    def panel_floyd(self):
        self.clear_dynamic()
        ttk.Label(self.dynamic, text='Floyd-Warshall (APSP) - O(n^3)', font=('Helvetica',12,'bold')).pack(anchor='w')
        frm = ttk.Frame(self.dynamic, padding=6); frm.pack(anchor='w')
        ttk.Label(frm, text='Peso (d=distancia,t=tiempo) [d]:').grid(row=0,column=0,sticky='w')
        e_w = ttk.Entry(frm, width=6); e_w.insert(0,'d'); e_w.grid(row=0,column=1,padx=6)
        ttk.Label(frm, text='Origen (opcional):').grid(row=1,column=0,sticky='w'); e_o = ttk.Entry(frm, width=20); e_o.grid(row=1,column=1,padx=6)
        ttk.Label(frm, text='Destino (opcional):').grid(row=2,column=0,sticky='w'); e_d = ttk.Entry(frm, width=20); e_d.grid(row=2,column=1,padx=6)
        def run():
            if self.lista_ady is None:
                messagebox.showwarning('No hay grafo','Carga el grafo primero (CSV/OSM)'); return
            n = len(self.lista_ady)
            if n > 500:
                if not messagebox.askyesno('Advertencia', f'Grafo con {n} nodos. Floyd puede tardar mucho. Continuar?'): return
            wt = e_w.get().strip().lower(); wt = 'distancia' if wt!='t' else 'tiempo'
            self.log('Ejecutando Floyd-Warshall...')
            t0 = time.time()
            dist, next_hop, nodes, stats = floyd_warshall(self.lista_ady, weight_type=wt)
            t1 = time.time()
            stats["tiempo_ejecucion_gui"] = round(t1 - t0,6)
            # guardar matriz a CSV (opcional)
            fname = f'floyd_{wt}.csv'
            import csv as _csv
            with open(fname,'w',newline='',encoding='utf-8') as f:
                w = _csv.writer(f); w.writerow(['origen/dest']+nodes)
                for u in nodes:
                    w.writerow([u] + [dist[u][v] if dist[u][v]<float('inf') else 'inf' for v in nodes])
            self.text_out.delete(1.0, tk.END)
            self.text_out.insert(tk.END, formatea_resumen(stats) + "\n")
            self.log(f'Floyd finalizado y guardado en {fname}')
            messagebox.showinfo('Floyd','Floyd finalizado.')

        ttk.Button(frm, text='Ejecutar Floyd-Warshall', command=run).grid(row=3,column=0,columnspan=2,pady=8)

    def panel_prim(self):
        self.clear_dynamic(); ttk.Label(self.dynamic, text='Prim (MST)', font=('Helvetica',12,'bold')).pack(anchor='w')
        frm = ttk.Frame(self.dynamic, padding=6); frm.pack(anchor='w')
        ttk.Label(frm, text='Peso (d=distancia,t=tiempo) [d]:').grid(row=0,column=0,sticky='w'); e_w = ttk.Entry(frm, width=6); e_w.insert(0,'d'); e_w.grid(row=0,column=1,padx=6)
        def run():
            if self.lista_ady is None:
                messagebox.showwarning('No hay grafo','Carga el grafo primero (CSV/OSM)'); return
            wt = e_w.get().strip().lower(); wt = 'distancia' if wt!='t' else 'tiempo'
            self.log('Ejecutando Prim...'); t0 = time.time()
            lag_dd = lista_ady_to_dict_dict(self.lista_ady, weight_type=wt)
            prim = MSTPrim(lag_dd)
            mst, costo, stats = prim.Prim() if False else prim.Prim()  # llamada original devuelve (mst,costo,stats)
            # Nota: en nuestra clase Prim implementada retorna (mst,costo,stats)
            # pero en caso tu versión tenga métodos separados usa: mst = prim.getMST(); costo = prim.getCostoTotal(); stats = {...}
            # ajustar según la implementación exacta
            # Para compatibilidad, intentamos:
            try:
                # si Prim devolvió (mst,costo,stats)
                mst_list, costo_total, stats = mst, costo, stats
            except Exception:
                # fallback: obtener desde el objeto
                mst_list = prim.getMST()
                costo_total = prim.getCostoTotal()
                stats = {"algoritmo":"Prim", "V": len(lag_dd), "aristas_en_mst": len(mst_list), "costo_total": costo_total, "complejidad_teorica":"O(E log V)"}
            t1 = time.time()
            stats["tiempo_ejecucion_gui"] = round(t1 - t0,6)
            # guardar CSV
            fname = f'mst_prim_{wt}.csv'
            import csv as _csv
            with open(fname,'w',newline='',encoding='utf-8') as f:
                w = _csv.writer(f); w.writerow(['u','v','peso'])
                for u,v,p in mst_list: w.writerow([u,v,p])
            # intentar dibujar
            try:
                img = prim.dibujaMST(f'mst_prim_{wt}'); self.last_image = img; self.log(f'Imagen generada: {img}')
            except Exception as e:
                self.log(f'No se pudo generar imagen MST Prim: {e}')
            self.text_out.delete(1.0, tk.END)
            self.text_out.insert(tk.END, formatea_resumen(stats) + "\n")
            self.log('Prim finalizado.')
            messagebox.showinfo('Prim','Prim finalizado.')


        ttk.Button(frm, text='Ejecutar Prim', command=run).grid(row=1,column=0,columnspan=2,pady=8)

    def panel_kruskal(self):
        self.clear_dynamic(); ttk.Label(self.dynamic, text='Kruskal (MST)', font=('Helvetica',12,'bold')).pack(anchor='w')
        frm = ttk.Frame(self.dynamic, padding=6); frm.pack(anchor='w')
        ttk.Label(frm, text='Peso (d=distancia,t=tiempo) [d]:').grid(row=0,column=0,sticky='w'); e_w = ttk.Entry(frm, width=6); e_w.insert(0,'d'); e_w.grid(row=0,column=1,padx=6)
        def run():
            if self.lista_ady is None:
                messagebox.showwarning('No hay grafo','Carga el grafo primero (CSV/OSM)'); return
            wt = e_w.get().strip().lower(); wt = 'distancia' if wt!='t' else 'tiempo'
            self.log('Ejecutando Kruskal...'); t0 = time.time()
            lag_dd = lista_ady_to_dict_dict(self.lista_ady, weight_type=wt)
            kr = MSTKruskal(lag_dd)
            mst_list, costo_total, stats = kr.Kruskal() if False else kr.Kruskal()
            # Compatibilidad: si Kruskal retorna triple ajusta; si no, usar getters
            try:
                pass
            except:
                mst_list = kr.getMST(); costo_total = kr.getCostoTotal(); stats = {"algoritmo":"Kruskal","V":len(lag_dd),"aristas_en_mst":len(mst_list),"costo_total":costo_total,"complejidad_teorica":"O(E log E)"}
            t1 = time.time()
            stats["tiempo_ejecucion_gui"] = round(t1 - t0,6)
            # guardar CSV
            fname = f'mst_kruskal_{wt}.csv'
            import csv as _csv
            with open(fname,'w',newline='',encoding='utf-8') as f:
                w = _csv.writer(f); w.writerow(['u','v','peso'])
                for u,v,p in mst_list: w.writerow([u,v,p])
            try:
                img = kr.dibujaMST(f'mst_kruskal_{wt}'); self.last_image = img; self.log(f'Imagen generada: {img}')
            except Exception as e:
                self.log(f'No se pudo generar imagen MST Kruskal: {e}')
            self.text_out.delete(1.0, tk.END)
            self.text_out.insert(tk.END, formatea_resumen(stats) + "\n")
            self.log('Kruskal finalizado.')
            messagebox.showinfo('Kruskal','Kruskal finalizado.')

        ttk.Button(frm, text='Ejecutar Kruskal', command=run).grid(row=1,column=0,columnspan=2,pady=8)

    def panel_dfs(self):
        self.clear_dynamic(); ttk.Label(self.dynamic, text='DFS', font=('Helvetica',12,'bold')).pack(anchor='w')
        frm = ttk.Frame(self.dynamic, padding=6); frm.pack(anchor='w')
        ttk.Label(frm, text='Nodo inicio (ENTER=aleatorio):').grid(row=0,column=0,sticky='w'); e_o = ttk.Entry(frm, width=20); e_o.grid(row=0,column=1,padx=6)
        def run():
            if self.lista_ady is None:
                messagebox.showwarning('No hay grafo','Carga el grafo primero (CSV/OSM)'); return
            inicio_raw = e_o.get().strip() or next(iter(self.lista_ady))
            try: inicio = int(inicio_raw) if str(inicio_raw).isdigit() else inicio_raw
            except: inicio = inicio_raw
            self.log(f'Ejecutando DFS desde {inicio}...')
            t0 = time.time()
            orden, stats = DFS(self.lista_ady, inicio)
            t1 = time.time()
            stats["tiempo_ejecucion_gui"] = round(t1 - t0,6)
            # mostrar resumen
            resumen = formatea_resumen(stats)
            self.text_out.delete(1.0, tk.END)
            self.text_out.insert(tk.END, resumen + "\n")
            self.log(f'DFS completado. Nodos visitados: {stats.get("total_nodos_visitados")}')
            messagebox.showinfo('DFS','DFS completado.')
        ttk.Button(frm, text='Ejecutar DFS', command=run).grid(row=1,column=0,columnspan=2,pady=8)

    
    # --------------------- UTILS ---------------------
    def show_last_image(self):
        if not self.last_image:
            messagebox.showinfo('Imagen','No hay imagen generada.')
            return
        if not os.path.exists(self.last_image):
            messagebox.showwarning('Imagen','Archivo no encontrado.')
            return
        try:
            from PIL import Image, ImageTk
            top = tk.Toplevel(self.root); top.title('Vista imagen')
            img = Image.open(self.last_image); img.thumbnail((900,900))
            imgtk = ImageTk.PhotoImage(img); lbl = tk.Label(top, image=imgtk); lbl.image = imgtk; lbl.pack()
        except Exception:
            messagebox.showinfo('Imagen', f'Imagen generada: {self.last_image} (instala Pillow para vista previa)')

def main():
    root = tk.Tk(); app = App(root); root.mainloop()

if __name__ == '__main__':
    main()
