# Dataset para entrenar carritos de juguete

## Clase del proyecto

El primer modelo personalizado debe usar una sola clase:

```text
0 toy_car
```

Cada carrito visible en una imagen necesita su propia caja. Si aparecen seis carritos, van seis cajas.

## Fotos necesarias

Para iniciar pruebas:

- 80 a 150 imagenes: prueba rapida.
- 300 a 500 imagenes: primer modelo util.
- 1000 o mas imagenes: modelo mas resistente a cambios de luz, fondo y angulo.

## Como tomar las fotos

Usa la ESP32-CAM y tambien puedes usar fotos del celular para enriquecer el dataset. Debe haber variacion:

- Carritos fuera del empaque.
- Carritos dentro del empaque plastico, como la foto que enviaste.
- Un carrito solo.
- Varios carritos juntos.
- Carritos parcialmente tapados.
- Fondo de mesa, piso, carretera de juguete, cuaderno y carton.
- Luz natural, luz artificial, sombra y reflejos.
- Camara cerca, lejos, lateral, superior y diagonal.

## Captura desde ESP32-CAM

```powershell
python scripts/capture_dataset.py --seconds 180 --every 1.0
```

Las imagenes quedan en:

```text
data/raw
```

## Etiquetado

Puedes usar LabelImg, Roboflow, CVAT o makesense.ai. Exporta en formato YOLO.

La estructura final debe quedar asi:

```text
data/images/train
data/images/val
data/labels/train
data/labels/val
```

Cada archivo `.txt` debe tener el mismo nombre que la imagen:

```text
data/images/train/foto_001.jpg
data/labels/train/foto_001.txt
```

Formato de cada linea:

```text
0 x_centro y_centro ancho alto
```

Los valores son proporciones entre 0 y 1.

## Entrenamiento

```powershell
python scripts/train_yolo.py --epochs 80 --imgsz 640 --model yolo11n.pt
```

Cuando termine, copia el mejor modelo:

```text
runs/detect/toy_car_detector/weights/best.pt
```

a:

```text
models/toy_car_best.pt
```

Al reiniciar el dashboard, el sistema usara ese modelo personalizado.

## Como saber si falta mas dataset

Agrega mas imagenes si pasa algo de esto:

- Detecta el empaque completo en vez del carrito.
- Confunde letras, ruedas o dibujos con carros.
- Solo detecta carritos de un color.
- Falla cuando hay reflejo en el plastico.
- Falla cuando el carrito esta pequeno o lejos.

La mejora normal es iterativa: capturar, etiquetar, entrenar, probar, corregir falsos positivos y volver a entrenar.

## Descargar YOLO base

Si la pagina dice `IA pendiente` o `modelo pendiente`, descarga primero el modelo base:

```powershell
python scripts/download_model.py --model yolo11n.pt
```

Tambien puedes hacer doble clic en:

```text
DESCARGAR_YOLO_BASE.bat
```
