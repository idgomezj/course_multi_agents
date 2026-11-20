"""Misma prueba y métricas para métodos elegidos, sin contaminar entrenamiento."""
import argparse
import time
from datos import PRUEBA


def evaluar(nombre, funcion):
    inicio = time.perf_counter()
    aciertos = 0
    desconocidos = 0
    print(f"\n=== {nombre.upper()} ===")
    for texto, esperado in PRUEBA:
        try:
            predicho = funcion(texto)
        except Exception as exc:
            print("ERROR:", exc)
            return
        correcto = predicho == esperado
        aciertos += int(correcto)
        desconocidos += int(predicho == "otro")
        print(f"{'✓' if correcto else '·'} {predicho:16} (real: {esperado:16}) {texto}")
    total = len(PRUEBA)
    print(f"Exactitud didáctica: {aciertos}/{total} ({100*aciertos/total:.1f}%)")
    print(f"Sin clasificar: {desconocidos}/{total}")
    print(f"Tiempo total: {time.perf_counter()-inicio:.3f} s (incluye inferencia)")
    print("ATENCIÓN: 16 mensajes sintéticos no validan un sistema en producción.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metodos", nargs="+", choices=["reglas", "ml", "embeddings", "llm"],
        default=["reglas", "ml"],
    )
    args = parser.parse_args()

    if "reglas" in args.metodos:
        from reglas import predecir
        evaluar("reglas", predecir)

    if "ml" in args.metodos:
        try:
            from ml_supervisado import construir_modelo
            modelo = construir_modelo()
            evaluar("ml supervisado", lambda texto: modelo.predict([texto])[0])
        except ImportError:
            print("Falta scikit-learn: pip install -r requirements.txt")

    if "embeddings" in args.metodos:
        try:
            from embeddings import construir_clasificador, predecir
            modelo = construir_clasificador()
            evaluar("embeddings", lambda texto: predecir(texto, modelo))
        except ImportError:
            print("Falta sentence-transformers: pip install sentence-transformers")

    if "llm" in args.metodos:
        from llm_local import predecir
        evaluar("llm local", predecir)


if __name__ == "__main__":
    main()
