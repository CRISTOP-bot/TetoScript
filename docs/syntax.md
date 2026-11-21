# Borrador de sintaxis

Este documento describe solo el subconjunto experimental implementado en `0.1.0`.

## Declaración

```teto
teto identificador = expresión
```

## Salida

```teto
tetolog (expresión)
```

## Condicional

```teto
Teto expresión_booleana:
    # bloque verdadero
else:
    # bloque alternativo
```

## Expresiones disponibles

Literales de texto, números, booleanos de Python (`True`/`False`), variables, `+`, `-`, `*`, `/`, comparaciones `==`, `!=`, `<`, `<=`, `>` y `>=`, operadores `and`, `or` y `not`.

## Pendiente de diseño

La forma `tetolog (teto%teto25) Teto else:tetolog (teto%"nose")` es una propuesta del autor. Aún no están definidos formalmente `%`, `Teto` en esa forma compacta, la precedencia ni el significado completo de la expresión. No forma parte todavía de la gramática ejecutable.
