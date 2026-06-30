def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_review(client):
    response = client.post(
        "/api/v1/reviews",
        json={
            "language": "python",
            "code": "def divide(a, b):\n    return a / b",
            "review_type": "code_snippet",
            "focus": ["bug", "edge_case", "exception", "test"],
            "generate_test_code": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["review_id"] == 1
    assert body["review_result"] == "HIGH_RISK"


def test_empty_code_returns_422(client):
    response = client.post("/api/v1/reviews", json={"language": "python", "code": ""})
    assert response.status_code == 422


def test_list_and_get_review(client):
    created = client.post("/api/v1/reviews", json={"language": "python", "code": "def ok():\n    return 1"}).json()
    list_response = client.get("/api/v1/reviews")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    detail_response = client.get(f"/api/v1/reviews/{created['review_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["review_id"] == created["review_id"]
