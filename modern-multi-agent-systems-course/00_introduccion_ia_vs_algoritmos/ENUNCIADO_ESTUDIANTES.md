# Reto inicial — ¿Un programa entiende los mensajes?

## El problema

Trabajas en el equipo de soporte de una empresa. Recibes mensajes escritos por clientes en español y debes enviarlos a uno de cuatro equipos:

- **acceso:** contraseñas, usuario, autenticación o inicio de sesión.
- **facturacion:** pagos, cargos, comprobantes, facturas.
- **soporte_tecnico:** errores de la aplicación, fallas técnicas, sistema caído.
- **envios:** entrega, paquete, dirección, seguimiento de pedido.

Cada mensaje debe tener exactamente una categoría.

## Ejemplos

| Mensaje | Equipo correcto |
|---|---|
| Olvidé mi contraseña | acceso |
| Necesito el recibo de mi compra | facturacion |
| La pantalla se queda en blanco | soporte_tecnico |
| Mi paquete no ha llegado | envios |

## Parte A. Sin usar IA (15 minutos)

En parejas, escriban un algoritmo **con condiciones if/else o pseudocódigo**. ¿Qué palabras buscarían? ¿En qué orden aplicarían las reglas? ¿Qué harían con una frase desconocida?

Ahora pruébenlo mentalmente con:

1. «¿Cómo cambio la clave para entrar?»
2. «Me aparece un cobro duplicado».
3. «El sitio se queda congelado».
4. «¿Dónde está lo que compré?».
5. «No puedo acceder a la factura».

No cambien las reglas hasta apuntar cuáles fallaron y por qué.

## Parte B. Con IA

El docente enseñará tres alternativas: aprender de ejemplos (ML supervisado), comparar significados (embeddings) y consultar un modelo de lenguaje (LLM).

**Antes de ejecutarlas:** voten qué alternativa creen que tendrá más aciertos y cuál será más barata, rápida, privada y fácil de explicar.

## Parte C. Discusión

- ¿Un programa con muchos if/else es IA?
- ¿Un modelo de lenguaje conoce realmente el estado del pedido?
- ¿Una IA puede equivocarse con mucha confianza?
- ¿Qué tarea debería seguir siendo una regla determinista?
- ¿Cuál sería la diferencia entre clasificar una solicitud y crear un agente que actúe sobre ella?

## Entrega ligera

Un esquema de reglas, dos casos donde fallan, una comparación de métodos y una decisión de ingeniería justificada. No se evalúa memorizar bibliotecas ni instalar un modelo grande.
