import csv
import random
import os
from datetime import datetime, timedelta

def generar_dataset(filename="data/dataset.csv", num_registros=500000):
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    categorias = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Juguetes', 'Libros']
    metodos_pago = ['Tarjeta', 'Efectivo', 'Transferencia', 'PayPal']
    ciudades = ['CDMX', 'Guadalajara', 'Monterrey', 'Puebla', 'Querétaro', 'Mérida']
    
    fecha_inicio = datetime(2025, 1, 1)
    
    print(f"Generando {num_registros} registros en '{filename}'...")
    
    headers = ['id_transaccion', 'timestamp', 'cliente_id', 'categoria', 'monto', 'metodo_pago', 'ciudad']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(1, num_registros + 1):
            timestamp = fecha_inicio + timedelta(seconds=random.randint(0, 31536000))
            cliente_id = f"USR-{random.randint(1000, 9999)}"
            categoria = random.choice(categorias)
            monto = round(random.uniform(5.0, 1500.0), 2)
            metodo = random.choice(metodos_pago)
            ciudad = random.choice(ciudades)
            
            writer.writerow([i, timestamp.strftime('%Y-%m-%d %H:%M:%S'), cliente_id, categoria, monto, metodo, ciudad])
            
            if i % 100000 == 0:
                print(f"  -> {i} registros procesados...")

    print("¡Dataset generado exitosamente!")

if __name__ == "__main__":
    generar_dataset()
