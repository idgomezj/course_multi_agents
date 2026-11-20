"""Pruebas de los ejemplos; el preentrenado no se descarga en CI."""
import ast
import importlib.util
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]

def cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, BASE / archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

class PruebaTresEnfoques(unittest.TestCase):
    def test_reglas(self):
        reglas = cargar("reglas_demo", "01_reglas.py")
        self.assertEqual(reglas.clasificar(reglas.MENSAJE), ["REVISAR"])
        self.assertEqual(reglas.clasificar("mi paquete"), ["ENVIOS"])

    def test_supervisado(self):
        ml = cargar("ml_demo", "02_ml_supervisado.py")
        modelo, n = ml.entrenar()
        self.assertEqual(n, 40)
        self.assertEqual(modelo.predict([ml.MENSAJE])[0], "FACTURACION")

    def test_preentrenado_sintaxis(self):
        codigo = (BASE / "03_preentrenado.py").read_text(encoding="utf-8")
        self.assertIsInstance(ast.parse(codigo), ast.Module)
        self.assertIn("zero-shot-classification", codigo)

if __name__ == "__main__":
    unittest.main()
