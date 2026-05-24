# Coloca aqui tus archivos SUMO

Copia en esta carpeta el archivo de red de SUMO, por ejemplo:

- `OSM.net.xml`
- `osm.net.xml`
- `OSM.ntxml.js` si es un JS que contiene el XML exportado
- `.sumocfg`, `.rou.xml`, etc.

El dashboard busca automaticamente una red en este orden:

1. `sumo/OSM.net.xml`
2. `sumo/osm.net.xml`
3. cualquier `*.net.xml`
4. cualquier archivo con `ntxml` en el nombre

Si solo tienes un `.js`, el parser intentara extraer el bloque XML que contiene `<net ...> ... </net>`.
