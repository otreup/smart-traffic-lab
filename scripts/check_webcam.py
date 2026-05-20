from __future__ import annotations

import argparse

import cv2


def main() -> None:
    parser = argparse.ArgumentParser(description="Prueba la camara web del computador.")
    parser.add_argument("--index", type=int, default=0, help="Indice de la webcam. Normalmente 0.")
    args = parser.parse_args()

    capture = None
    for name, backend in [("directshow", cv2.CAP_DSHOW), ("mediafoundation", cv2.CAP_MSMF), ("default", cv2.CAP_ANY)]:
        print(f"Probando webcam {args.index} con {name}...")
        candidate = cv2.VideoCapture(args.index, backend)
        if candidate.isOpened():
            capture = candidate
            print(f"Webcam abierta con {name}.")
            break
        candidate.release()

    if capture is None:
        capture = cv2.VideoCapture(-1)
    if not capture.isOpened():
        raise RuntimeError(f"No pude abrir la webcam con indice {args.index}.")

    print("Webcam activa. Presiona q para salir.")
    try:
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("No llego frame de la webcam.")
                continue
            cv2.imshow("Webcam computador", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
