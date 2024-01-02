"""
Test module intended to validate ASGI servers implementations work as expected
"""
import httpx


def test_middleware_works_as_expected(asgi_server):
    _, num_middlewares, container, _ = asgi_server
    print(container)

    response = httpx.get(f"http://{container.network_settings.ip_address}/_ping", timeout=5)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json() == {
        "count": num_middlewares,
    }
