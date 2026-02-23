import os, sys
import pytest
from datetime import datetime, timedelta

# ensure app package is importable during tests (add backend directory to path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import calendar

class DummyClient:
    def __init__(self, response):
        self._resp = response
        self.called = []
    def post(self, url, json=None):
        self.called.append((url, json))
        class R:
            def __init__(self, data):
                self._data = data
            def raise_for_status(self):
                pass
            def json(self):
                return self._data
        return R(self._resp)

@pytest.mark.asyncio
async def test_check_availability_free():
    # simulate free schedule
    resp = {"value":[{"scheduleItems":[{"status":"free"}]}]}
    client = DummyClient(resp)
    start = datetime.utcnow() + timedelta(days=30)
    ok = await calendar.check_availability(client, start, "12:00")
    assert ok

@pytest.mark.asyncio
async def test_check_availability_busy():
    resp = {"value":[{"scheduleItems":[{"status":"busy"}]}]}
    client = DummyClient(resp)
    start = datetime.utcnow() + timedelta(days=30)
    ok = await calendar.check_availability(client, start, "12:00")
    assert not ok

# further tests for create_event and send_confirmation could be done by inspecting the payloads
