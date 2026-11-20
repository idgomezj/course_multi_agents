"""Solución 1: reglas escritas por personas. Cero IA y cero dependencias."""
import re
import unicodedata
from datos import PRUEBA

PALABRAS = {
    "acceso": ("contrasena", "clave", "login", "sesion", "usuario", "ingresar"),
    "facturacion": ("factura", "pago", "cobro", "cobr", "recibo", "tarjeta"),
    "soporte_tecnico": ("error", "aplicacion", "pantalla", "no carga", "sistema", "boton"),
    "envios": ("paquete", "pedido", "envio", "entrega", "direccion", "seguimiento"),
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def predecir(texto: str) -> str:
    normalizado = normalizar(texto)
    for categoria, palabras in PALABRAS.items():
        if any(palabra in normalizado for palabra in palabras):
            return categoria
    return "otro"  # No forzar una respuesta falsa por falta de coincidencia.


def main() -> None:
    for texto, esperado in PRUEBA[:8]:
        prediccion = predecir(texto)
        print(f"{prediccion:17} | esperado: {esperado:17} | {texto}")


if __name__ == "__main__":
    main()
