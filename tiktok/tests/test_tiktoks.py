import pytest
from tiktok.models import Tiktok, WeeklyReport
from test_fixtures import user, auth_client, weekly_report, tiktok, tiktok_2, thumbnail

@pytest.mark.django_db
def test_tiktoks_get(auth_client, weekly_report, tiktok):
    response = auth_client.get("/api/tiktoks/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_tiktoks_create(auth_client, weekly_report, thumbnail):
    response = auth_client.post("/api/tiktoks/", {
        "weekly_report": weekly_report.id,
        "like_count": 2,
        "comment_count": 2,
        "favourite_count": 2,
        "view_count": 2,
        "share_count": 2,
        "url": "https://www.tiktok.com/@cheekyglo/video/7219255008934563074?lang=en",
        "thumbnail": thumbnail
    })
    assert response.status_code == 200
    assert len(Tiktok.objects.all()) == 1

@pytest.mark.django_db
def test_tiktoks_bulk_refresh(auth_client, tiktok):
    response = auth_client.put("/api/tiktoks/", {"urls": ["https://m.tiktok.com/@cheekyglo/video/7219255008934563074"]}, format="json")
    assert response.status_code == 200
    assert Tiktok.objects.get(id=tiktok.id).like_count > 1

@pytest.mark.django_db
def test_tiktok_update_notes(auth_client, tiktok):
    response = auth_client.put(f"/api/tiktoks/{tiktok.id}", {"notes": "notes"}, format="json")
    assert response.status_code == 200
    assert Tiktok.objects.get(id=tiktok.id).notes == "notes"

    response = auth_client.put(f"/api/tiktoks/{tiktok.id}", {"hook": "hook"}, format="json")
    assert response.status_code == 200
    assert Tiktok.objects.get(id=tiktok.id).hook == "hook"

    response = auth_client.put(f"/api/tiktoks/{tiktok.id}", {"improvements": "improvements"}, format="json")
    assert response.status_code == 200
    assert Tiktok.objects.get(id=tiktok.id).improvements == "improvements"

@pytest.mark.django_db
def test_tiktok_update_order(auth_client, tiktok, tiktok_2):
    response = auth_client.put(f"/api/tiktoks/{tiktok.id}", {"order": 1}, format="json")
    assert response.status_code == 200
    assert Tiktok.objects.get(id=tiktok.id).order == 1
    assert Tiktok.objects.get(id=tiktok_2.id).order == 0

@pytest.mark.django_db
def test_tiktok_delete(auth_client, tiktok):
    response = auth_client.delete(f"/api/tiktoks/{tiktok.id}")
    assert response.status_code == 200
    assert len(Tiktok.objects.all()) == 0
