from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import TiktokSerializer, WeeklyReportSerializer
from .models import Tiktok, WeeklyReport
from django.db.models import Q

from tiktokapipy.async_api import AsyncTikTokAPI
from tiktokapipy.models.video import video_link
from asgiref.sync import async_to_sync, sync_to_async

from datetime import datetime
from imgurpython import ImgurClient
from decouple import config

client_id = config("IMGUR_CLIENT_ID")
client_secret = config("IMGUR_CLIENT_SECRET")

client = ImgurClient(client_id, client_secret)

async def get_videos(serializer_instance, n):
    async with AsyncTikTokAPI(navigation_retries=5) as api:
        user_tag = "cheekyglo"
        user = await api.user(user_tag, video_limit=n)
        counter = 0
        async for video in user.videos:
            if n - counter > 7:
                counter += 1
                continue
            create_tiktok = sync_to_async(Tiktok.objects.create)
            get_video_url = sync_to_async(client.upload_from_url)
            uploaded_image = await get_video_url(video.video.cover, config=None, anon=True)
            tiktok = await create_tiktok(
                weekly_report_id=serializer_instance.id,
                thumbnail=uploaded_image['link'],
                like_count=video.stats.digg_count,
                comment_count=video.stats.comment_count,
                view_count=video.stats.play_count,
                favourite_count=video.stats.collect_count,
                improvement_like_count=0,
                improvement_comment_count=0,
                improvement_view_count=0,
                improvement_favourite_count=0,
                notes="",
                url=video_link(video.id),
                created=video.create_time.strftime("%Y-%m-%d")
            )
            await sync_to_async(tiktok.save)()
        return serializer_instance

async def get_video_by_url(video_url):
    async with AsyncTikTokAPI(navigation_retries=5) as api:
        video = await api.video(video_url)  

        return video

class UserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"success": True}, status=status.HTTP_200_OK)
        
    
class TiktokApiView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, tiktok_id):
        tiktok = Tiktok.objects.get(id=tiktok_id)
        data = {
            "notes": request.data.get("notes")
        }
        serializer = TiktokSerializer(instance=tiktok, data=data, partial=True)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)

class TiktokListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tiktoks = Tiktok.objects.all()
        serializer = TiktokSerializer(tiktoks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = {
            "weekly_report": request.data.get("weekly_report"),
            "thumbnail": request.data.get("thumbnail"),
            "like_count": request.data.get("like_count"),
            "view_count": request.data.get("view_count"),
            "comment_count": request.data.get("comment_count"),
            "notes": request.data.get("notes"),
            "created": request.data.get("created")
        }
        serializer = TiktokSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        for tiktok_url in request.data.get("urls"):
            tiktok = Tiktok.objects.get(url=tiktok_url)
            video = async_to_sync(get_video_by_url)(tiktok_url)
            data = {
                "like_count": video.stats.digg_count,
                "comment_count": video.stats.comment_count,
                "view_count": video.stats.play_count,
                "favourite_count": video.stats.collect_count,
                "improvement_like_count": tiktok.improvement_like_count + (video.stats.digg_count - tiktok.like_count),
                "improvement_comment_count": tiktok.improvement_comment_count + (video.stats.comment_count - tiktok.comment_count),
                "improvement_view_count": tiktok.improvement_view_count + (video.stats.play_count - tiktok.view_count),
                "improvement_favourite_count": tiktok.improvement_favourite_count + (video.stats.collect_count - tiktok.favourite_count),
                "last_updated": datetime.today().strftime('%Y-%m-%d')
            }

            serializer = TiktokSerializer(instance=tiktok, data=data, partial=True)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)

class WeeklyReportApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, weekly_report_id):
        tiktoks = Tiktok.objects.filter(weekly_report=weekly_report_id)
        serializer = TiktokSerializer(tiktoks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeeklyReportListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        weekly_reports = WeeklyReport.objects.filter(owner=request.user.id)
        serializer = WeeklyReportSerializer(weekly_reports, many=True)
        for report in serializer.data:  
            report["total_likes"] = 0
            report["total_views"] = 0
            report["total_comments"] = 0
            report["total_favourites"] = 0
            report["total_improvement_likes"] = 0
            report["total_improvement_views"] = 0
            report["total_improvement_comments"] = 0
            report["total_improvement_favourites"] = 0
            report["last_updated"] = ""
            tiktoks = Tiktok.objects.filter(weekly_report=report["id"])

            for tiktok in tiktoks:
                report["total_likes"] += tiktok.like_count
                report["total_views"] += tiktok.view_count
                report["total_comments"] += tiktok.comment_count
                report["total_favourites"] += tiktok.favourite_count
                report["total_improvement_likes"] += tiktok.improvement_like_count
                report["total_improvement_views"] += tiktok.improvement_view_count
                report["total_improvement_comments"] += tiktok.improvement_comment_count
                report["total_improvement_favourites"] += tiktok.improvement_favourite_count
                if (tiktok.last_updated != None):
                    report["last_updated"] = tiktok.last_updated
  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = {
            "owner": request.user.id,
            "title": request.data.get("title"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date")
        }
        if Tiktok.objects.filter(created__gte=data["start_date"], created__lte=data["end_date"]).exists():
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WeeklyReportSerializer(data=data)
        if serializer.is_valid():
            serializer_instance = serializer.save()
            get_videos_sync = async_to_sync(get_videos)

            date_format = "%Y-%m-%d"
            a = datetime.strptime(data["start_date"], date_format)
            b = datetime.strptime(data["end_date"], date_format)
            c = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), date_format)
            delta_1 = b - a
            delta_2 = c - b

            serializer_instance = get_videos_sync(serializer_instance, delta_1.days + delta_2.days)
            return_data = {
                "title": serializer_instance.title,
                "start_date": serializer_instance.start_date,
                "end_date": serializer_instance.end_date
            }
            serializer_instance.save()

        
            return Response(return_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        for weekly_report_id in request.data.get("ids"):
            weekly_report = WeeklyReport.objects.get(id = weekly_report_id, owner=request.user.id)
            weekly_report.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
