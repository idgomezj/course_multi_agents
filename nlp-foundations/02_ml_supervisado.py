"""Ejemplo 2: NLP con Machine Learning — ENTRENAMOS con datos etiquetados.

Dependencias: python3 -m pip install -r nlp-foundations/requirements_ml.txt
"""
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

MENSAJE = "Me hicieron un cargo duplicado en mi tarjeta"

DATOS = {
    "FACTURACION": [
        "me aparece un cargo extraño en la tarjeta",
        "la factura tiene un monto incorrecto",
        "se repitió el cargo de la compra",
        "quiero un reembolso por el pago",
        "el banco registró dos cargos por la misma compra",
        "debo pagar una factura que ya está pagada",
        "me cobraron dos veces por el mismo producto",
        "necesito una devolución de dinero",
        "el importe de mi factura está mal",
        "tengo un cargo adicional en la cuenta bancaria",
    ],
    "ENVIOS": [
        "mi paquete todavía no ha llegado",
        "el transportista perdió mi envío",
        "quiero conocer el estado de la entrega",
        "el pedido está retrasado",
        "necesito la fecha de llegada del paquete",
        "me entregaron la caja incompleta",
        "no veo el seguimiento del envío",
        "la compra no llega a mi dirección",
        "dónde está mi pedido comprado ayer",
        "hay un retraso con el paquete",
    ],
    "ACCESO": [
        "no puedo ingresar en mi cuenta",
        "olvidé mi contraseña de acceso",
        "mi usuario está bloqueado",
        "necesito restablecer mis credenciales",
        "no funciona el inicio de sesión",
        "quiero recuperar la clave de mi usuario",
        "al iniciar sesión sale contraseña incorrecta",
        "la cuenta está suspendida",
        "cómo puedo acceder a mi perfil",
        "perdí la contraseña de la cuenta",
    ],
    "SOPORTE_TECNICO": [
        "la aplicación se cierra inesperadamente",
        "la página web muestra un error",
        "la app está congelada",
        "el sistema no responde al hacer clic",
        "hay un problema técnico en el sitio",
        "el enlace está roto y no carga",
        "desde la actualización hay fallos",
        "la pantalla se queda en blanco",
        "el botón no funciona en la aplicación",
        "la plataforma se bloquea cuando la abro",
    ],
}

def entrenar():
    textos = [frase for ejemplos in DATOS.values() for frase in ejemplos]
    etiquetas = [nombre for nombre, ejemplos in DATOS.items() for _ in ejemplos]
    modelo = make_pipeline(
        TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2)),
        LogisticRegression(max_iter=1500, random_state=7),
    )
    modelo.fit(textos, etiquetas)  # AQUÍ sí aprendemos los pesos con ejemplos.
    return modelo, len(textos)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mensaje", default=MENSAJE)
    args = parser.parse_args()
    modelo, total = entrenar()
    print("CASO 2: ML SUPERVISADO — entrenamiento local")
    print("Ejemplos etiquetados:", total)
    print("Mensaje:", args.mensaje)
    print("Predicción:", modelo.predict([args.mensaje])[0])
    print("Limitación: 40 ejemplos y una sola etiqueta no prueban generalización.")

if __name__ == "__main__":
    main()
