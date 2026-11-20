"""Prepara una hoja para anotación MANUAL; no entrena ni califica."""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "datos" / "mensajes.csv"
DESTINO = BASE / "datos" / "respuestas_estudiante.csv"
CAMPOS = ["id", "mensaje", "intenciones", "urgente", "revision", "pedido_id"]


def crear_plantilla(origen=ORIGEN, destino=DESTINO):
    with Path(origen).open(encoding="utf-8-sig", newline="") as archivo:
        mensajes = list(csv.DictReader(archivo))
    if not mensajes or any(not m.get("id") or not m.get("mensaje") for m in mensajes):
        raise ValueError("El CSV está vacío o contiene mensajes inválidos.")
    with Path(destino).open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        for mensaje in mensajes:
            escritor.writerow({
                "id": mensaje["id"], "mensaje": mensaje["mensaje"],
                "intenciones": "", "urgente": "", "revision": "", "pedido_id": "",
            })
    return len(mensajes)


if __name__ == "__main__":
    cantidad = crear_plantilla()
    print(f"Plantilla creada: {DESTINO} ({cantidad} mensajes).")
    print("Completa las respuestas manualmente y discútelas con la clase.")
