import pytest
from tiktok.models import Client
from test_fixtures import user, user_2, unauth_client, auth_client_no_tiktok_account, auth_client

@pytest.mark.django_db
def test_client_login(unauth_client):
    response = unauth_client.post("/api-token-auth/", {"username": "test", "password": "test"}, format="json")
    assert response.status_code == 200

@pytest.mark.django_db
def test_client_get_tiktok_account(auth_client):
    response = auth_client.get("/api/client/")
    assert response.status_code == 200
    assert response.data == {
        "tiktok_account": "cheekyglo"
    }

@pytest.mark.django_db
def test_client_create(auth_client_no_tiktok_account):
    response = auth_client_no_tiktok_account.post("/api/client/", {"tiktok_account": "therock"}, format="json")
    assert response.status_code == 200
    assert Client.objects.get(tiktok_account="therock").user.username == "test_2"

@pytest.mark.django_db
def test_client_update(auth_client):
    response = auth_client.put("/api/client/", {"tiktok_account": "therock"}, format="json")
    assert response.status_code == 200
    assert Client.objects.get(tiktok_account="therock").user.username == "test"