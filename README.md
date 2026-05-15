# Reserva Iteso

Sistema multi-modelo para gestión de eventos universitarios utilizando **Cassandra, MongoDB y Dgraph**, desarrollado para el proyecto final de **Bases de Datos No Relacionales**.

## Integrantes

- Diego Alejandro Alvarez Hernández  
- Ángel Barbarín  
- Fabián Gaxiola

---

# Descripción del Proyecto

ReservaITESO es una plataforma conceptual para administrar:

- Eventos universitarios (académicos, culturales, deportivos y recreativos)
- Reservación y uso de espacios dentro del campus
- Registro histórico de asistencia y actividad de usuarios
- Análisis de relaciones entre usuarios, roles, organizadores y eventos

El proyecto usa un enfoque **polyglot persistence**, aprovechando la mejor base para cada tipo de problema.

---

# Tecnologías utilizadas

## Cassandra

Orientada a consultas históricas y patrones de acceso por tiempo.

Usada para:

- Historial de asistencia
- Historial de reservaciones
- Check-ins
- Cancelaciones
- Actividad por usuario

---

## MongoDB

Modelo documental para entidades y agregaciones.

Usada para:

- Eventos
- Espacios
- Reservaciones
- Analíticas y pipelines

---

## Dgraph

Modelo de grafo para relaciones complejas.

Usado para:

- Usuarios relacionados por eventos compartidos
- Eventos con múltiples tipos de participantes
- Participación de usuarios externos
- Relaciones entre organizadores y roles
- Uso compartido de espacios universitarios

---

# Requerimientos Funcionales

El proyecto implementa **24 requerimientos funcionales**:

- 8 Cassandra
- 8 MongoDB
- 8 Dgraph

Las consultas están agrupadas por categorías para mejorar la experiencia del usuario:

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
├── generate_csv_data.py
├── test_dgraph.py
│
├── Queries/
│   ├── __init__.py
│   ├── cassandra_queries.py
│   ├── mongo_queries.py
│   └── dgraph_queries.py
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
└── README.md
# Modelo de Datos

## Cassandra

Tablas:

- attendance_by_user
- reservations_by_user
- attendance_by_event_date
- space_usage_by_space_date
- user_activity_by_date
- checkins_by_space
- cancelled_reservations_by_user
- cancelled_reservations_by_space
- participation_by_user_activity_type

Modelo basado en Query-Driven Design.

---

## MongoDB

Colecciones:

- events
- spaces
- reservations

Incluye:

- Índices simples y compuestos
- Aggregation pipelines
- Modelo embebido para organizer_info

---

## Dgraph

Nodos:

- User
- Role
- Event
- Organizer
- Space

Relaciones:

- has_role
- participates_in
- organized_by
- takes_place_in
- uses_space

---

# Dataset

La carga de datos se realiza mediante archivos CSV generados automáticamente con `generate_csv_data.py`.

El dataset fue diseñado para generar relaciones reales entre usuarios, eventos, organizadores y espacios, permitiendo consultas significativas especialmente en Dgraph.

Dataset base:

- 100 usuarios
- 25 espacios
- 40 eventos
- 200 reservaciones
- 400 asistencias
- 250 check-ins
- 8 organizadores
- 4 roles

Los datos incluyen:

- overlap entre participantes
- usuarios internos y externos
- distintos tipos de eventos
- reservaciones canceladas
- relaciones organizador-evento
- uso compartido de espacios

Esto permite realizar consultas reales y relaciones complejas entre entidades.

---

# Instalación

## 1. Clonar repositorio

```bash
git clone https://github.com/angelbarbarin/ConviveIteso.git
cd ConviveIteso
```

---

## 2. Crear entorno virtual

```bash
python -m venv venv
```

Activar entorno virtual:

### Windows

```bash
.\venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias Python

```bash
pip install pymongo cassandra-driver pydgraph faker
```
python -m pip install --upgrade pip
pip install -r requirements.txt

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
docker run --name dgraph-convive -p 8080:8080 -p 9080:9080 -d dgraph/standalone:latest
```

---

## Verificar contenedores

```bash
docker ps
```

---

# Dgraph Ratel

