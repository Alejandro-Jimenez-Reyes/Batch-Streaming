"""Ejecuta ambos modos como funciones (sin subprocess) y genera la grafica
comparativa que se usa como evidencia visual en el reporte / exposicion."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import batch_mode
import streaming_mode

res_batch = batch_mode.main()
print("\n" + "=" * 60 + "\n")
res_stream = streaming_mode.main()

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# --- Grafica 1: resultados disponibles a lo largo del tiempo ---
ax = axes[0]
ax.step([0, res_batch["tiempo_total_seg"]], [0, res_batch["num_resultados_emitidos"]],
        where="post", label="Batch (1 solo resultado, al final)", color="#d1495b", linewidth=2)
tiempos_stream = [0] + res_stream["historial_tiempos"]
conteo_stream = list(range(len(tiempos_stream)))
ax.step(tiempos_stream, conteo_stream, where="post",
        label="Streaming (resultados incrementales)", color="#118ab2", linewidth=2)
ax.set_xlabel("Tiempo transcurrido (s)")
ax.set_ylabel("Resultados disponibles (acumulado)")
ax.set_title("Disponibilidad de resultados en el tiempo")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- Grafica 2: latencia hasta el primer resultado ---
ax2 = axes[1]
modos = ["Batch", "Streaming"]
latencias = [res_batch["latencia_primer_resultado_seg"] * 1000,
             res_stream["latencia_primer_resultado_seg"] * 1000]
barras = ax2.bar(modos, latencias, color=["#d1495b", "#118ab2"])
ax2.set_ylabel("Latencia al primer resultado (ms)")
ax2.set_title("Latencia hasta el primer resultado")
for b, v in zip(barras, latencias):
    ax2.text(b.get_x() + b.get_width() / 2, v, f"{v:.1f} ms",
              ha="center", va="bottom", fontsize=9)
ax2.grid(alpha=0.3, axis="y")

fig.tight_layout()
fig.savefig("../docs/evidencias/comparacion_batch_streaming.png", dpi=150)
print("\nGrafica guardada en docs/evidencias/comparacion_batch_streaming.png")

print("\nRESUMEN COMPARATIVO")
print(f"  Batch     -> tiempo total: {res_batch['tiempo_total_seg']*1000:.2f} ms | "
      f"1 resultado final | latencia primer resultado: "
      f"{res_batch['latencia_primer_resultado_seg']*1000:.2f} ms")
print(f"  Streaming -> tiempo total: {res_stream['tiempo_total_seg']*1000:.2f} ms | "
      f"{res_stream['num_resultados_emitidos']} resultados parciales | "
      f"latencia primer resultado: {res_stream['latencia_primer_resultado_seg']*1000:.2f} ms")