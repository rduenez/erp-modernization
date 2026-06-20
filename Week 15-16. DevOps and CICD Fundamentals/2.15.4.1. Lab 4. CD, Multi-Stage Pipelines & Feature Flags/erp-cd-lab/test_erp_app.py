import importlib
import os

import pytest


def reload_erp_app(monkeypatch, flag_value):
    if flag_value is None:
        monkeypatch.delenv("ENABLE_NEW_PAYMENT_GATEWAY", raising=False)
    else:
        monkeypatch.setenv("ENABLE_NEW_PAYMENT_GATEWAY", flag_value)

    import erp_app
    return importlib.reload(erp_app)


def test_health_endpoint_returns_healthy():
    erp_app = reload_erp_app(pytest.MonkeyPatch(), None)
    client = erp_app.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "healthy"}


def test_checkout_uses_legacy_gateway_when_flag_not_enabled():
    erp_app = reload_erp_app(pytest.MonkeyPatch(), "false")
    client = erp_app.app.test_client()

    response = client.post("/api/checkout")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"message": "Payment processed using the legacy V1 Gateway."}


def test_checkout_uses_new_gateway_when_flag_enabled():
    erp_app = reload_erp_app(pytest.MonkeyPatch(), "true")
    client = erp_app.app.test_client()

    response = client.post("/api/checkout")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"message": "Payment processed using the NEW V2 Gateway!"}