Interfaz gráfica para visualizar el grafo:

```text
http://localhost:8080
```

---

# Configuración de conexión

El archivo `connect.py` concentra las conexiones a las tres bases de datos:

- Cassandra → localhost:9042
- MongoDB → localhost:27017
- Dgraph → localhost:9080

---

# Generar datasets automáticamente

El proyecto incluye un generador automático de datos realistas.

Ejecutar:

```bash
python generate_csv_data.py
```

Esto genera:

- usuarios con nombres reales
- eventos universitarios
- overlap entre participantes
- reservaciones
- check-ins
- relaciones útiles para Dgraph

Posteriormente ejecutar:

```bash
python populate.py
```

---

# Poblar bases de datos

Ejecutar:

```bash
python populate.py
```

Esto:

- crea tablas Cassandra
- crea esquema Dgraph
- carga CSV en las 3 bases
- crea índices MongoDB

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

# Experiencia de usuario

El sistema fue diseñado para que las consultas no dependan únicamente de identificadores técnicos.

Por ejemplo, los usuarios pueden realizar búsquedas utilizando:

- nombres completos
- códigos institucionales
- identificadores amigables

Ejemplos válidos:

```text
Diego Alvarez
A001
USER001
```

Esto permite que las consultas sean más naturales para el usuario final.

---

# Ejemplos de consultas

## Cassandra

- Historial reciente de asistencia por usuario
- Últimos check-ins de un espacio
- Reservaciones canceladas por espacio
- Actividad histórica por rango de fechas

---

## MongoDB

- Eventos por tipo y fecha
- Eventos con mayor demanda
- Reservaciones por tipo de espacio
- Espacios disponibles para reserva

---

## Dgraph

- Usuarios que coinciden en eventos
- Eventos con roles distintos
- Participación de usuarios externos
- Usuarios vinculados por espacios compartidos
- Organizadores relacionados con roles de usuarios

---

# Pruebas individuales

Durante el desarrollo se utilizan archivos de prueba independientes para validar consultas antes de integrarlas al menú principal.

Ejemplo:

```bash
python test_dgraph.py
```

Esto facilita el desarrollo incremental y el debugging de consultas complejas.

---

# Flujo de ejecución

1. Generar datasets automáticamente
2. Levantar bases de datos
3. Ejecutar `populate.py`
4. Ejecutar menú principal
5. Ejecutar consultas

---

# Diseño del proyecto

El proyecto sigue el principio:

## “La consulta define el modelo”

Se eligió cada base según el problema:

| Necesidad | Base elegida |
|---|---|
| Históricos por tiempo | Cassandra |
| Documentos y agregaciones | MongoDB |
| Relaciones complejas | Dgraph |

---

# Commits relevantes del avance

```bash
Initial repository structure
Database modeling implementation
CSV automatic dataset generator
Populate integration for MongoDB Cassandra and Dgraph
Grouped menu structure
User-friendly Dgraph queries
Schema and index improvements
```

---

# Posibles mejoras futuras

- API con FastAPI o Flask
- Dashboard para analíticas
- Recomendador de eventos basado en grafo
- Visualización avanzada de relaciones en Dgraph
- Reservación en tiempo real
- Sistema de autenticación
- Frontend web interactivo

---

# Curso

Proyecto desarrollado para:

**Bases de Datos No Relacionales**  
ITESO

---

# Licencia

Proyecto académico para fines educativos.

---

# Nota importante

Si es la primera vez ejecutando el proyecto:

```bash
1. Levantar contenedores Docker
2. Ejecutar generate_csv_data.py
3. Ejecutar populate.py
4. Ejecutar main.py
```

En ese orden.

---

# Solución de problemas

## Verificar contenedores activos

```bash
docker ps
```

---

## Reiniciar bases de datos

```bash
docker restart mongo-convive
docker restart cassandra-convive
docker restart dgraph-convive
```

---

## Si Cassandra tarda en conectar

Esperar aproximadamente 1 o 2 minutos después de iniciar el contenedor.

---

## Si Dgraph no responde

Verificar:

```text
http://localhost:8080
```

y confirmar que el contenedor esté activo.
