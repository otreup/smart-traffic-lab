# Mapa mental del diseño del programa

Este mapa mental explica como esta organizado el proyecto de semaforos inteligentes con ESP32-CAM, YOLO, dashboard web y simulacion.

```mermaid
mindmap
  root((Smart Traffic Lab))
    Objetivo
      Detectar carritos de juguete
      Simular trafico
      Apoyar semaforos inteligentes
      Mostrar todo en una pagina web
    Entrada
      ESP32-CAM
        URL http://192.168.1.44
        Captura imagenes
        Transmite video
      Dataset
        Fotos de carritos
        Varias luces
        Varios angulos
        Varios fondos
    Inteligencia Artificial
      YOLO
        Modelo base yolo11n.pt
        Modelo entrenado toy_car_best.pt
      Entrenamiento
        Capturar fotos
        Etiquetar cajas
        Separar train y val
        Entrenar
        Probar
    Backend
      FastAPI
        Entrega la pagina web
        Lee la camara
        Ejecuta detecciones
        Devuelve resultados
      Endpoints
        /health
        /snapshot
        /detect/live
        /api/status
        /api/network
    Frontend
      Dashboard web
        Ver camara
        Ver detecciones
        Ver simulacion
        Ver decision del semaforo
      Archivos
        index.html
        app.js
        styles.css
    Simulacion
      SUMO
        Red vial
        Carretera
        Intersecciones
      Simulacion interna
        Vehiculos falsos
        Conteo por carril
        Flujo de prueba
    Semaforo inteligente
      Conteo de carros
      Calculo de demanda
      Eleccion de via con mas carros
      Tiempo verde dinamico
    Carpetas importantes
      configs
        settings.yaml
        traffic_lights.yaml
        toy_car_dataset.yaml
      src
        camera.py
        detector.py
        api.py
        traffic_controller.py
      scripts
        check_camera.py
        capture_dataset.py
        train_yolo.py
        run_dashboard.py
      data
        raw
        images
        labels
      models
        toy_car_best.pt
      web
        dashboard
```

## Explicacion sencilla

El proyecto funciona como un cuerpo:

- La **ESP32-CAM** son los ojos.
- **YOLO** es el cerebro que reconoce los carritos.
- **FastAPI** es el mensajero que conecta la camara, la IA y la pagina web.
- El **dashboard web** es la pantalla donde vemos lo que esta pasando.
- **SUMO** es una ciudad simulada para probar trafico y semaforos.
- El **controlador de semaforo** decide que via debe tener mas tiempo en verde.

## Flujo principal

```mermaid
flowchart LR
    A[ESP32-CAM] --> B[Imagen o video]
    B --> C[YOLO]
    C --> D[Deteccion toy_car]
    D --> E[Conteo de carros]
    E --> F[Decision del semaforo]
    F --> G[Dashboard web]
    H[SUMO] --> G
```

## Flujo para entrenar la IA

```mermaid
flowchart TD
    A[Tomar fotos de carritos] --> B[Guardar en data/raw]
    B --> C[Etiquetar cada carrito]
    C --> D[Organizar train y val]
    D --> E[Entrenar YOLO]
    E --> F[Obtener best.pt]
    F --> G[Guardar como models/toy_car_best.pt]
    G --> H[Probar con la ESP32-CAM]
```

