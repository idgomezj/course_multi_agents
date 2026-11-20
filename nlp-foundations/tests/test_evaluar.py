"""Tests sin dependencias externas del módulo introductorio de NLP."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evaluar_nlp", BASE / "evaluar.py")
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)

spec_plantilla = importlib.util.spec_from_file_location("plantilla_nlp", BASE / "crear_plantilla.py")
plantilla = importlib.util.module_from_spec(spec_plantilla)
spec_plantilla.loader.exec_module(plantilla)


class PruebasNLP(unittest.TestCase):
    def test_referencia_perfecta(self):
        referencia = modulo.leer_csv(BASE / "datos" / "referencia_docente.csv")
        self.assertEqual(len(referencia), 20)
        resultado = modulo.calcular(referencia, referencia)
        for campo in ("exactitud", "precision_micro", "recall_micro",
                      "f1_micro", "urgencia", "revision", "pedido"):
            self.assertEqual(resultado[campo], 1.0)

    def test_demo_tiene_errores_y_no_es_entrenamiento(self):
        referencia = modulo.leer_csv(BASE / "datos" / "referencia_docente.csv")
        demo = modulo.leer_csv(BASE / "datos" / "predicciones_demo.csv")
        r = modulo.calcular(referencia, demo)
        self.assertLess(r["exactitud"], 1)
        self.assertGreater(r["f1_micro"], 0)
        self.assertGreater(len(r["diferencias"]), 0)

    def test_multietiqueta_sin_orden(self):
        self.assertEqual(modulo.intenciones("ENVIOS|FACTURACION"),
                         modulo.intenciones("FACTURACION|ENVIOS"))

    def test_revision_exclusiva(self):
        with self.assertRaises(ValueError):
            modulo.intenciones("REVISAR|ENVIOS")

    def test_plantilla_20_filas_vacias(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "salida.csv"
            numero = plantilla.crear_plantilla(
                BASE / "datos" / "mensajes.csv", destino)
            self.assertEqual(numero, 20)
            with destino.open(encoding="utf-8", newline="") as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(len(filas), 20)
            self.assertTrue(all(fila["intenciones"] == "" for fila in filas))


if __name__ == "__main__":
    unittest.main()
