"""Evaluar anotaciones de NLP contra una referencia docente acordada.

No entrena ningún modelo. Las predicciones pueden ser humanas o de cualquier
sistema; las métricas no identifican por sí solas cómo fueron producidas.
Solo utiliza la biblioteca estándar de Python.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
REFERENCIA = BASE / "datos" / "referencia_docente.csv"
DEMO = BASE / "datos" / "predicciones_demo.csv"
CAMPOS = ("id", "intenciones", "urgente", "revision", "pedido_id")
ETIQUETAS = (
    "ACCESO", "FACTURACION", "SOPORTE_TECNICO", "ENVIOS", "OTRO", "REVISAR"
)


def leer_csv(ruta):
    """Leer y validar columnas e identificadores únicos."""
    with Path(ruta).open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None or any(c not in lector.fieldnames for c in CAMPOS):
            raise ValueError(f"{ruta}: faltan columnas: {', '.join(CAMPOS)}")
        datos = {}
        for fila in lector:
            identificador = fila["id"].strip()
            if not identificador or identificador in datos:
                raise ValueError(f"{ruta}: ID vacío o duplicado: {identificador!r}")
            datos[identificador] = fila
    if not datos:
        raise ValueError(f"{ruta}: CSV vacío")
    return datos


def intenciones(valor):
    """Interpretar una anotación multilabel sin imponer un orden."""
    elementos = [v.strip().upper() for v in valor.split("|")]
    if not elementos or any(not v for v in elementos):
        raise ValueError(f"Intenciones vacías o mal separadas: {valor!r}")
    conjunto = set(elementos)
    if len(conjunto) != len(elementos):
        raise ValueError(f"Intención repetida: {valor!r}")
    if not conjunto.issubset(ETIQUETAS):
        raise ValueError(f"Intenciones desconocidas: {valor!r}")
    if len(conjunto) > 1 and ("OTRO" in conjunto or "REVISAR" in conjunto):
        raise ValueError("OTRO y REVISAR son etiquetas exclusivas")
    return conjunto


def validar(fila):
    """Validar la coherencia de una fila antes de computar las métricas."""
    etiquetas = intenciones(fila["intenciones"])
    for campo in ("urgente", "revision"):
        if fila[campo].strip().upper() not in ("SI", "NO"):
            raise ValueError(f"{campo}: usar SI o NO")
    if fila["revision"].strip().upper() != ("SI" if "REVISAR" in etiquetas else "NO"):
        raise ValueError("revision debe ser SI exactamente cuando intenciones es REVISAR")
    numero = fila["pedido_id"].strip()
    if numero and not numero.isdigit():
        raise ValueError("pedido_id debe ser numérico o vacío")
    return etiquetas


def calcular(referencia, respuestas):
    """Devolver métricas y ejemplos que requieren discusión."""
    if set(referencia) != set(respuestas):
        faltantes = sorted(set(referencia) - set(respuestas))
        extras = sorted(set(respuestas) - set(referencia))
        raise ValueError(f"IDs diferentes. Faltantes: {faltantes}; extras: {extras}")

    conteos = {e: Counter(tp=0, fp=0, fn=0) for e in ETIQUETAS}
    completos = urgencia = revision = pedido = 0
    diferencias = []

    for identificador in referencia:
        real, pred = referencia[identificador], respuestas[identificador]
        try:
            reales = validar(real)
            predichas = validar(pred)
        except ValueError as exc:
            raise ValueError(f"Mensaje {identificador}: {exc}") from exc

        completos += reales == predichas
        urgencia += real["urgente"].strip().upper() == pred["urgente"].strip().upper()
        revision += real["revision"].strip().upper() == pred["revision"].strip().upper()
        pedido += real["pedido_id"].strip() == pred["pedido_id"].strip()

        for etiqueta in ETIQUETAS:
            conteos[etiqueta]["tp"] += etiqueta in reales and etiqueta in predichas
            conteos[etiqueta]["fp"] += etiqueta not in reales and etiqueta in predichas
            conteos[etiqueta]["fn"] += etiqueta in reales and etiqueta not in predichas
        if (reales != predichas or real["urgente"].strip().upper() != pred["urgente"].strip().upper()
                or real["revision"].strip().upper() != pred["revision"].strip().upper()
                or real["pedido_id"].strip() != pred["pedido_id"].strip()):
            diferencias.append((identificador, "|".join(sorted(reales)), "|".join(sorted(predichas))))

    total = len(referencia)
    tp = sum(c["tp"] for c in conteos.values())
    fp = sum(c["fp"] for c in conteos.values())
    fn = sum(c["fn"] for c in conteos.values())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "n": total, "exactitud": completos / total,
        "precision_micro": precision, "recall_micro": recall, "f1_micro": f1,
        "urgencia": urgencia / total, "revision": revision / total,
        "pedido": pedido / total, "conteos": conteos, "diferencias": diferencias
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--respuestas", type=Path, default=DEMO,
                        help="CSV del estudiante o de demostración")
    parser.add_argument("--referencia", type=Path, default=REFERENCIA,
                        help="CSV de consenso docente")
    args = parser.parse_args()
    try:
        resultado = calcular(leer_csv(args.referencia), leer_csv(args.respuestas))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    n = resultado["n"]
    print(f"Mensajes evaluados: {n}")
    for nombre, etiqueta in [
        ("Coincidencia exacta de intenciones", "exactitud"),
        ("Precision micro", "precision_micro"),
        ("Recall micro", "recall_micro"),
        ("F1 micro", "f1_micro"),
        ("Urgencia correcta", "urgencia"),
        ("Revisión correcta", "revision"),
        ("Identificador de pedido correcto", "pedido"),
    ]:
        print(f"{nombre}: {resultado[etiqueta]:.1%}")
    print("\nPor etiqueta (TP = correcto, FP = sobra, FN = falta):")
    for etiqueta, c in resultado["conteos"].items():
        print(f"  {etiqueta:17s} TP={c['tp']:2d} FP={c['fp']:2d} FN={c['fn']:2d}")
    print("\nMensajes para discutir:")
    for identificador, real, predicho in resultado["diferencias"][:20]:
        print(f"  #{identificador}: referencia={real}; propuesta={predicho}")
    if not resultado["diferencias"]:
        print("  Ninguno (coincidencia total).")
    print("\nAviso: estos 20 ejemplos docentes no permiten afirmar generalización.")


if __name__ == "__main__":
    main()
