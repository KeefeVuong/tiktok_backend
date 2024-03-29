from datetime import datetime
import json
import os
import shutil
import requests

from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.conf import settings

from TikTokApi import TikTokApi
from imgurpython import ImgurClient
from tiktokapipy.async_api import AsyncTikTokAPI
from tiktokapipy.models.video import video_link

from .models import Tiktok, WeeklyReport, Client
from .serializers import TiktokSerializer, WeeklyReportSerializer, ClientSerializer
from .permissions import IsGuestUser


STATIC_FOLDER_PATH = settings.STATIC_ROOT

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

# client_id = config["IMGUR_CLIENT_ID"]
# client_secret = config["IMGUR_CLIENT_SECRET"]

# imgur_client = ImgurClient(client_id, client_secret)

async def get_async_enumerate(async_gen):
    idx = 0
    async for item in async_gen:
        yield idx, item
        idx += 1

def get_data(data, val, key):
    if val != None:
        data[key] = val

def calculate_improvement(improvement_count, curr_count, prev_count):
    return improvement_count + (curr_count - prev_count)

def save_thumbnail(serializer_instance, video_id, thumbnail):
    if config["DEBUG"]:
        return ""

    owner = serializer_instance.owner
    weekly_report_id = serializer_instance.id

    if not os.path.exists(f"{STATIC_FOLDER_PATH}/{owner}"):
        os.makedirs(f"{STATIC_FOLDER_PATH}/{owner}")

    if not os.path.exists(f"{STATIC_FOLDER_PATH}/{owner}/{weekly_report_id}"):
        os.makedirs(f"{STATIC_FOLDER_PATH}/{owner}/{weekly_report_id}")

    with open(f"{STATIC_FOLDER_PATH}/{owner}/{weekly_report_id}/{video_id}.png", "wb") as handler:
        handler.write(thumbnail)

    return f"https://keefe-tk-be.xyz/static/{owner}/{weekly_report_id}/{video_id}.png"

async def get_videos(serializer_instance, n, user_tag):
    async with TikTokApi() as api:
        await api.create_sessions(num_sessions=1, sleep_after=3)
        user = api.user(user_tag)

        async for idx, video in get_async_enumerate(user.videos(count=n)):
            create_tiktok = sync_to_async(Tiktok.objects.create)
#           get_video_url = sync_to_async(imgur_client.upload_from_url)
#           uploaded_image = await get_video_url(video.as_dict["video"]["cover"], config=None, anon=True)

            tiktok = await create_tiktok(
                weekly_report_id=serializer_instance.id,
		        thumbnail="",
                like_count=video.stats["diggCount"],
                comment_count=video.stats["commentCount"],
                view_count=video.stats["playCount"],
                favourite_count=video.stats["collectCount"],
                share_count=video.stats["shareCount"],
                improvement_like_count=0,
                improvement_comment_count=0,
                improvement_view_count=0,
                improvement_favourite_count=0,
                hook="",
                notes="",
                url=video_link(video.id),
                created=video.create_time.strftime("%Y-%m-%d"),
                order=idx
            )

            tiktok.thumbnail = save_thumbnail(serializer_instance, tiktok.id, requests.get(video.as_dict["video"]["cover"]).content)

            await sync_to_async(tiktok.save)()
        return serializer_instance


# async def get_videos(serializer_instance, n, user_tag):
#     async with AsyncTikTokAPI(navigation_retries=5, navigation_timeout=30, headless=False) as api:
#         user = await api.user(user_tag, video_limit=n)

#         async for idx, video in get_async_enumerate(user.videos):
#             create_tiktok = sync_to_async(Tiktok.objects.create)

#             tiktok = await create_tiktok(
#                 weekly_report_id=serializer_instance.id,
#                 thumbnail="",
#                 like_count=video.stats.digg_count,
#                 comment_count=video.stats.comment_count,
#                 view_count=video.stats.play_count,
#                 favourite_count=video.stats.collect_count,
#                 share_count=video.stats.share_count,
#                 improvement_like_count=0,
#                 improvement_comment_count=0,
#                 improvement_view_count=0,
#                 improvement_favourite_count=0,
#                 hook="",
#                 notes="",
#                 url=video_link(video.id),
#                 created=video.create_time.strftime("%Y-%m-%d"),
#                 order=idx
#             )

#             tiktok.thumbnail = save_thumbnail(
#                 serializer_instance, 
#                 tiktok.id, 
#                 requests.get(video.video.cover).content
#             )
            
#             await sync_to_async(tiktok.save)()
#         return serializer_instance

async def get_video_by_url(video_url):   
    async with AsyncTikTokAPI(navigation_retries=5, navigation_timeout=30) as api:
        video = None
        try:
            video = await api.video(video_url)  
        except:
            pass

        return video

