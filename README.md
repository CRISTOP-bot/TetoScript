# TetoScript

**TetoScript** es un lenguaje experimental inspirado en Kasane Teto: una propuesta de lenguaje propio con una sintaxis expresiva y familiar para quienes usan TypeScript.

> Estado: prototipo inicial. Todavía no sustituye a TypeScript ni busca compatibilidad con su ecosistema. El objetivo de este repositorio es diseñar el lenguaje y construirlo de forma incremental.

## Sintaxis que estamos explorando

La idea inicial compartida para el lenguaje fue:

```teto
 tetolog (teto%teto25) Teto else:tetolog (teto%"nose")
```

La conservamos como **propuesta de diseño**, pero su gramática y el significado de `%` y `Teto` todavía necesitan definirse; esta línea aún no se ejecuta en el prototipo. La primera sintaxis ejecutable es deliberadamente pequeña:

```teto
# examples/hello.teto
teto nombre = "Teto"
Teto nombre == "Teto":
    tetolog ("¡Hola, " + nombre + "!")
else:
    tetolog ("Hola, mundo")
```

En esta primera versión, `teto` declara una variable, `Teto condición:` inicia una condición, `else:` marca la alternativa y `tetolog (...)` imprime un valor.

## Probarlo

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```sh
python -m tetoscript examples/hello.teto
```

Ejecutar las pruebas:

```sh
python -m unittest discover -s tests -v
```

## Visión

Queremos explorar un lenguaje con tipos, funciones, módulos y herramientas de desarrollo modernas, tomando como referencia la ergonomía de TypeScript sin copiar su identidad. El diseño irá evolucionando con ejemplos, una especificación y pruebas ejecutables.

## Licencia

Aún no se ha elegido una licencia. No reutilices ni redistribuyas el código hasta que se añada una licencia explícita.
