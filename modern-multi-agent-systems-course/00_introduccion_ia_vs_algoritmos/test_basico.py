"""Pruebas ligeras sin modelos descargados ni dependencias de ML."""
import unittest
from datos import CATEGORIAS, ENTRENAMIENTO, PRUEBA
from reglas import predecir
from agente import ejecutar


class CursoIntroTest(unittest.TestCase):
    def test_datos_etiquetados(self):
        self.assertEqual(len(ENTRENAMIENTO), 40)
        self.assertEqual(len(PRUEBA), 16)
        self.assertTrue(all(c in CATEGORIAS for _, c in ENTRENAMIENTO + PRUEBA))

    def test_division_sin_duplicados(self):
        self.assertFalse(set(t for t, _ in ENTRENAMIENTO) & set(t for t, _ in PRUEBA))

    def test_reglas_conocidas(self):
        self.assertEqual(predecir("Olvidé mi contraseña"), "acceso")
        self.assertEqual(predecir("Tengo una factura"), "facturacion")

    def test_reglas_sin_coincidencia(self):
        self.assertEqual(predecir("Buenos días, tengo una pregunta"), "otro")

    def test_agente_requiere_aprobacion(self):
        self.assertEqual(ejecutar("Olvidé mi contraseña")["estado"], "pendiente_aprobacion")
        self.assertEqual(ejecutar("Olvidé mi contraseña", aprobado=True)["estado"], "accion_simulada")

    def test_agente_desconocido_no_actua(self):
        self.assertEqual(ejecutar("Hola a todos", aprobado=True)["estado"], "revision_humana")


if __name__ == "__main__":
    unittest.main()
