# Camaras del proyecto

El proyecto puede usar dos camaras:

1. **ESP32-CAM** en `http://192.168.1.44`
2. **Webcam del computador** con indice `0`

## Modo recomendado

El modo recomendado es:

```text
auto
```

En este modo el programa intenta primero la ESP32-CAM. Si no responde, usa la webcam del computador.

## Cambiar modo facilmente

Usa estos archivos:

- `CAMARA_AUTO.bat`: ESP32 primero, webcam como respaldo.
- `CAMARA_ESP32.bat`: solo ESP32-CAM.
- `CAMARA_WEBCAM.bat`: solo webcam del computador.

Tambien puedes hacerlo por terminal:

```powershell
python scripts/set_camera_source.py auto
python scripts/set_camera_source.py esp32
python scripts/set_camera_source.py webcam --webcam-index 0
```

## Probar camaras

ESP32-CAM:

```powershell
python scripts/check_camera.py
```

Webcam:

```powershell
python scripts/check_webcam.py
```

## Configuracion

La configuracion vive en:

```text
configs/settings.yaml
```

Campos importantes:

```yaml
camera_source: auto
camera_url: "http://192.168.1.44"
use_webcam_fallback: true
webcam_index: 0
```

