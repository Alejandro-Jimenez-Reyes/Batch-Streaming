"""
MODO STREAMING
--------------
Simula la LLEGADA continua de posts (registro por registro / en micro-lotes)
como si fueran eventos en tiempo real (tipico de monitoreo, deteccion de
fraude o un feed de red social). Los resultados se ACTUALIZAN de forma
incremental conforme van llegando los datos, sin esperar a tener el
archivo completo.

Caracteristica clave a demostrar: baja latencia hasta el primer resultado
(se obtiene un resultado apenas llega el primer micro-lote), a costa de
mas "overhead" por emitir muchos resultados parciales en vez de uno solo.
"""
import time
import pandas as pd

RUTA_DATASET = "../data/posts_redes_sociales.csv"
TAMANO_LOTE = 100          # registros por "evento" que llega
RETARDO_SIMULADO = 0.01    # segundos entre llegadas, simula tiempo real


class EstadoIncremental:
    """Mantiene estadisticas acumuladas sin releer el pasado."""

    def __init__(self):
        self.total_posts = 0
        self.engagement_total = 0
        self.engagement_por_categoria = {}
        self.conteo_sentimiento = {}

    def actualizar(self, lote: pd.DataFrame):
        self.total_posts += len(lote)
        self.engagement_total += int(lote["engagement"].sum())
        for cat, suma in lote.groupby("categoria")["engagement"].sum().items():
            self.engagement_por_categoria[cat] = (
                self.engagement_por_categoria.get(cat, 0) + int(suma)
            )
        for sent, cuenta in lote["sentimiento"].value_counts().items():
            self.conteo_sentimiento[sent] = (
                self.conteo_sentimiento.get(sent, 0) + int(cuenta)
            )

    def resumen(self) -> dict:
        promedio = (self.engagement_total / self.total_posts
                    if self.total_posts else 0)
        top_categoria = (max(self.engagement_por_categoria,
                              key=self.engagement_por_categoria.get)
                          if self.engagement_por_categoria else None)
        return {
            "total_posts": self.total_posts,
            "engagement_total": self.engagement_total,
            "engagement_promedio": round(promedio, 2),
            "categoria_top": top_categoria,
        }


def main():
    print("=" * 60)
    print("MODO STREAMING - Llegada incremental de eventos")
    print("=" * 60)

    # El dataset completo solo se usa para simular la "fuente" de eventos;
    # el programa NUNCA lo lee de golpe como un solo bloque para calcular.
    fuente = pd.read_csv(RUTA_DATASET, parse_dates=["timestamp"])
    estado = EstadoIncremental()

    t_inicio = time.perf_counter()
    t_primer_resultado = None
    resultados_emitidos = 0
    historial_tiempos = []

    for inicio_lote in range(0, len(fuente), TAMANO_LOTE):
        lote = fuente.iloc[inicio_lote: inicio_lote + TAMANO_LOTE]

        time.sleep(RETARDO_SIMULADO)  # simula el tiempo real de llegada

        estado.actualizar(lote)
        resultados_emitidos += 1
        t_ahora = time.perf_counter()
        historial_tiempos.append(t_ahora - t_inicio)

        if t_primer_resultado is None:
            t_primer_resultado = t_ahora - t_inicio

        resumen = estado.resumen()
        if resultados_emitidos % 5 == 0 or inicio_lote == 0:
            print(f"[STREAM] Lote #{resultados_emitidos:>2} "
                  f"(+{len(lote)} posts, acumulado={resumen['total_posts']:>4}) "
                  f"-> engagement_prom={resumen['engagement_promedio']:>6} "
                  f"| top={resumen['categoria_top']}")

    t_fin = time.perf_counter()

    print()
    print("----- RESULTADO FINAL ACUMULADO (igual al batch, pero ya lo "
          "conociamos parcialmente desde el principio) -----")
    resumen_final = estado.resumen()
    print(f"Total de posts procesados : {resumen_final['total_posts']}")
    print(f"Engagement total          : {resumen_final['engagement_total']}")
    print(f"Engagement promedio/post  : {resumen_final['engagement_promedio']}")
    print(f"Categoria con mas engagement : {resumen_final['categoria_top']}")
    print()
    print(f"[STREAM] Tiempo total de procesamiento: {t_fin - t_inicio:.4f} s")
    print(f"[STREAM] Latencia hasta el PRIMER resultado: "
          f"{t_primer_resultado:.4f} s")
    print(f"[STREAM] Resultados parciales emitidos: {resultados_emitidos}")

    return {
        "modo": "streaming",
        "tiempo_total_seg": t_fin - t_inicio,
        "latencia_primer_resultado_seg": t_primer_resultado,
        "num_resultados_emitidos": resultados_emitidos,
        "historial_tiempos": historial_tiempos,
        "stats_finales": resumen_final,
    }


if __name__ == "__main__":
    main()