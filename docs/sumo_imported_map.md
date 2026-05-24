# SUMO del proyecto

El proyecto usa el mapa simple original:

```text
sumo/sample_intersection.net.xml
```

Se quito el mapa importado desde `map.zip` para mantener una simulacion pequena, estable y facil de explicar en la entrega.

Este mapa representa una interseccion sencilla con entradas y salidas, suficiente para explicar:

- nodos/intersecciones,
- aristas/calles,
- carriles,
- semaforo,
- conteo y decision de tiempo verde.

## Para abrirlo en SUMO

Si SUMO esta instalado y quieres abrir el archivo simple, puedes usar NetEdit o crear una configuracion `.sumocfg` a partir de `sample_intersection.net.xml`.

Para el dashboard no necesitas abrir SUMO GUI: la pagina lee directamente el archivo `.net.xml`.

## Nota

El archivo `map.zip` no se usa en esta version del proyecto.
