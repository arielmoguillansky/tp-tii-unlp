# TP final Tópicos II - Maestría en Ingeniería de Software - UNLP

- Este proyecto es una simple aplicación que utiliza un modelo pre entrenado para calcular las similitudes entre publicaciones inmobiliarias. 

- Trabajo hecho por Ariel Moguillansky

# Instalación y puesta en marcha

1. Clonar el repositorio al ambiente local
2. Revisar que no haya servicios utilizando los puertos utilizados por la aplicación
3. Dentro del directorio raíz del proyecto, ejecutar `docker-compose up --build`
4. La aplicación cliente se ejecutará dentro del puerto 3000.
5. Para ingresar por primera vez, ingresar un mail y registrarse en `/register`. Seleccionar un tipo de suscripción.
6. Para hacer uso del predictor, asignar URIs o Ids de entidades. Para facilitar el procesamiento, se ha límitado el número de parámetros enviados a 3. 
 - Ejemplo de URI válida: `https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1579031724`
 - Ejemplo de ID válido: 10000
7. Para ver el historial de peticiones enviadas al modelo inteligente, visitar `/logrequests`


# Arquitectura del Proyecto

Este proyecto implementa una arquitectura de microservicios para una aplicación de predicción de similitudes entre publicaciones de inmuebles. Consta de los siguientes servicios:

*   **Webapp:** La principal aplicación web que proporciona la interfaz de usuario para interactuar con el sistema.
*   **Servicio de Registro:** Gestiona las funcionalidades de registro, inicio y cierre de sesión de usuario.
*   **Servicio de Predicción:** Proporciona la funcionalidad de predicción de bienes raíces basada en un modelo entrenado.
*   **Servicio de Limitador:** Implementa la limitación de velocidad para proteger el servicio de predicción del abuso.

## Componentes

### 1. Webapp

*   **Descripción:** La aplicación web construida con Flask que sirve como interfaz de usuario.
*   **Funcionalidad:**
    *   Gestiona la autenticación de usuarios a través del Servicio de Registro.
    *   Envía solicitudes de predicción al Servicio de Predicción.
    *   Muestra los resultados de la predicción al usuario.
    *   Gestiona las sesiones de usuario utilizando Redis.
    *   Muestra las peticiones hechas por el usuario.

### 2. Servicio de Registro

*   **Descripción:** Gestiona el registro y la autenticación de usuarios.
*   **Funcionalidad:**
    *   Registra nuevos usuarios.
    *   Autentica usuarios existentes.
    *   Gestiona las sesiones de usuario utilizando Redis.
    *   Cierra sesión del usuario
    *   Mantiene la conexión con la BD para el guardado de usuarios y logs

### 3. Servicio de Predicción

*   **Descripción:** Hace uso del modelo ya entrenado para obtener resultados (scores) a partir de entidades (ut o id) proporcionadas por el usuario.
*   **Funcionalidad:**
    *   Recibe solicitudes de entidades desde la Webapp.
    *   Carga y utiliza un modelo de aprendizaje automático pre-entrenado (`trained_model.pkl`).
    *   Consulta un grafo de conocimiento para obtener información relevante para la predicción.
    *   Devuelve los resultados de la predicción a la Webapp.

### 4. Servicio de Limitador

*   **Descripción:** Implementa la limitación de velocidad para proteger el Servicio de Predicción del abuso.
*   **Funcionalidad:**
    *   Recibe solicitudes del Servicio de Predicción.
    *   Verifica si el usuario ha excedido su límite de solicitudes.
    *   Permite o deniega las solicitudes según el límite de velocidad.
    *   Para usarios Freemium, el RPM es 5.
    *   Para usuarios Preemium, el RPM es 50. 

### 5. MongoDB

*   **Descripción:** Base de datos utilizada para almacenar información de usuario y registros de solicitudes.
*   **Funcionalidad:**
    *   Almacena las credenciales de usuario y la información del perfil.
    *   Almacena los registros de solicitudes para auditoría y análisis.

### 6. Redis

*   **Descripción:** Almacén de datos en memoria utilizado para la gestión de sesiones y la limitación de velocidad.
*   **Funcionalidad:**
    *   Almacena los datos de la sesión del usuario.
    *   Almacena los recuentos de solicitudes para la limitación de velocidad.

## Tecnologías Utilizadas

*   **Python:** El lenguaje utilizado para todos los servicios.
*   **Flask:** Un micro framework web para construir la aplicación web y los servicios.
*   **MongoDB:** Base de datos NoSQL para almacenar información de usuario y registros de solicitudes.
*   **Redis:** Un almacén de datos en memoria para la gestión de sesiones y la limitación de velocidad.
*   **Docker:** Una plataforma de contenedorización para empaquetar y desplegar los servicios.
*   **Docker Compose:** Una herramienta para definir y gestionar aplicaciones Docker multi-contenedor.

## Razonamiento

El proyecto utiliza una arquitectura de microservicios para lograr los siguientes beneficios:

*   **Escalabilidad:** Cada servicio se puede escalar independientemente según sus necesidades específicas.
*   **Modularidad:** Cada servicio es una unidad autocontenida con una responsabilidad específica, lo que facilita la comprensión y el mantenimiento del código.
*   **Diversidad de Tecnologías:** Cada servicio puede utilizar las tecnologías más apropiadas para su tarea específica.
*   **Aislamiento de Fallas:** Si un servicio falla, no necesariamente derriba toda la aplicación.

El uso de MongoDB y Redis proporciona los siguientes beneficios:

*   **MongoDB:** Proporciona una base de datos flexible y escalable para almacenar información de usuario y registros de solicitudes.
*   **Redis:** Proporciona un almacenamiento rápido en memoria para la gestión de sesiones y la limitación de velocidad.

El uso de Docker y Docker Compose simplifica el despliegue y la gestión de la aplicación.

El uso de PyKeen permite que el Servicio de Predicción aproveche la incrustación y el razonamiento de grafos de conocimiento para la predicción de bienes raíces.


# Mejoras

Esta aplicación es apenas una versión de prueba de la cual se extraen muchos puntos de mejora. 

- Mejor gestión de los datos almacenados en Redis.
- Implementación de sistemas de guardado de sesión (cookie, session storage) para consultas más rápidas.
- Mejora en la seguridad y acceso a datos de usuario
- Implementación de una API gateway como punto de entrada central para todas las solicitudes desde la aplicación web. Se puede usar un proxy inverso con reglas de enrutamiento.