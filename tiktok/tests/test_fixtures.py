import pytest
from django.contrib.auth.models import User
from tiktok.models import Client, Tiktok, WeeklyReport
from rest_framework.test import APIClient
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def user():
    yield User.objects.create_user(username='test', password='test')

@pytest.fixture
def user_2():
    yield User.objects.create_user(username='test_2', password='test_2')

@pytest.fixture
def unauth_client(user):
    api_client = APIClient()
    yield api_client

@pytest.fixture
def auth_client_no_tiktok_account(user_2):
    api_client = APIClient()
    api_client.force_authenticate(user=user_2)
    yield api_client

@pytest.fixture
def auth_client(user):
    client = Client.objects.create(user=user, tiktok_account="cheekyglo")

    api_client = APIClient()
    api_client.force_authenticate(user=user)
    yield api_client

@pytest.fixture
def weekly_report(user):
    yield WeeklyReport.objects.create(
        title="Test Report",
        owner=user,
        notes="",
        platform="tiktok"
    )

@pytest.fixture
def tiktok(weekly_report):
    yield Tiktok.objects.create(
        weekly_report_id=weekly_report.id,
        thumbnail="",
        like_count=1,
        comment_count=1,
        view_count=1,
        favourite_count=1,
        share_count=1,
        improvement_like_count=0,
        improvement_comment_count=0,
        improvement_view_count=0,
        improvement_favourite_count=0,
        hook="",
        notes="",
        url="https://m.tiktok.com/@cheekyglo/video/7219255008934563074",
        created=datetime.datetime.now(),
        order=0
    )

@pytest.fixture
def tiktok_2(weekly_report):
    yield Tiktok.objects.create(
        weekly_report_id=weekly_report.id,
        thumbnail="",
        like_count=1,
        comment_count=1,
        view_count=1,
        favourite_count=1,
        share_count=1,
        improvement_like_count=0,
        improvement_comment_count=0,
        improvement_view_count=0,
        improvement_favourite_count=0,
        hook="",
        notes="",
        url="https://m.tiktok.com/@cheekyglo/video/7219255008934563074",
        created=datetime.datetime.now(),
        order=1
    )

@pytest.fixture
def thumbnail():
    content = b'Fake picture content'
    return SimpleUploadedFile("fake_picture.jpg", content, content_type="image/jpeg")