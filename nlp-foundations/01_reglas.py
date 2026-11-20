"""Ejemplo 1: reglas manuales, SIN entrenamiento."""
import argparse
import unicodedata

MENSAJE = "Me hicieron un cargo duplicado en mi tarjeta"
REGLAS = {
    "FACTURACION": ["factura", "cobro", "me cobraron", "reembolso", "pago"],
    "ENVIOS": ["paquete", "entrega", "seguimiento", "envio"],
    "ACCESO": ["contrasena", "iniciar sesion", "no puedo entrar"],
    "SOPORTE_TECNICO": ["app", "la pagina falla", "se cierra"],
}

def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.casefold())
                   if unicodedata.category(c) != "Mn")

def clasificar(texto):
    texto = normalizar(texto)
    encontradas = [etiqueta for etiqueta, expresiones in REGLAS.items()
                   if any(patron in texto for patron in expresiones)]
    return encontradas or ["REVISAR"]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mensaje", default=MENSAJE)
    args = parser.parse_args()
    print("CASO 1: REGLAS — no se entrena un modelo")
    print("Mensaje:", args.mensaje)
    print("Resultado:", ", ".join(clasificar(args.mensaje)))
    print("Conocimiento: frases escritas directamente en REGLAS.")

if __name__ == "__main__":
    main()
