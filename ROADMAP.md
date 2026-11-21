# Roadmap

TetoScript está en fase de diseño y prototipo. La prioridad es convertir el lenguaje en algo consistente y comprobable, no prometer compatibilidad con TypeScript antes de construirla.

## Hecho en 0.3.0

- Lexer propio y parser con precedencia de operadores.
- Intérprete sin `eval` ni ejecución de código Python fuente.
- Variables, comentarios, `tetolog`, expresiones y condicional `Teto (...) { ... } else { ... }`.
- Funciones, parámetros tipados, retorno y comprobaciones de tipos básicos en runtime.
- Pruebas automatizadas y ejemplo ejecutable.
- Comando `teto check` para validar sintaxis sin ejecutar el archivo.
- Logo oficial proporcionado por el creador, integrado al README.

## Próximas etapas

1. Especificar semántica y mensajes de error; decidir estilo de nombres, mutabilidad y política de tipos.
2. Añadir asignación y estructuras de datos con pruebas de compatibilidad.
3. Añadir bucles y módulos/importaciones con manejo seguro de rutas.
4. Incorporar análisis estático antes de ejecución y un modo `teto check`.
5. Formateador, linter y documentación de API.
6. Evaluar si conviene compilar a JavaScript para acercarse a los casos de uso de TypeScript; no afirmar compatibilidad hasta probarla.
7. Elegir y publicar una licencia explícita antes de aceptar contribuciones de código.

Las etapas futuras no se consideran implementadas hasta que estén integradas y cubiertas por pruebas reales.
