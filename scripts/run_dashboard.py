from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.esp32_yolo.settings import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicia el dashboard web del proyecto.")
    parser.add_argument("--reload", action="store_true", help="Recarga automatica para desarrollo.")
    args = parser.parse_args()

    settings = load_settings()
    uvicorn.run("src.esp32_yolo.api:app", host=settings.api.host, port=settings.api.port, reload=args.reload)


if __name__ == "__main__":
    main()
