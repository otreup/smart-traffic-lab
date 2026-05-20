from __future__ import annotations

import argparse
from pathlib import Path
import random
import shutil


def main() -> None:
    parser = argparse.ArgumentParser(description="Divide imagenes y labels YOLO en train/val.")
    parser.add_argument("--images", type=Path, default=Path("data/raw"))
    parser.add_argument("--labels", type=Path, default=Path("data/raw_labels"))
    parser.add_argument("--val-ratio", type=float, default=0.2)
    args = parser.parse_args()

    image_paths = sorted([p for p in args.images.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    if not image_paths:
        raise RuntimeError(f"No encontre imagenes en {args.images}")

    random.seed(42)
    random.shuffle(image_paths)
    val_count = max(1, int(len(image_paths) * args.val_ratio))
    val_set = set(image_paths[:val_count])

    for split in ["train", "val"]:
        Path(f"data/images/{split}").mkdir(parents=True, exist_ok=True)
        Path(f"data/labels/{split}").mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:
        split = "val" if image_path in val_set else "train"
        label_path = args.labels / f"{image_path.stem}.txt"
        shutil.copy2(image_path, Path(f"data/images/{split}") / image_path.name)
        if label_path.exists():
            shutil.copy2(label_path, Path(f"data/labels/{split}") / label_path.name)
        else:
            print(f"Aviso: falta label para {image_path.name}")

    print(f"Dataset dividido. Train: {len(image_paths) - val_count}, Val: {val_count}")


if __name__ == "__main__":
    main()
