Actividad 1 — Clasificación automática de solicitudes de clientes

Enunciado del problema

Una empresa de comercio electrónico recibe diariamente cientos de mensajes de sus clientes a través de su plataforma de atención al usuario.

Actualmente, un empleado debe leer cada mensaje, identificar el motivo de la solicitud y asignarlo manualmente al departamento encargado de atenderla.

La empresa cuenta con cuatro departamentos:

Departamento

Responsabilidad

Acceso

Problemas con cuentas, contraseñas, usuarios e inicio de sesión.

Facturación

Consultas sobre pagos, cobros, facturas y reembolsos.

Soporte técnico

Errores, fallas y dificultades de funcionamiento de la aplicación.

Envíos

Consultas sobre pedidos, entregas, direcciones y paquetes.

La empresa desea desarrollar un programa que reciba el mensaje de un cliente, analice su contenido y determine automáticamente a cuál de los cuatro departamentos debe asignarse.

Ejemplo

Entrada:

"Olvidé mi contraseña y no puedo ingresar a mi cuenta".

Salida esperada:

ACCESO

Casos de prueba

#

Mensaje recibido

Departamento esperado

1

No puedo ingresar a mi cuenta.

Acceso

2

Me cobraron dos veces por el mismo producto.

Facturación

3

La aplicación se cierra inesperadamente.

Soporte técnico

4

Mi paquete todavía no ha llegado.

Envíos

5

Necesito recuperar mis credenciales.

Acceso

6

Quiero saber dónde está mi compra.

Envíos

7

La página se queda congelada.

Soporte técnico

8

Me descontaron dinero que no debía.

Facturación

Actividad para los estudiantes

Parte 1. Solución mediante programación tradicional

Diseñe un algoritmo que permita clasificar automáticamente los mensajes utilizando estructuras de programación convencionales, como condicionales, ciclos y funciones.

Implemente su solución en Python.

Parte 2. Evaluación de la solución

Pruebe su algoritmo con los ocho mensajes proporcionados y determine cuántos clasifica correctamente.

Posteriormente, analice cómo se comportaría ante mensajes que utilizan expresiones diferentes a las contempladas inicialmente.