class ClientAPI(APIView):
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        client = Client.objects.get(user=request.user)
        return Response({"tiktok_account": client.tiktok_account}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = {
            "user": request.user.id,
            "tiktok_account": request.data.get("tiktok_account")
        }

        serializer = ClientSerializer(data=data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

    def put(self, request):
        client = Client.objects.get(user=request.user)
        data = {
            "tiktok_account": request.data.get("tiktok_account")
        }

        serializer = ClientSerializer(instance=client, data=data, partial=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

    
class TiktokAPI(APIView):
    permission_classes = [IsAuthenticated, IsGuestUser]

    def put(self, request, tiktok_id):
        tiktok = Tiktok.objects.get(id=tiktok_id)

        data = {}
        get_data(data, request.data.get("notes"), "notes")
        get_data(data, request.data.get("hook"), "hook")
        get_data(data, request.data.get("improvements"), "improvements")
        get_data(data, request.data.get("other_platform_notes"), "other_platform_notes")

        if request.data.get("order") != None:
            og_order = tiktok.order
            tiktok_2 = Tiktok.objects.get(weekly_report=tiktok.weekly_report_id, order=request.data.get("order"))

            tiktok.order = tiktok_2.order
            tiktok_2.order = og_order
            tiktok_2.save()

        serializer = TiktokSerializer(instance=tiktok, data=data, partial=True)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"success": True}, status=status.HTTP_200_OK)
    
    def delete(self, request, tiktok_id):
        tiktok = Tiktok.objects.get(id=tiktok_id)

        thumbnail_path = f"{STATIC_FOLDER_PATH}/{request.user}/{tiktok.weekly_report.id}/{tiktok_id}.png"

        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

        weekly_report_id = tiktok.weekly_report_id
        tiktok.delete()

        tiktoks = Tiktok.objects.filter(weekly_report=weekly_report_id).order_by("order")
        for idx, tiktok in enumerate(tiktoks):
            tiktok.order = idx
            tiktok.save()
    

        return Response({"success": True}, status=status.HTTP_200_OK)

class TiktoksAPI(APIView):
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        tiktoks = Tiktok.objects.all()
        serializer = TiktokSerializer(tiktoks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        order = len(Tiktok.objects.filter(weekly_report=request.data.get("weekly_report")))
        data = {
            "weekly_report": request.data.get("weekly_report"),
            "thumbnail": "",
            "like_count": request.data.get("like_count"),
            "comment_count": request.data.get("comment_count"),
            "view_count": request.data.get("view_count"),
            "favourite_count": request.data.get("favourite_count"),
            "share_count": 0,
            "improvement_like_count": 0,
            "improvement_comment_count": 0,
            "improvement_view_count": 0,
            "improvement_favourite_count": 0,
            "notes": "",
            "url": request.data.get("url"),
            "created": datetime.today().strftime("%Y-%m-%d"),
            "manual": True,
            "order": order
        }
        serializer = TiktokSerializer(data=data)
        if serializer.is_valid():
            serializer_instance = serializer.save()
            serializer_instance.thumbnail =  save_thumbnail(WeeklyReport.objects.get(id=request.data.get("weekly_report")), serializer_instance.id, request.data.get("thumbnail").read())
            serializer_instance.save()            

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        for tiktok_url in request.data.get("urls"):
            tiktoks = Tiktok.objects.filter(url=tiktok_url)
            video = async_to_sync(get_video_by_url)(tiktok_url)

            if video == None:
                continue


            for tiktok in tiktoks:
                like_count=video.stats.digg_count
                comment_count=video.stats.comment_count
                view_count=video.stats.play_count
                favourite_count=video.stats.collect_count
                share_count=video.stats.share_count

                data = {
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "view_count": view_count,
                    "favourite_count": favourite_count,
                    "share_count": share_count,
                    "improvement_like_count": calculate_improvement(tiktok.improvement_like_count, like_count, tiktok.like_count),
                    "improvement_comment_count": calculate_improvement(tiktok.improvement_comment_count, comment_count, tiktok.comment_count),
                    "improvement_view_count": calculate_improvement(tiktok.improvement_view_count, view_count, tiktok.view_count),
                    "improvement_favourite_count": calculate_improvement(tiktok.improvement_favourite_count, favourite_count, tiktok.favourite_count),
                    "last_updated": datetime.today().strftime('%Y-%m-%d')
                }
                serializer = TiktokSerializer(instance=tiktok, data=data, partial=True)
                if not serializer.is_valid():
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)
    

class WeeklyReportAPI(APIView):
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request, weekly_report_id):
        tiktoks = Tiktok.objects.filter(weekly_report=weekly_report_id).order_by("order")
        tiktok_serializer = TiktokSerializer(tiktoks, many=True)

        weekly_report = WeeklyReport.objects.get(id=weekly_report_id)
        weekly_report_serializer = WeeklyReportSerializer(weekly_report)

        return Response({"tiktok": tiktok_serializer.data, "weekly_report": weekly_report_serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, weekly_report_id):
        weekly_report = WeeklyReport.objects.get(id=weekly_report_id)
        data = {}
        get_data(data, request.data.get("notes"), "notes")
        get_data(data, request.data.get("title"), "title")
        
        serializer = WeeklyReportSerializer(instance=weekly_report, data=data, partial=True)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class WeeklyReportsAPI(APIView):
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        weekly_reports = WeeklyReport.objects.filter(owner=request.user.id).order_by("-created_date")
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
            # "created_date": datetime.today().strftime('%d/%m/%y')
        }

        serializer = WeeklyReportSerializer(data=data)
        if serializer.is_valid():
            serializer_instance = serializer.save()

            get_videos_sync = async_to_sync(get_videos)
            user_tag = Client.objects.get(user=request.user).tiktok_account
    
            if user_tag == "":
                user_tag = "cheekyglo"

            serializer_instance = get_videos_sync(serializer_instance, int(request.data.get("number_of_videos")), user_tag)

            return_data = {
                "title": serializer_instance.title,
            }

            serializer_instance.save()

            return Response(return_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        for weekly_report_id in request.data.get("ids"):
            weekly_report = WeeklyReport.objects.get(id = weekly_report_id, owner=request.user.id)
            folder_path = f"{STATIC_FOLDER_PATH}/{request.user}/{weekly_report_id}"

            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            weekly_report.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)
