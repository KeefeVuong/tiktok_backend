import pytest
from tiktok.models import Client, Tiktok, WeeklyReport
from test_fixtures import user, auth_client, weekly_report, tiktok

@pytest.mark.django_db
def test_weekly_report_get_associated_tiktoks(user, auth_client, weekly_report, tiktok):
    response = auth_client.get(f"/api/weekly-reports/{weekly_report.id}")
    assert response.status_code == 200
    assert response.data["weekly_report"] == {
        'id': f"{weekly_report.id}",
        'owner': user.id, 
        'title': 'Test Report', 
        'notes': "",
    }
    assert len(response.data["tiktok"]) == 1

@pytest.mark.django_db
def test_weekly_report_update(auth_client, weekly_report):
    response = auth_client.put(f"/api/weekly-reports/{weekly_report.id}", {"notes": "notes", "title": "new title"}, format="json")
    assert response.status_code == 200

    new_weekly_report = WeeklyReport.objects.get(id=weekly_report.id)
    assert new_weekly_report.notes == "notes"
    assert new_weekly_report.title == "new title"

@pytest.mark.django_db
def test_weekly_reports_get(auth_client, weekly_report):
    response = auth_client.get("/api/weekly-reports/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_weekly_reports_create(auth_client):
    response = auth_client.post("/api/weekly-reports/", {"title": "Test Report 2", "number_of_videos": 2}, format="json")
    assert response.status_code == 200
    assert response.data["title"] == "Test Report 2"

    assert len(WeeklyReport.objects.all()) == 1

    new_weekly_report = WeeklyReport.objects.get(title="Test Report 2")
    assert len(Tiktok.objects.filter(weekly_report_id=new_weekly_report.id)) == 2

@pytest.mark.django_db
def test_weekly_reports_delete(auth_client, weekly_report):
    response = auth_client.delete("/api/weekly-reports/", {"ids": [weekly_report.id]}, format="json")
    assert response.status_code == 200
    assert len(WeeklyReport.objects.all()) == 0