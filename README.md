# ConviveITESO

Sistema multi-modelo para gestión de eventos universitarios utilizando **Cassandra, MongoDB y Dgraph**, desarrollado para el proyecto final de **Bases de Datos No Relacionales**.

## Integrantes

* Diego Alejandro Alvarez Hernández
* Ángel Barbarín
* (Agregar integrantes restantes si aplica)

---

# Descripción del Proyecto

ConviveITESO es una plataforma conceptual para administrar:

* Eventos universitarios (académicos, culturales, deportivos y recreativos)
* Reservación y uso de espacios dentro del campus
* Registro histórico de asistencia y actividad de usuarios
* Análisis de relaciones entre usuarios, roles, organizadores y eventos

El proyecto usa un enfoque **polyglot persistence**, aprovechando la mejor base para cada tipo de problema:

## Tecnologías utilizadas

### Cassandra

Orientada a consultas históricas y patrones de acceso por tiempo.

Usada para:

* Historial de asistencia
* Historial de reservaciones
* Check-ins
* Cancelaciones
* Actividad por usuario

## MongoDB

Modelo documental para entidades y agregaciones.

Usada para:

* Eventos
* Espacios
* Reservaciones
* Analíticas y pipelines

## Dgraph

Modelo de grafo para relaciones complejas.

Usado para:

* Coincidencias entre usuarios
* Roles en eventos
* Participación externa
* Relaciones entre organizadores, usuarios y espacios

---

# Requerimientos Funcionales

El proyecto implementa **24 requerimientos funcionales**:

* 8 Cassandra
* 8 MongoDB
* 8 Dgraph

Consultas agrupadas en:

1. Historial y actividad de usuarios
2. Consulta de eventos
3. Consulta de espacios y reservaciones
4. Analíticas y métricas
5. Relaciones en grafo

Esto permite un menú más usable que mostrar 24 consultas individuales.

---

# Estructura del Proyecto

```bash
ConviveIteso/
│
├── main.py
├── connect.py
├── populate.py
│
├── data/
│   ├── users.csv
│   ├── roles.csv
│   ├── spaces.csv
│   ├── organizers.csv
│   ├── events.csv
│   ├── attendance.csv
│   ├── reservations.csv
│   └── checkins.csv
│
├── cassandra/
├── mongo/
├── dgraph/
│
└── README.md
```

---

# Modelo de Datos

## Cassandra

Tablas:

* attendance_by_user
* reservations_by_user
* attendance_by_event_date
* space_usage_by_space_date
* user_activity_by_date
* checkins_by_space
* cancelled_reservations_by_user
* cancelled_reservations_by_space
* participation_by_user_activity_type

Modelo basado en Query-Driven Design.

---

## MongoDB

Colecciones:

* events
* spaces
* reservations

Incluye:

* Índices simples y compuestos
* Aggregation pipelines
* Modelo embebido para organizer_info

---

## Dgraph

Nodos:

* User
* Role
* Event
* Organizer
* Space

Relaciones:

* has_role
* participates_in
* organized_by
* takes_place_in
* uses_space

---

# Dataset

Carga inicial mediante archivos CSV.

Dataset base:

* 100 usuarios
* 25 espacios
* 40 eventos
* 200 reservaciones
* 400 asistencias
* 250 check-ins
* 8 organizadores
* 4 roles

Los datos fueron diseñados con overlap entre usuarios y eventos para permitir consultas significativas en Dgraph.

---

# Instalación

## 1 Clonar repositorio

```bash
git clone https://github.com/angelbarbarin/ConviveIteso.git
cd ConviveIteso
```

---

## 2 Instalar dependencias Python

```bash
pip install pymongo cassandra-driver pydgraph faker
```

---

# Levantar Bases de Datos con Docker

## Cassandra

```bash
docker run --name cassandra-convive -p 9042:9042 -d cassandra:4.1
```

---

## MongoDB

```bash
docker run --name mongo-convive -p 27017:27017 -d mongo
```

---

## Dgraph

```bash
docker run -it -p 8080:8080 -p 9080:9080 dgraph/standalone:latest
```

Ratel UI:

```text
http://localhost:8080
```

---

# Configuración de conexión

Ajustar `connect.py` según entorno local:

* Cassandra → localhost:9042
* MongoDB → localhost:27017
* Dgraph → localhost:9080

---

# Poblar datos

Ejecutar:

```bash
python populate.py
```

Esto:

* crea tablas Cassandra
* crea esquema Dgraph
* carga CSV en las 3 bases
* crea índices MongoDB

---

# Ejecutar proyecto

```bash
python main.py
```

Menú principal:

```text
1 Historial y actividad de usuarios
2 Consulta de eventos
3 Consulta espacios y reservaciones
4 Analíticas y métricas
5 Relaciones en grafo
0 Salir
```

---

# Ejemplos de consultas

## Cassandra

* Historial reciente de asistencia por usuario
* Últimos check-ins de un espacio
* Reservaciones canceladas por espacio

## MongoDB

* Eventos por tipo y fecha
* Eventos con mayor demanda
* Reservaciones por tipo de espacio

## Dgraph

* Usuarios que coinciden en eventos
* Eventos con roles distintos
* Participación de usuarios externos

---

# Flujo de ejecución

1. Conectar a las tres bases
2. Poblar datos con CSV
3. Ejecutar menú
4. Seleccionar categoría
5. Ejecutar consulta

---

# Diseño del proyecto

El proyecto sigue el principio:

**La consulta define el modelo.**

Se eligió cada base según el problema:

| Necesidad                 | Base elegida |
| ------------------------- | ------------ |
| Históricos por tiempo     | Cassandra    |
| Documentos y agregaciones | MongoDB      |
| Relaciones complejas      | Dgraph       |

---

# Commits relevantes del avance

Ejemplos (actualizar con hashes reales):

```bash
Initial repository structure
Multi-database modeling added
Populate script with CSV loading
Main menu grouped by sections
Final intermediate delivery fixes
```

---

# Posibles mejoras futuras

* API con FastAPI/Flask
* Dashboard para analíticas
* Recomendador de eventos por grafo
* Visualización de relaciones en Dgraph
* Reservación en tiempo real

---

# Curso

Proyecto desarrollado para:

**Bases de Datos No Relacionales**
ITESO

---

# Licencia

Proyecto académico para fines educativos.

---

## Nota

Si es la primera vez corriendo el proyecto:

```bash
1. Levantar contenedores
2. Ejecutar populate.py
3. Ejecutar main.py
```

En ese orden.

---

Si hay errores de conexión:

Verificar:

```bash
docker ps
```

y revisar que Cassandra, Mongo y Dgraph estén activos.
