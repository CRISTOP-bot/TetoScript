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

El intérprete ejecuta variables, anotaciones, funciones, `return`, bloques condicionales, llamadas e impresiones. El análisis estático inicial existe, pero aún faltan bucles, módulos, arrays/objetos, cobertura de rutas de retorno, manejo formal de errores, formato/linter, editor y compilador. La sintaxis y semántica pueden evolucionar antes de una versión estable.

## Análisis estático con `teto check`

```sh
teto check programa.teto
```

El comando tokeniza, parsea y comprueba estáticamente nombres definidos, tipos anotados, tipos de los argumentos, tipos de retorno y condiciones booleanas. No ejecuta expresiones. El analizador aún no verifica que todas las rutas de una función devuelvan un valor ni analiza flujo complejo.


## Reasignación

Las variables declaradas con `teto` son mutables. Una reasignación actualiza una variable ya existente; no crea nombres nuevos. El tipo inferido o anotado se conserva y `teto check` informa si intentas asignarle otro tipo.

```teto
teto contador: number = 0
contador = contador + 1
```

## Bucles

```teto
teto contador: number = 0
while (contador < 3) {
    tetolog(contador)
    contador = contador + 1
}
```

La condición debe ser booleana según el analizador estático. El intérprete detiene cada bucle después de 100 000 iteraciones como protección frente a ciclos accidentales; `break` y `continue` todavía no existen.
