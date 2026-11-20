"""Solución 3: similitud de significado mediante embeddings preentrenados.

Requiere: pip install sentence-transformers
Descarga inicial del modelo, ejecuta localmente después.
"""
from datos import ENTRENAMIENTO, PRUEBA

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def construir_clasificador():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(MODELO)
    textos = [texto for texto, _ in ENTRENAMIENTO]
    categorias = [categoria for _, categoria in ENTRENAMIENTO]
    vectores = modelo.encode(textos, normalize_embeddings=True, show_progress_bar=False)
    return modelo, np.asarray(vectores), categorias


def predecir(texto, clasificador):
    import numpy as np

    modelo, vectores, categorias = clasificador
    consulta = modelo.encode([texto], normalize_embeddings=True)[0]
    similitudes = vectores @ np.asarray(consulta)
    mejor = int(np.argmax(similitudes))
    return categorias[mejor]  # vecino más parecido: didáctico, no producción


def main():
    clasificador = construir_clasificador()
    for texto, esperado in PRUEBA[:8]:
        print(f"{predecir(texto, clasificador):17} | esperado: {esperado:17} | {texto}")


if __name__ == "__main__":
    main()
