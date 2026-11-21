# TetoScript 0.2 — borrador ejecutable de sintaxis

TetoScript es un lenguaje propio, interpretado y de tipado dinámico con anotaciones opcionales comprobadas al ejecutar. Las palabras y nombres se inspiran en Teto; el lenguaje no es compatible con TypeScript ni pretende ocultar que es un prototipo.

## Variables y tipos

```teto
teto nombre: string = "Teto"
teto edad: number = 25
teto activo: boolean = true
```

Tipos de anotación disponibles: `string`, `number`, `boolean` y `bool`. Las anotaciones se validan al ejecutar; todavía no hay análisis estático ni inferencia de tipos formal.

## Salida

```teto
tetolog("Teto%Teto25")
```

`tetolog` imprime un argumento. La propuesta original `tetolog (teto%teto25)` no es equivalente a una concatenación: `%` es el operador módulo numérico; para mostrar el texto se usan comillas. Esto evita confundir operadores con contenido.

## Condicional

```teto
Teto (edad % 2 == 1) {
    tetolog("impar")
} else {
    tetolog("par")
}
```

`Teto (condición) { ... } else { ... }` conserva la palabra característica propuesta y usa llaves para delimitar bloques sin ambigüedad.

## Funciones

```teto
teto fn saludo(persona: string) -> string {
    return "Hola, " + persona
}

tetolog(saludo("Teto"))
```

## Operadores y valores

Aritmética `+ - * / %`; comparaciones `== != < <= > >=`; lógicos `and`, `or`, `not` y equivalentes `&&`, `||`, `!`; booleanos `true` y `false`; ausencia de valor `nose` (también acepta `null`). `#` inicia comentarios.

## Alcance de esta versión

El intérprete ejecuta variables, anotaciones, funciones, `return`, bloques condicionales, llamadas e impresiones. Aún faltan análisis estático, bucles, módulos, arrays/objetos, manejo formal de errores, formato/linter, editor y compilador. La sintaxis y semántica pueden evolucionar antes de una versión estable.
