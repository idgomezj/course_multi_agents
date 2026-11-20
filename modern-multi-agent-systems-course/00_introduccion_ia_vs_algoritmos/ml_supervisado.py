"""Solución 2: ML supervisado. Aprende parámetros de ejemplos etiquetados.

Requiere: pip install scikit-learn
"""
from datos import ENTRENAMIENTO, PRUEBA


def construir_modelo():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline

    textos = [texto for texto, _ in ENTRENAMIENTO]
    categorias = [categoria for _, categoria in ENTRENAMIENTO]
    modelo = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True),
        LogisticRegression(max_iter=1000, random_state=42),
    )
    modelo.fit(textos, categorias)
    return modelo


def main() -> None:
    modelo = construir_modelo()
    for texto, esperado in PRUEBA[:8]:
        prediccion = modelo.predict([texto])[0]
        confianza = max(modelo.predict_proba([texto])[0])
        print(f"{prediccion:17} | p={confianza:.2f} | esperado: {esperado:17} | {texto}")
    print("\n¡Una probabilidad de modelo NO garantiza que la respuesta sea correcta!")


if __name__ == "__main__":
    main()
