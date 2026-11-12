
from unittest.mock import patch
from types import SimpleNamespace

import pytest

from src.detection import VehicleDetector


class FakeYOLO:
    names = {
        0: "bus",
        1: "car",
        2: "motorbike",
        3: "truck"
    }

    def predict(self, **kwargs):
        fake_box = SimpleNamespace(
            cls=[1],
            conf=[0.91],
            xyxy=[
                SimpleNamespace(
                    tolist=lambda: [10.0, 20.0, 100.0, 120.0]
                )
            ]
        )

        return [
            SimpleNamespace(boxes=[fake_box])
        ]


def create_fake_model(tmp_path):
    model_file = tmp_path / "fake_model.pt"
    model_file.write_bytes(b"fake weights")
    return model_file


def test_detect_image_returns_vehicle_information(tmp_path):
    image = tmp_path / "test.jpg"
    image.write_bytes(b"fake image")
    model_file = create_fake_model(tmp_path)

    with patch("src.detection.YOLO", return_value=FakeYOLO()):
        detector = VehicleDetector(model_path=model_file)
        detections = detector.detect_image(image)

    assert len(detections) == 1
    assert detections[0]["class"] == "car"
    assert detections[0]["confidence"] == 0.91
    assert detections[0]["bbox"] == [10.0, 20.0, 100.0, 120.0]


def test_detect_image_raises_error_for_missing_image(tmp_path):
    model_file = create_fake_model(tmp_path)

    with patch("src.detection.YOLO", return_value=FakeYOLO()):
        detector = VehicleDetector(model_path=model_file)

    with pytest.raises(FileNotFoundError):
        detector.detect_image(tmp_path / "image_inexistante.jpg")
