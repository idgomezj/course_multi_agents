# Tres enfoques de NLP — demostraciones ejecutables

Los tres programas usan inicialmente el mismo mensaje: «Me hicieron un cargo duplicado en mi tarjeta».
Son demostraciones docentes independientes; no son una evaluación automática de estudiantes.

| Enfoque | Archivo | Cómo clasifica | ¿Entrenamos nosotros? |
|---|---|---|---|
| Reglas | [01_reglas.py](01_reglas.py) | Busca expresiones registradas por el programador | No |
| Machine Learning supervisado | [02_ml_supervisado.py](02_ml_supervisado.py) | Aprende de 40 mensajes etiquetados con TF-IDF + regresión logística | Sí, al ejecutar fit() |
| Modelo preentrenado | [03_preentrenado.py](03_preentrenado.py) | Carga un modelo multilingüe de Hugging Face entrenado por terceros | No |

## Ejecución desde la raíz del repositorio

1. Solo reglas, sin instalar paquetes: `python3 nlp-foundations/01_reglas.py`
2. ML supervisado: instalar `python3 -m pip install -r nlp-foundations/requirements_ml.txt` y ejecutar `python3 nlp-foundations/02_ml_supervisado.py`
3. Preentrenado: instalar `python3 -m pip install -r nlp-foundations/requirements_preentrenado.txt` y ejecutar `python3 nlp-foundations/03_preentrenado.py`

La primera ejecución del tercero descarga los pesos desde Hugging Face: requiere internet y puede tardar. Conviene instalarlo antes de la clase.

Todos permiten probar otra frase usando `--mensaje`. Por ejemplo:

    python3 nlp-foundations/01_reglas.py --mensaje "No puedo iniciar sesión"
    python3 nlp-foundations/02_ml_supervisado.py --mensaje "No puedo iniciar sesión"
    python3 nlp-foundations/03_preentrenado.py --mensaje "No puedo iniciar sesión"

## Qué deberías observar

- Con la frase original, **reglas** devuelve REVISAR porque no figura la expresión «cargo duplicado».
- El **ML supervisado** se entrena con 40 ejemplos al ejecutar el script; en la verificación local devolvió FACTURACION.
- El **preentrenado** devuelve puntuaciones por etiqueta. No inventamos su resultado: debe comprobarse al descargar y ejecutarlo.
- Los casos 2 y 3 seleccionan **una única categoría**; no sirven directamente para el ejercicio de intenciones múltiples.
- Los tres pueden fallar con lenguaje nuevo. Una demostración no mide su calidad en producción.

## Nota para clase

No confundir NLP con una arquitectura neuronal concreta. El primer enfoque son reglas, el segundo TF-IDF con regresión logística, y el tercero reutiliza pesos aprendidos antes para clasificación zero-shot.
El código anterior [demo_nlp.py](demo_nlp.py) sigue disponible como demostración de reglas con spaCy y varias intenciones.

Fuentes: [scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) · [Modelo zero-shot multilingüe](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli)
