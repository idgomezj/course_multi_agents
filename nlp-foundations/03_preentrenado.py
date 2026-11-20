"""Ejemplo 3: clasificador zero-shot con un MODELO PREENTRENADO.

Instalación: python3 -m pip install -r nlp-foundations/requirements_preentrenado.txt
Internet es necesario para descargar los pesos la primera vez.
"""
import argparse

MODELO = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"
MENSAJE = "Me hicieron un cargo duplicado en mi tarjeta"
ETIQUETAS = [
    "problemas de facturación y cobros",
    "problemas de envíos o entregas",
    "problemas para acceder a la cuenta",
    "problemas técnicos de una aplicación",
]

def clasificar(texto):
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise SystemExit("Instala primero: python3 -m pip install -r nlp-foundations/requirements_preentrenado.txt") from exc
    clasificador = pipeline("zero-shot-classification", model=MODELO, device=-1)
    return clasificador(
        texto,
        candidate_labels=ETIQUETAS,
        hypothesis_template="Este mensaje trata sobre {}.",
        multi_label=False,
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mensaje", default=MENSAJE)
    args = parser.parse_args()
    print("CASO 3: MODELO PREENTRENADO — sin entrenamiento local")
    print("Modelo:", MODELO)
    print("Mensaje:", args.mensaje)
    resultado = clasificar(args.mensaje)
    print("Puntuaciones por categoría (no son probabilidades calibradas):")
    for categoria, puntuacion in zip(resultado["labels"], resultado["scores"]):
        print(f"  {categoria}: {puntuacion:.1%}")
    print("El entrenamiento de este modelo lo realizaron terceros.")

if __name__ == "__main__":
    main()
