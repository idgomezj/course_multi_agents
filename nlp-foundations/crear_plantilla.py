"""Crear una plantilla de anotación humana a partir de mensajes sin etiquetar.

No entrena, predice ni llama a modelos: su fin es la práctica de anotación NLP.
"""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "datos" / "mensajes.csv"
DESTINO = BASE / "datos" / "respuestas_estudiante.csv"
CAMPOS = ["id", "intenciones", "urgente", "revision", "pedido_id"]


def crear_plantilla(origen=ORIGEN, destino=DESTINO):
    with Path(origen).open(newline="", encoding="utf-8-sig") as archivo:
        mensajes = list(csv.DictReader(archivo))
    if not mensajes or any(not fila.get("id") or not fila.get("mensaje") for fila in mensajes):
        raise ValueError("El archivo de mensajes está vacío o contiene filas inválidas.")

    with Path(destino).open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        for mensaje in mensajes:
            escritor.writerow({"id": mensaje["id"], "intenciones": "",
                               "urgente": "", "revision": "", "pedido_id": ""})
    return len(mensajes)


if __name__ == "__main__":
    cantidad = crear_plantilla()
    print(f"Plantilla creada: {DESTINO} ({cantidad} mensajes).")
    print("Completa todas las columnas siguiendo ACTIVIDAD.md.")
