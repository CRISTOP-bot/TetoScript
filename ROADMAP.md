# Roadmap

TetoScript está en fase de diseño y prototipo. La prioridad es convertir el lenguaje en algo consistente y comprobable, no prometer compatibilidad con TypeScript antes de construirla.

## Hecho en 0.4.0

- Lexer propio y parser con precedencia de operadores.
- Intérprete sin `eval` ni ejecución de código Python fuente.
- Variables, comentarios, `tetolog`, expresiones y condicional `Teto (...) { ... } else { ... }`.
- Funciones, parámetros tipados, retorno y comprobaciones de tipos básicos en runtime.
- Pruebas automatizadas y ejemplo ejecutable.
- `teto check` valida sintaxis, nombres y tipos básicos sin ejecutar el archivo.
- Logo oficial proporcionado por el creador, integrado al README.
- Verificador estático inicial para nombres, tipos de variables, argumentos y tipos de retorno.

## Próximas etapas

1. Especificar semántica y mensajes de error; decidir estilo de nombres, mutabilidad y política de tipos.
2. Añadir asignación y estructuras de datos con pruebas de compatibilidad.
3. Añadir bucles y módulos/importaciones con manejo seguro de rutas.
4. Completar análisis de flujo, inferencia y cobertura de rutas de retorno; el verificador básico y `teto check` ya existen.
5. Formateador, linter y documentación de API.
6. Evaluar si conviene compilar a JavaScript para acercarse a los casos de uso de TypeScript; no afirmar compatibilidad hasta probarla.
7. Elegir y publicar una licencia explícita antes de aceptar contribuciones de código.

Las etapas futuras no se consideran implementadas hasta que estén integradas y cubiertas por pruebas reales.
