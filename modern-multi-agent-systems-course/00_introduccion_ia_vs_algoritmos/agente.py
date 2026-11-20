"""Mini-agente didáctico: observar -> decidir -> validar -> actuar.

Una herramienta SIMULADA, sin conexión a servicios reales. No es un sistema
multiagente ni un agente LLM autónomo. Se puede sustituir 'reglas' por un modelo.
"""
import argparse
from datetime import datetime, timezone
from reglas import predecir

EQUIPOS = {
    "acceso": "mesa_identidades",
    "facturacion": "mesa_pagos",
    "soporte_tecnico": "mesa_tecnica",
    "envios": "mesa_logistica",
}


def herramienta_crear_ticket(texto: str, equipo: str) -> dict:
    # Ejemplo seguro: no envía ninguna solicitud y no escribe archivos.
    return {
        "simulado": True,
        "equipo": equipo,
        "resumen": texto[:80],
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
    }


def ejecutar(texto: str, aprobado: bool = False) -> dict:
    categoria = predecir(texto)
    if categoria not in EQUIPOS:
        return {"estado": "revision_humana", "motivo": "No se pudo clasificar"}
    if not aprobado:
        return {"estado": "pendiente_aprobacion", "categoria": categoria}
    ticket = herramienta_crear_ticket(texto, EQUIPOS[categoria])
    return {"estado": "accion_simulada", "categoria": categoria, "ticket": ticket}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texto", default="No puedo iniciar sesión")
    parser.add_argument("--aprobar", action="store_true", help="Solo autoriza la simulación")
    args = parser.parse_args()
    print(ejecutar(args.texto, aprobado=args.aprobar))
    print("Para simular la acción, añade --aprobar. Nunca crea tickets reales.")


if __name__ == "__main__":
    main()
