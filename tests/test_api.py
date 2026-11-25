"""REST API scenarios against JSONPlaceholder: CRUD operations, filtering and negative cases."""

import allure
import pytest
from playwright.sync_api import APIRequestContext

pytestmark = [allure.feature("REST API"), pytest.mark.api]

POST_SCHEMA = {"userId": int, "id": int, "title": str, "body": str}


def _assert_matches_schema(resource: dict, schema: dict[str, type]) -> None:
    for field, expected_type in schema.items():
        assert field in resource, f"Missing field '{field}'"
        assert isinstance(resource[field], expected_type), (
            f"Field '{field}' should be {expected_type.__name__}, got {type(resource[field]).__name__}"
        )


@pytest.mark.smoke
@allure.story("Read resource")
def test_get_post_by_id_returns_expected_resource(api_context: APIRequestContext) -> None:
    response = api_context.get("/posts/1")
    assert response.status == 200
    assert "application/json" in response.headers["content-type"]
    payload = response.json()
    _assert_matches_schema(payload, POST_SCHEMA)
    assert payload["id"] == 1
    assert payload["title"]


@allure.story("Read resource")
def test_get_nonexistent_post_returns_404(api_context: APIRequestContext) -> None:
    response = api_context.get("/posts/999999")
    assert response.status == 404
    assert response.json() == {}


@allure.story("Filter collection")
def test_filter_posts_by_user(api_context: APIRequestContext) -> None:
    response = api_context.get("/posts", params={"userId": 1})
    assert response.ok
    posts = response.json()
    assert posts, "Expected at least one post for userId=1"
    assert all(post["userId"] == 1 for post in posts)
    for post in posts:
        _assert_matches_schema(post, POST_SCHEMA)


@allure.story("Create resource")
def test_create_post_returns_created_resource(api_context: APIRequestContext) -> None:
    payload = {"title": "Playwright API test", "body": "Created by automated test", "userId": 1}
    response = api_context.post("/posts", data=payload)
    assert response.status == 201
    created = response.json()
    assert {key: created[key] for key in payload} == payload
    assert isinstance(created["id"], int)


@allure.story("Update resource")
def test_update_post_with_put(api_context: APIRequestContext) -> None:
    payload = {"id": 1, "title": "Updated title", "body": "Updated body", "userId": 1}
    response = api_context.put("/posts/1", data=payload)
    assert response.status == 200
    assert response.json() == payload


@allure.story("Update resource")
def test_partial_update_post_with_patch(api_context: APIRequestContext) -> None:
    response = api_context.patch("/posts/1", data={"title": "Patched title"})
    assert response.status == 200
    updated = response.json()
    assert updated["title"] == "Patched title"
    assert updated["id"] == 1, "Fields not included in the PATCH body should be preserved"


@allure.story("Delete resource")
def test_delete_post(api_context: APIRequestContext) -> None:
    response = api_context.delete("/posts/1")
    assert response.status == 200
