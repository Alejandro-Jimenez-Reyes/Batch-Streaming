# Módulo de Datos - Generador de Dataset

Este módulo contiene el script encargado de sintetizar el conjunto de datos de transacciones utilizado para la comparación entre procesamiento **Batch** y **Streaming**.

## 📁 Archivos

- `generar_dataset.py`: Script en Python que genera el archivo CSV con transacciones sintéticas.
- `dataset.csv`: Archivo generado resultado de la ejecución.

## 📊 Esquema del Dataset (`dataset.csv`)

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id_transaccion` | Entero | Identificador único del evento / venta. |
| `timestamp` | String (`YYYY-MM-DD HH:MM:SS`) | Fecha y hora exacta de la transacción. |
| `cliente_id` | String | Identificador del cliente. |
| `categoria` | String | Categoría del producto vendido. |
| `monto` | Flotante | Importe total de la compra. |
| `metodo_pago` | String | Método empleado (Tarjeta, Efectivo, etc.). |
| `ciudad` | String | Ubicación donde ocurrió la transacción. |

## 🚀 Instrucciones de Ejecución

Desde la raíz del proyecto, ejecuta:

```bash
python3 data/generar_dataset.py
