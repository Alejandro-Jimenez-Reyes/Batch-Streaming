import time
import json
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Configuración de la página en Streamlit
st.set_page_config(page_title="Comparativa Batch vs Streaming en Tiempo Real", layout="wide")

st.title("⚡ Monitoreo Continuo en Tiempo Real: Batch vs. Streaming")
st.markdown("---")

# URL del flujo continuo de datos de Wikimedia
STREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"

# Sidebar para ajuste de parámetros
st.sidebar.header("⚙️ Configuración del Flujo")
MAX_EVENTOS = st.sidebar.slider("Eventos por ciclo", 50, 500, 100)
TAMANO_LOTE = st.sidebar.slider("Tamaño del micro-lote", 10, 50, 20)

st.info("🟢 Conectado al flujo de eventos en vivo de Wikimedia (sin interacción requerida).")

eventos_acumulados = []

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔴 Procesamiento Streaming (Tiempo Real)")
    metric_stream_count = st.empty()
    metric_stream_latency = st.empty()
    chart_stream = st.empty()
    table_stream = st.empty()
    
with col2:
    st.subheader("📦 Procesamiento Batch (Acumulado)")
    status_batch = st.empty()
    chart_batch = st.empty()
    table_batch = st.empty()
    
status_batch.warning("⌛ Modo BATCH: En espera de completar el lote de recolección...")

# --- CONEXIÓN CONTINUA AUTOMÁTICA ---
headers = {'User-Agent': 'PythonStreamApp/1.0'}
t_inicio = time.perf_counter()
t_primer_resultado = None

count = 0
historial_streaming = []

try:
    response = requests.get(STREAM_URL, stream=True, headers=headers, timeout=10)
    
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data_str = line[6:]
            try:
                data = json.loads(data_str)
                
                if not isinstance(data, dict):
                    continue
                    
                evento = {
                    "usuario": data.get("user", "Anónimo"),
                    "titulo": data.get("title", "Desconocido"),
                    "bytes": data.get("length", {}).get("new", 0) - data.get("length", {}).get("old", 0) if isinstance(data.get("length"), dict) else 0,
                    "tipo": data.get("type", "edit"),
                    "timestamp": time.time()
                }
                eventos_acumulados.append(evento)
                count += 1
                
                if t_primer_resultado is None:
                    t_primer_resultado = time.perf_counter() - t_inicio
                    
                # Actualización directa en pantalla sin botones
                if count % TAMANO_LOTE == 0 or count == MAX_EVENTOS:
                    df_temp = pd.DataFrame(eventos_acumulados)
                    historial_streaming.append({
                        "eventos": len(df_temp),
                        "tiempo": time.perf_counter() - t_inicio
                    })
                    
                    metric_stream_count.metric("Eventos procesados", f"{len(df_temp)} / {MAX_EVENTOS}")
                    metric_stream_latency.success(f"⚡ Latencia primer resultado: {t_primer_resultado*1000:.2f} ms")
                    
                    fig, ax = plt.subplots(figsize=(5, 2.5))
                    ax.plot([h["tiempo"] for h in historial_streaming], [h["eventos"] for h in historial_streaming], marker='o', color='teal')
                    ax.set_title("Disponibilidad Incremental (Streaming)")
                    ax.set_xlabel("Tiempo (s)")
                    ax.set_ylabel("Eventos listos")
                    chart_stream.pyplot(fig)
                    plt.close(fig)
                    
                    table_stream.dataframe(df_temp.tail(5)[["usuario", "titulo", "bytes", "tipo"]])
                    
                if count >= MAX_EVENTOS:
                    break
            except Exception:
                continue
except Exception as e:
    st.error(f"Error en la conexión al stream: {e}")

t_fin_streaming = time.perf_counter() - t_inicio

# --- PROCESAMIENTO BATCH AL COMPLETAR EL LOTE ---
if eventos_acumulados:
    t_inicio_batch = time.perf_counter()
    status_batch.info("🔄 Procesando lote completo BATCH...")
    
    df_batch = pd.DataFrame(eventos_acumulados)
    total_bytes = df_batch["bytes"].sum()
    promedio_bytes = round(df_batch["bytes"].mean(), 2)
    
    t_fin_batch = (time.perf_counter() - t_inicio_batch) + t_fin_streaming
    
    status_batch.success(f"✅ Procesamiento BATCH finalizado en {t_fin_batch:.2f} s")
    
    fig_b, ax_b = plt.subplots(figsize=(5, 2.5))
    ax_b.bar(["Batch (Único resultado)"], [len(df_batch)], color='crimson')
    ax_b.set_ylabel("Eventos listos")
    chart_batch.pyplot(fig_b)
    plt.close(fig_b)
    
    table_batch.write(f"**Métricas Finales BATCH:**")
    table_batch.json({
        "Total Eventos": len(df_batch),
        "Suma Bytes Cambiados": int(total_bytes),
        "Promedio Bytes/Cambio": promedio_bytes,
        "Latencia Primer Resultado (s)": round(t_fin_batch, 4)
    })

    # --- COMPARATIVA DE LATENCIAS ---
    st.markdown("---")
    st.header("📊 Comparativa de Latencia hasta el Primer Resultado")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        fig_comp, ax_comp = plt.subplots(figsize=(6, 3))
        ax_comp.bar(["Streaming", "Batch"], [t_primer_resultado * 1000, t_fin_batch * 1000], color=['teal', 'crimson'])
        ax_comp.set_ylabel("Latencia (ms)")
        ax_comp.set_title("Latencia al primer resultado (ms)")
        st.pyplot(fig_comp)
        plt.close(fig_comp)
        
    with col_c2:
        st.write(f"• **Streaming:** Entregó el primer resultado parcial en **{t_primer_resultado*1000:.2f} ms**.")
        st.write(f"• **Batch:** Tuvo que esperar a juntar los {MAX_EVENTOS} eventos, tardando **{t_fin_batch*1000:.2f} ms**.")
        st.write("• **Conclusión:** Ambos paradigmas devuelven el mismo cómputo total al final, pero Streaming ofrece visibilidad inmediata.")

    # Reinicio automático para flujo continuo e infinito
    time.sleep(2)
    st.rerun()
