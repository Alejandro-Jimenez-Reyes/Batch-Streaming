"""
MODO BATCH
----------
Espera a tener el archivo COMPLETO de posts del dia y, hasta ese momento,
calcula todas las estadisticas de una sola vez (procesamiento periodico,
tipico de un reporte de fin de dia / nomina / reporte mensual).

Caracteristica clave a demostrar: alta latencia hasta el primer resultado
(no hay ningun resultado disponible hasta terminar de leer TODO el archivo),
pero alto rendimiento (throughput) porque se procesa todo junto.
"""
import time
import pandas as pd

RUTA_DATASET = "../data/posts_redes_sociales.csv"

# En la vida real, el archivo "del dia completo" no existe hasta que se
# cierra la ventana de recoleccion (ej. medianoche). Aqui simulamos esa
# espera con el mismo tiempo que tarda el modo streaming en recibir TODOS
# los eventos, para que la comparacion de latencia sea justa y no solo
# mida el tiempo de computo (que en un archivo pequeno es casi instantaneo).
ESPERA_CIERRE_VENTANA_SEG = 0.33


def calcular_estadisticas(df: pd.DataFrame) -> dict:
    return {
        "total_posts": len(df),
        "engagement_total": int(df["engagement"].sum()),
        "engagement_promedio": round(df["engagement"].mean(), 2),
        "por_categoria": df.groupby("categoria")["engagement"].sum()
                           .sort_values(ascending=False).to_dict(),
        "por_sentimiento": df["sentimiento"].value_counts().to_dict(),
        "categoria_top": df.groupby("categoria")["engagement"].sum().idxmax(),
    }


def main():
    print("=" * 60)
    print("MODO BATCH - Procesamiento de archivo completo")
    print("=" * 60)

    t_inicio = time.perf_counter()

    print(f"[BATCH] Esperando cierre de la ventana de recoleccion "
          f"({ESPERA_CIERRE_VENTANA_SEG:.2f} s simulados)...")
    time.sleep(ESPERA_CIERRE_VENTANA_SEG)

    print("[BATCH] Ventana cerrada. Leyendo archivo completo del dia...")
    df = pd.read_csv(RUTA_DATASET, parse_dates=["timestamp"])
    t_lectura = time.perf_counter()

    stats = calcular_estadisticas(df)
    t_fin = time.perf_counter()

    latencia_primer_resultado = t_fin - t_inicio

    print(f"[BATCH] Archivo leido: {len(df)} registros "
          f"en {t_lectura - t_inicio:.4f} s")
    print("[BATCH] Calculando estadisticas finales (una sola vez)...")
    print()
    print("----- RESULTADOS FINALES (unico reporte) -----")
    print(f"Total de posts procesados : {stats['total_posts']}")
    print(f"Engagement total          : {stats['engagement_total']}")
    print(f"Engagement promedio/post  : {stats['engagement_promedio']}")
    print(f"Categoria con mas engagement : {stats['categoria_top']}")
    print("Engagement por categoria:")
    for cat, val in stats["por_categoria"].items():
        print(f"   - {cat:16s}: {val}")
    print("Distribucion de sentimiento:")
    for sent, val in stats["por_sentimiento"].items():
        print(f"   - {sent:10s}: {val}")
    print()
    print(f"[BATCH] Tiempo total de procesamiento: {t_fin - t_inicio:.4f} s")
    print(f"[BATCH] Latencia hasta el PRIMER resultado disponible: "
          f"{latencia_primer_resultado:.4f} s (= tiempo total, "
          f"porque no hay resultados parciales)")

    return {
        "modo": "batch",
        "tiempo_total_seg": t_fin - t_inicio,
        "latencia_primer_resultado_seg": latencia_primer_resultado,
        "num_resultados_emitidos": 1,
        "stats_finales": stats,
    }


if __name__ == "__main__":
    main()
