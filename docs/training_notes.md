# Notas de entrenamiento para carros de juguete

## Dataset recomendado

Para que YOLO aprenda carros de juguete y no solo carros reales, usa imagenes propias de tu entorno.

Cantidad minima:

- Prueba rapida: 80-150 imagenes.
- Primer modelo decente: 300-500 imagenes.
- Modelo robusto: 1000+ imagenes.

## Variaciones importantes

- Luces: dia, noche, sombra, lampara directa.
- Fondo: mesa, piso, cartulina, pista, cuaderno, mano cerca.
- Angulo: frontal, lateral, superior, diagonal.
- Distancia: carro pequeno, mediano y grande dentro del frame.
- Casos dificiles: dos carros juntos, carro parcialmente tapado, fondo con objetos parecidos.

## Etiquetado

Etiqueta solo el carro de juguete visible. Si hay varios, crea una caja para cada uno. La caja debe cubrir el objeto, no toda la mesa.

## Prueba despues de entrenar

1. Copia `runs/detect/toy_car_detector/weights/best.pt` a `models/toy_car_best.pt`.
2. Ejecuta `python scripts/live_detect.py`.
3. Si detecta falsos positivos, agrega esas escenas al dataset y reentrena.
