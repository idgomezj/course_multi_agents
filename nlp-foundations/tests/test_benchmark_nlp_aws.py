"""Tests del benchmark, sin bajar el modelo preentrenado."""
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/"benchmark_nlp_aws.py"
s=importlib.util.spec_from_file_location("benchmark_aws",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class TestBench(unittest.TestCase):
    def test_volumen(self):
        self.assertEqual(100*3600*8,2880000)
        self.assertEqual(100*3600*8*30,86400000)
    def test_proyeccion(self):
        r={"estado":"medido","rps":50.,"precio":.1008}
        x=m.proyeccion(r,100,8,.7)
        self.assertEqual(x[0],3)
        self.assertAlmostEqual(x[1],2.4192)
    def test_sin_medicion(self):
        self.assertIsNone(m.proyeccion({"estado":"no medido"},100,8,.7))
    def test_datos(self):
        texto,ref=m.corpus()
        self.assertEqual(len(texto),20)
        self.assertGreaterEqual(len(ref),8)

if __name__=="__main__":
    unittest.main()
