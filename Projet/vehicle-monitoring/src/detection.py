
from pathlib import Path
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"


class VehicleDetector:
    """Détecte les véhicules avec le modèle YOLO entraîné."""

    def __init__(self, model_path=MODEL_PATH):
        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Modèle introuvable : {model_path}"
            )

        self.model = YOLO(str(model_path))

    def detect_image(self, image_path, confidence=0.25):
        """Retourne les détections d'une image."""

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image introuvable : {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=confidence,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                score = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    "class": class_name,
                    "confidence": round(score, 3),
                    "bbox": [
                        round(x1, 2),
                        round(y1, 2),
                        round(x2, 2),
                        round(y2, 2)
                    ]
                })

        return detections

    def detect_video(self, video_path, confidence=0.25):
        """Lance la détection sur une vidéo et sauvegarde le résultat."""

        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(
                f"Vidéo introuvable : {video_path}"
            )

        return self.model.predict(
            source=str(video_path),
            conf=confidence,
            save=True,
            verbose=True
        )
