# Proyecto Final — Agentic Operations Intelligence Challenge

## Su misión

La aplicación, el Manager, las tools y la infraestructura ya están construidos.

Su equipo solo modifica:

1. sus modelos PyTorch;
2. la configuración/estrategia RAG permitida;
3. sus Skills.

Toda la información empresarial de su caso se obtiene en runtime mediante la **Data API del curso**. Su token solo debe permitir acceso al equipo asignado.

## El sistema debe

- producir un plan mensual integrado;
- cumplir demanda/servicio;
- respetar materiales, capacidad, proveedores y políticas;
- manejar la incertidumbre particular del caso;
- minimizar el costo operacional total.

## No pueden modificar

- Manager Agent;
- backend/framework;
- frontend;
- implementación de tools;
- simulador;
- motor de costos;
- evaluator;
- schemas;
- Data API.

## No deben almacenar copias locales de los datos

No creen una copia del dataset o documentos RAG para evitar la API. El training script y el runtime solicitan la información al servicio usando `DATA_API_URL` y `DATA_API_TOKEN`.

La evaluación final utilizará escenarios no vistos durante el desarrollo.
