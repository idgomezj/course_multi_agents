from __future__ import annotations

import threading
import time

import torch
from torch import nn

from challenge.model_registry import StudentModelRegistry


class _FakeModule(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x.sum(dim=1, keepdim=True)


class _FakeExportedProgram:
    def module(self) -> nn.Module:
        return _FakeModule()


def test_torch_export_deserialization_is_process_serialized(tmp_path, monkeypatch):
    (tmp_path / "model_a.pt2").write_bytes(b"a")
    (tmp_path / "model_b.pt2").write_bytes(b"b")

    spec = {
        "models": {
            "model_a": {
                "artifact": "model_a.pt2",
                "task": "test_a",
                "features": ["x"],
            },
            "model_b": {
                "artifact": "model_b.pt2",
                "task": "test_b",
                "features": ["x"],
            },
        }
    }

    active = 0
    maximum_active = 0
    counter_lock = threading.Lock()
    start = threading.Barrier(2)

    def fake_load(_path):
        nonlocal active, maximum_active
        with counter_lock:
            active += 1
            maximum_active = max(maximum_active, active)
        time.sleep(0.05)
        with counter_lock:
            active -= 1
        return _FakeExportedProgram()

    monkeypatch.setattr(torch.export, "load", fake_load)

    registry_a = StudentModelRegistry(tmp_path, spec)
    registry_b = StudentModelRegistry(tmp_path, spec)
    errors: list[BaseException] = []

    def worker(registry, key, value):
        try:
            start.wait(timeout=2)
            assert registry.predict(key, {"x": value}) == [value]
        except BaseException as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=worker, args=(registry_a, "model_a", 1.0)),
        threading.Thread(target=worker, args=(registry_b, "model_b", 2.0)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert not errors
    assert maximum_active == 1
