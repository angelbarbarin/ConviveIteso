"""
PLAN DE POBLACIÓN DE DATOS - CONVIVE ITESO

1. Generar usuarios de prueba:
   - estudiantes
   - profesores
   - administrativos
   - organizadores
   - externos

2. Generar organizadores:
   - coordinaciones
   - departamentos
   - áreas universitarias

3. Generar espacios:
   - auditorios
   - salas de estudio
   - zonas recreativas
   - espacios de trabajo colaborativo

4. Generar eventos:
   - académicos
   - culturales
   - deportivos
   - recreativos

5. Poblar MongoDB:
   - colección events
   - colección spaces
   - colección reservations

6. Poblar Cassandra:
   - attendance_by_user
   - reservations_by_user
   - attendance_by_event_date
   - space_usage_by_space_date
   - user_activity_by_date
   - checkins_by_space
   - cancelled_reservations_by_user
   - cancelled_reservations_by_space
   - participation_by_user_activity_type

7. Poblar Dgraph:
   - nodos User, Role, Event, Organizer, Space
   - relaciones has_role, participates_in, organized_by,
     takes_place_in, uses_space

8. Fuente de datos sugerida:
   - Faker para usuarios y nombres
   - JSON para eventos y espacios
   - scripts de prueba para historiales y relaciones
"""