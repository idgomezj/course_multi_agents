"""Pruebas técnicas, NO evaluación de estudiantes."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def importar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


demo = importar("demo_nlp", BASE / "demo_nlp.py")
plantilla = importar("crear_plantilla", BASE / "crear_plantilla.py")


class PruebasDemoNLP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analizador = demo.AnalizadorNLP()

    def test_dos_intenciones_y_pedido(self):
        r = self.analizador.analizar(
            "Me cobraron dos veces el pedido 4582, todavía no llega y es urgente."
        )
        self.assertEqual(r["intenciones"], ["ENVIOS", "FACTURACION"])
        self.assertEqual(r["pedido_id"], "4582")
        self.assertEqual(r["urgente"], "SI")

    def test_ambiguedad(self):
        r = self.analizador.analizar("El banco no funciona.")
        self.assertEqual(r["intenciones"], ["REVISAR"])
        self.assertEqual(r["revision"], "SI")

    def test_fuera_de_categoria(self):
        r = self.analizador.analizar("Quiero conocer el horario de atención")
        self.assertEqual(r["intenciones"], ["OTRO"])

    def test_expresion_nueva_puede_fallar(self):
        r = self.analizador.analizar("La compra desapareció del mapa")
        self.assertEqual(r["intenciones"], ["REVISAR"])

    def test_plantilla_contiene_el_texto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "respuestas.csv"
            n = plantilla.crear_plantilla(BASE / "datos/mensajes.csv", destino)
            self.assertEqual(n, 20)
            with destino.open(encoding="utf-8", newline="") as f:
                filas = list(csv.DictReader(f))
            self.assertEqual(len(filas), 20)
            self.assertTrue(all(fila["mensaje"] and not fila["intenciones"] for fila in filas))


if __name__ == "__main__":
    unittest.main()
