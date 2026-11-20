"""Demo de NLP por patrones para comparación grupal, no para calificaciones.

Este script NO entrena un modelo. Usa spaCy en español (sin modelo descargado)
y PhraseMatcher para detectar intenciones; regex para números de pedido.
Los patrones pueden fallar frente a lenguaje no previsto.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

import spacy
from spacy.matcher import PhraseMatcher

BASE = Path(__file__).resolve().parent
MENSAJES = BASE / "datos" / "mensajes.csv"

PATRONES = {
    "ACCESO": [
        "mi cuenta", "iniciar sesion", "entrar a mi cuenta", "acceder",
        "credenciales", "contrasena", "recuperar mi cuenta", "cuenta bloqueada",
        "fue bloqueada", "no puedo ingresar", "no puedo entrar", "no puedo acceder",
    ],
    "FACTURACION": [
        "cobraron", "cobro", "cobros", "factura", "facturas",
        "facturacion", "pagar", "pago", "devolucion", "dinero", "reembolso",
    ],
    "SOPORTE_TECNICO": [
        "aplicacion", "app", "pagina", "enlace", "actualizacion",
        "se congela", "se cierra", "error", "no carga", "falla",
        "fallo", "congelada",
    ],
    "ENVIOS": [
        "paquete", "entrega", "direccion de entrega", "seguimiento",
        "no ha llegado", "no llega", "no llegar", "llego incompleto",
        "llego incompleta", "pedido incompleto", "pedido no aparece", "rastrear",
    ],
    "OTRO": [
        "horario de atencion", "una sugerencia", "sugerencia", "mejorar el servicio",
    ],
}
URGENCIA = [
    "urgente", "urgencia", "hoy mismo", "inmediatamente",
    "inmediato", "lo antes posible", "ahora mismo",
]
PEDIDO = re.compile(
    r"\b(?:pedido|orden)\s*(?:numero\s*|num\.?\s*|nro\.?\s*|n[°º]\s*|#\s*)?(\d{3,})\b"
)


def normalizar(texto: str) -> str:
    """Uniforma mayúsculas y tildes para las coincidencias."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.casefold())
        if unicodedata.category(c) != "Mn"
    )


class AnalizadorNLP:
    """Agrupa detección de múltiples intenciones y extracción de información."""

    def __init__(self):
        self.nlp = spacy.blank("es")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        for etiqueta, expresiones in PATRONES.items():
            self.matcher.add(
                etiqueta, [self.nlp.make_doc(normalizar(x)) for x in expresiones]
            )
        self.urgencias = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.urgencias.add("URGENCIA", [self.nlp.make_doc(x) for x in URGENCIA])

    def analizar(self, mensaje: str) -> dict:
        texto = normalizar(mensaje)
        doc = self.nlp.make_doc(texto)
        intenciones = {self.nlp.vocab.strings[m] for m, _, _ in self.matcher(doc)}
        if len(intenciones) > 1:
            intenciones.discard("OTRO")
        if not intenciones:
            intenciones = {"REVISAR"}
        pedido = PEDIDO.search(texto)
        return {
            "intenciones": sorted(intenciones),
            "urgente": "SI" if self.urgencias(doc) else "NO",
            "revision": "SI" if "REVISAR" in intenciones else "NO",
            "pedido_id": pedido.group(1) if pedido else "",
        }


def leer_mensajes(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        mensajes = list(csv.DictReader(archivo))
    if not mensajes or not {"id", "mensaje"}.issubset(mensajes[0]):
        raise ValueError("El archivo debe contener id y mensaje.")
    return mensajes


def main():
    parser = argparse.ArgumentParser(description="Demostración de NLP para discusión en clase.")
    opciones = parser.add_mutually_exclusive_group(required=True)
    opciones.add_argument("--mensaje", help="Analizar texto libre")
    opciones.add_argument("--id", help="Mensaje existente por ID")
    opciones.add_argument("--todos", action="store_true", help="Recorrer todo el CSV")
    opciones.add_argument("--ejemplos", action="store_true", help="Ocho mensajes recomendados")
    parser.add_argument("--pausa", action="store_true", help="Revelar resultado después de Enter")
    parser.add_argument("--csv", type=Path, default=MENSAJES, help="CSV con id y mensaje")
    args = parser.parse_args()
    try:
        if args.mensaje is not None:
            mensajes = [{"id": "NUEVO", "mensaje": args.mensaje}]
        else:
            mensajes = leer_mensajes(args.csv)
        if args.id:
            mensajes = [x for x in mensajes if x["id"] == args.id]
            if not mensajes:
                parser.error(f"No hay un mensaje con ID {args.id}")
        elif args.ejemplos:
            ids = {"5", "6", "7", "11", "12", "13", "15", "20"}
            mensajes = [x for x in mensajes if x["id"] in ids]
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    analizador = AnalizadorNLP()
    print("NLP por patrones con spaCy. Sin entrenamiento y sin notas automáticas.")
    print("La clase decide primero. El programa revela después.\n")
    for fila in mensajes:
        print(f"[{fila['id']}] {fila['mensaje']}")
        if args.pausa:
            try:
                input("    ¿Qué opina la clase? Pulsa Enter para revelar... ")
            except EOFError:
                pass
        resultado = analizador.analizar(fila["mensaje"])
        print("    Intenciones:", " + ".join(resultado["intenciones"]))
        print("    Urgente:   ", resultado["urgente"])
        print("    Revisión:  ", resultado["revision"])
        print("    Pedido:    ", resultado["pedido_id"] or "(no identificado)")
        if resultado["revision"] == "SI":
            print("    Nota: faltan datos; habría que preguntar al cliente.")
        print()


if __name__ == "__main__":
    main()
