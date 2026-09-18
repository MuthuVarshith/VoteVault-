"""Smoke tests for VoteVault's pages. They only read the database, never write to it."""
import pytest

from app import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.parametrize("path", ["/", "/login", "/register", "/results"])
def test_public_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_export_votes_requires_admin(client):
    response = client.get("/export_votes")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_candidate_requires_admin(client):
    response = client.get("/add_candidate")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
