# coding = utf-8
# -- Library made by deluvsushi
# -- github.com/Zakovskiy помог с библиотекой
# -- github.com/Minori100 недокодер, чурка, безмамный
import requests
from hmac import new
from os import urandom
from uuid import uuid4
from hashlib import sha1
from typing import BinaryIO
from json import dumps, loads
from time import time, timezone
from json_minify import json_minify
from base64 import b64encode, b64decode
from locale import getdefaultlocale as locale


class Client:
    def __init__(self, device_Id: str = None, proxy: dict = None):
        self.device_Id = self.generate_device_Id(
            urandom(20)) if not device_Id else device_Id
        self.api = "https://service.narvii.com/api/v1"
        self.proxy = proxy
        self.headers = {
            "NDCDEVICEID": self.device_Id,
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33597)",
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"}
        self.sid = None
        self.auid = None

    # generate NDC-MSG-SIG
    def generate_signature(self, data: str):
        signature = b64encode(
            bytes.fromhex("32") + new(
                bytes.fromhex("fbf98eb3a07a9042ee5593b10ce9f3286a69d4e2"),
                data.encode("utf-8"),
                sha1).digest()).decode("utf-8")
        self.headers["NDC-MSG-SIG"] = signature
        return signature

    # generate device_Id
    def generate_device_Id(self, identifier: str):
        return ("32" +
                identifier.hex() +
                new(bytes.fromhex("76b4a156aaccade137b8b1e77b435a81971fbd3e"), b"\x32" +
                    identifier, sha1).hexdigest()).upper()

    # authorization
    def auth(self, email: str, password: str):
        data = dumps({
            "email": email,
            "secret": f"0 {password}",
            "deviceID": self.device_Id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        response = requests.post(
            f"{self.api}/g/s/auth/login",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()
        try:
            self.sid = response["sid"]
            self.auid = response["auid"]
            self.headers["NDCAUTH"] = f"sid={self.sid}"
        except BaseException:
            print(f">> {response['api:message']}")
        return response

    # send active object
    def send_active_object(
            self,
            ndc_id: int,
            start_time: int = None,
            end_time: int = None,
            timers: list = None):
        data = {
            "userActiveTimeChunkList": [
                {
                    "start": start_time,
                    "end": end_time
                }
            ],
            "timestamp": int(time() * 1000),
            "optInAdsFlags": 2147483647,
            "timezone": -timezone // 1000
        }
        if timers:
            data["userActiveTimeChunkList"] = timers
        data = json_minify(dumps(data))
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/community/stats/user-active-time",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # request verify code
    def request_verify_code(self, email: str, reset_password: bool = False):
        data = {
            "identity": email,
            "type": 1,
            "deviceID": self.device_Id
        }
        if reset_password is True:
            data["level"] = 2
            data["purpose"] = "reset-password"
        data = dumps(data)
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/g/s/auth/request-security-validation",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # register account
    def register(
            self,
            nickname: str = None,
            email: str = None,
            password: str = None,
            device_Id: str = None):
        data = dumps({
            "secret": f"0 {password}",
            "deviceID": device_Id,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "type": 1,
            "identity": email,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/g/s/auth/register",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get from device_Id
    def get_from_device_Id(self, device_Id: str):
        return requests.get(
            f"{self.api}/g/s/auid?deviceId={device_Id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # accept host in thread(chat)
    def accept_host(self, ndc_id: int, thread_id: str):
        data = dumps({"timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/accept-organizer",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get notification list
    def get_notifications(self, ndc_id: int, start: int = 0, size: int = 10):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/notification?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # check device_Id
    def check_device_Id(self, device_Id: str):
        data = dumps({
            "deviceID": device_Id,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -int(timezone) // 1000,
            "systemPushEnabled": True,
            "locale": locale()[0],
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/g/s/device",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get wallet info
    def get_wallet_info(self):
        return requests.get(
            f"{self.api}/g/s/wallet",
            headers=self.headers,
            proxies=self.proxy).json()

    # get wallet history
    def get_wallet_history(self, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get joined communities list
    def my_communities(self, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/g/s/community/joined?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # watch ad
    def watch_ad(self):
        return requests.post(
            f"{self.api}/g/s/wallet/ads/video/start",
            headers=self.headers,
            proxies=self.proxy).json()

    # transfer host in thread(chat)
    def transfer_host(self, ndc_id: int, thread_id: str, user_ids: list):
        data = dumps({
            "uidList": user_ids,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/transfer-organizer",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # join thread(chat)
    def join_thread(self, ndc_id: int, thread_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member/{self.auid}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get thread(chat) messages list
    def get_thread_messages(self, ndc_id: int, thread_id: str, size: int = 10):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message?v=2&pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get thread(chat)
    def get_thread(self, ndc_id: int, thread_id: str):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # send audio
    def send_audio(self, path, ndc_id: int, thread_id: str):
        audio = b64encode(open(path, "rb").read())
        data = dumps({"content": None,
                      "type": 2,
                      "clientRefId": 827027430,
                      "timestamp": int(time() * 1000),
                      "mediaType": 110,
                      "mediaUploadValue": audio,
                      "attachedObject": None})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # ban user
    def ban_user(
            self,
            ndc_id: int,
            user_id: str,
            reason: str,
            ban_type: int = None):
        data = dumps({
            "reasonType": ban_type,
            "note": {
                "content": reason
            },
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/ban",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get banned users list
    def get_banned_users(self, ndc_id: int, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/user-profile?type=banned&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # unban user
    def unban_user(self, ndc_id: int, user_id: str, reason: str):
        data = dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/unban",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # start chat
    def create_chat_thread(self, ndc_id: int, message: str, user_id: str):
        data = dumps({"inviteeUids": [user_id],
                      "initialMessageContent": message,
                      "type": 0,
                      "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # delete message from thread(chat)
    def delete_message(
            self,
            ndc_id: int,
            thread_id: str,
            message_Id: str,
            reason: str = None,
            asStaff: bool = False):
        data = dumps({
            "adminOpName": 102,
            "adminOpNote": {"content": reason},
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        if not asStaff:
            return requests.delete(
                f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message/{message_Id}",
                headers=self.headers,
                proxies=self.proxy).json()
        else:
            return requests.post(
                f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message/{message_Id}/admin",
                data=data,
                headers=self.headers,
                proxies=self.proxy).json()

    # kick user from thread(chat)
    def kick(
            self,
            ndc_id: int,
            thread_id: str,
            user_id: str,
            allowRejoin: int = 0):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member/{user_id}?allowRejoin={allowRejoin}",
            headers=self.headers,
            proxies=self.proxy).json()

    # load sticker Image
    def load_sticker_Image(self, link: str):
        data = requests.get(link).content
        return requests.post(
            f"{self.api}/g/s/media/upload/target/sticker",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # create sticker pack
    def create_sticker_pack(self, ndc_id: int, name, stickers):
        data = dumps({"collectionType": 3,
                      "description": "sticker_pack",
                      "iconSourceStickerIndex": 0,
                      "name": name,
                      "stickerList": stickers,
                      "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/sticker-collection",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # search user thread
    def search_user_thread(self, ndc_id: int, user_id: str):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/thread?type=exist-single&cv=1.2&q={user_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # change vc permission
    def change_vc_permission(
            self,
            ndc_id: int,
            thread_id: str,
            permission: int):
        data = dumps({"vvChatJoinType": permission,
                     "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/vvchat-permission",
            headers=self.headers,
            data=data,
            proxies=self.proxy).json()

    # send embed

    def send_embed(
            self,
            ndc_id: int,
            thread_id: str,
            message: str = None,
            embed_title: str = None,
            embed_content: str = None,
            link: str = None,
            embed_Image: BinaryIO = None):
        data = dumps({
            "type": 0,
            "content": message,
            "clientRefId": int(time() / 10 % 1000000000),
            "attachedObject": {
                "objectId": None,
                "objectType": 100,
                "link": link,
                "title": embed_title,
                "content": embed_content,
                "mediaList": embed_Image
            },
            "extensions": {"mentionedArray": None},
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message",
            headers=self.headers,
            data=data,
            proxies=self.proxy).json()

    # send message to thread(chat)

    def send_message(
            self,
            ndc_id: int,
            thread_id: str,
            message: str,
            message_type: int = 0,
            reply_message_Id: str = None,
            notification: list = None,
            client_refId: int = 43196704):
        data = {
            "content": message,
            "type": message_type,
            "clientRefId": client_refId,
            "mentionedArray": [notification],
            "timestamp": int(
                time() * 1000)}
        ndc_msg_sig = self.generate_signature(data=data)
        if reply_message_Id is not None:
            data["replyMessageId"] = reply_message_Id
        data = dumps(data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # admin delete message
    def admin_delete_message(
            self,
            ndc_id: int,
            thread_id: str,
            message_Id: str):
        data = dumps({"adminOpName": 102, "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message/{message_Id}/admin",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get thread(chat) users
    def get_thread_users(
            self,
            ndc_id: int,
            thread_id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member&type=default&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get joined threads(chats) list
    def my_chat_threads(self, ndc_id: int, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/thread?type=joined-me&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get public chats list
    def get_public_chat_threads(
            self,
            ndc_id: int,
            start: int = 0,
            size: int = 10):
        return requests.get(
            f"{self.api}/chat/live-threads?ndcId=x{ndc_id}&start={start}&size={size}",
            headers=self.headers)

    # thank tip
    def thank_tip(self, ndc_id: int, thread_id: str, user_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/tipping/tipped-users/{user_id}/thank",
            headers=self.headers,
            proxies=self.proxy).json()

    # get user
    def get_user(self, ndc_id: int, user_id: str):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}?action=visit",
            headers=self.headers,
            proxies=self.proxy).json()

    # get tipped users wall
    def get_tipped_users_wall(
            self,
            ndc_id: int,
            blog_Id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/blog/{blog_Id}/tipping/tipped-users-summary?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # send Image
    def send_Image(self, ndc_id: int, thread_id: str, image: str):
        image = b64encode(open(image, "rb").read())
        data = dumps({"type": 0,
                      "clientRefId": 43196704,
                      "timestamp": int(time() * 1000),
                      "mediaType": 100,
                      "mediaUploadValue": image.strip().decode(),
                      "mediaUploadValueContentType": "image/jpg",
                      "mediaUhqEnabled": False,
                      "attachedObject": None})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # join community

    def join_community(self, ndc_id: int, invitation_Id: str = None):
        data = {"timestamp": int(time() * 1000)}
        if invitation_Id:
            data["invitationId"] = invitation_Id
        data = dumps(data)
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/community/join",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # invite to chat
    def invite_to_chat(
        self,
        ndc_id: int,
        thread_id: str,
        user_id: [
            str,
            list]):
        if isinstance(user_id, str):
            user_ids = [user_id]
        elif isinstance(user_id, list):
            user_ids = user_id
        data = dumps({
            "uids": user_ids,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member/invite",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get online users
    def get_online_members(self, ndc_id: int, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/live-layer?topic=ndtopic:x{ndc_id}:online-members&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get recent users
    def get_recent_members(self, ndc_id: str, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/user-profile?type=recent&start={start}&size={size}",
            headers=self.headers)

    # leave chat
    def leave_thread(self, ndc_id: int, thread_id: str):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member/{self.auid}",
            headers=self.headers,
            proxies=self.proxy).json()

    # send gif
    def send_gif(self, ndc_id: int, thread_id: str, gif: str):
        image = b64encode(open(gif, "rb").read())
        data = dumps({"type": 0,
                      "clientRefId": 43196704,
                      "timestamp": int(time() * 1000),
                      "mediaType": 100,
                      "mediaUploadValue": image.strip().decode(),
                      "mediaUploadValueContentType": "image/gid",
                      "mediaUhqEnabled": False,
                      "attachedObject": None})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/message",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # comment profile
    def comment_profile(self, ndc_id: int, content: str, user_id: str):
        data = dumps({"content": content,
                      "mediaList": [],
                      "eventSource": "PostDetailView",
                      "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/comment",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get from link
    def get_from_link(self, link: str):
        return requests.get(
            f"{self.api}/g/s/link-resolution?q={link}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get user blogs
    def get_user_blogs(
            self,
            ndc_id: int,
            user_id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/blog?type=user&q={user_id}&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get community info
    def get_community_info(self, ndc_id: int):
        return requests.get(
            f"{self.api}/g/s-x{ndc_id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount",
            headers=self.headers,
            proxies=self.proxy).json()

    # check in
    def check_In(self, ndc_id: int = 0, tz: int = -int(timezone) // 1000):
        data = dumps({"timezone": tz, "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/check-in",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # send coins to blog

    def send_coins_blog(
            self,
            ndc_id: int,
            blog_Id: str = None,
            coins: int = None,
            transaction_Id: str = None):
        if transaction_Id is None:
            transaction_Id = str(uuid4())
        data = dumps({"coins": coins,
                      "tippingContext": {"transactionId": transaction_Id},
                      "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/blog/{blog_Id}/tipping",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # send coins to thread
    def send_coins_thread(
            self,
            ndc_id: int,
            thread_id: str = None,
            coins: int = None,
            transaction_Id: str = None):
        if transaction_Id is None:
            transaction_Id = str(uuid4())
        data = dumps({"coins": coins,
                      "tippingContext": {"transactionId": transaction_Id},
                      "timestamp": int(time() * 1000)})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/tipping",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # play lottery
    def lottery(self, ndc_id: int, time_zone: str = -int(timezone) // 1000):
        data = dumps({
            "timezone": time_zone,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/check-in/lottery",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # edit chat
    def edit_thread(
            self,
            ndc_id: int,
            thread_id: str,
            content: str = None,
            title: str = None,
            background_Image: str = None):
        result = []

        if background_Image is not None:
            data = dumps(
                {"media": [100, background_Image, None], "timestamp": int(time() * 1000)})
            ndc_msg_sig = self.generate_signature(data=data)
            response = requests.post(
                f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/member/{self.auid}/background",
                data=data,
                headers=self.headers,
                proxies=self.proxy).json()
            result.append(response)

        data = {"timestamp": int(time() * 1000)}
        ndc_msg_sig = self.generate_signature(data=data)
        if content:
            data["content"] = content
        if title:
            data["title"] = title
        data = dumps(data)
        response = requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()
        result.append(response)
        return result

    # Moder:{ from zakovskiy library

    def moderation_history_community(self, ndc_id: int, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/admin/operation?pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    def moderation_history_user(
            self,
            ndc_id: int = 0,
            user_id: str = None,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/admin/operation?objectId={user_id}&objectType=0&pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    def moderation_history_blog(
            self,
            ndc_id: int = 0,
            blog_Id: str = None,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/admin/operation?objectId={blog_Id}&objectType=1&pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    def moderation_history_quiz(
            self,
            ndc_id: int = 0,
            quiz_Id: str = None,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/admin/operation?objectId={quiz_Id}&objectType=1&pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    def moderation_history_wiki(
            self,
            ndc_id: int,
            wiki_Id: str = None,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/admin/operation?objectId={wiki_Id}&objectType=2&pagingType=t&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    def give_curator(self, ndc_id: int, user_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{uid}/curator",
            headers=self.headers,
            proxies=self.proxy).json()

    def give_leader(self, ndc_id: int, user_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{uid}/leader",
            headers=self.headers,
            proxies=self.proxy).json()

    # }

    # Bubble:{ from zakovskiy library

    def upload_bubble_1(self, file: str):
        data = open(file, "rb").read()
        return requests.post(
            f"{self.api}/g/s/media/upload/target/chat-bubble-thumbnail",
            data=data,
            headers=self.headers,
            lroxies=self.proxy)

    def upload_bubble_2(self, ndc_id: int, template_Id: str, file: str):
        data = open(file, "rb").read()
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/chat-bubble/{template_Id}",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    def generate_bubble(
            self,
            ndc_id: int,
            file: str,
            template_Id: str = "fd95b369-1935-4bc5-b014-e92c45b8e222"):
        data = open(file, "rb").read()
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/chat-bubble/templates/{template_Id}/generate",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    def get_bubble_info(self, ndc_id: int, bubble_Id: str):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/chat/chat-bubble/{bubble_Id}",
            headers=self.headers,
            proxies=self.proxy).json()

    def buy_bubble(self, ndc_id: int, bubble_Id: str):
        data = dumps({
            "objectId": bubble_Id,
            "objectType": 116,
            "v": 1,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/store/purchase",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # }

    # invite to voice chat
    def invite_to_vc(self, ndc_id: int, thread_id: str, user_id: str):
        data = dumps({"uid": user_id})
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}/vvchat-presenter/invite",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # delete thread (chat)
    def delete_thread(self, ndc_id: int, thread_id: str):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/chat/thread/{thread_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # delete notification
    def delete_notification(self, ndc_id: int, notification_Id: str):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/notification/{notificationId}",
            headers=self.headers,
            proxies=self.proxy).json()

    # clear notifications
    def clear_notifications(self, ndc_id: int):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/notification",
            headers=self.headers,
            proxies=self.proxy).json()

    # edit profile
    def edit_profile(
            self,
            ndc_id: int,
            nickname: str = None,
            content: str = None,
            chat_request_privilege: str = None,
            background_color: str = None,
            titles: list = None,
            colors: list = None,
            default_bubble_Id: str = None):
        data = {"timestamp": int(time() * 1000)}
        if nickname:
            data["nickname"] = nickname
        elif content:
            data["content"] = content
        elif chat_request_privilege:
            data["extensions"] = {
                "privilegeOfChatInviteRequest": chatRequestPrivilege}
        elif background_color:
            data["extensions"] = {
                "style": {
                    "backgroundColor": backgroundColor}}
        elif default_bubble_Id:
            data["extensions"] = {"defaultBubbleId": defaultBubbleId}
        if titles or colors:
            titles_colors = []
            for titles, colors in zip(titles, colors):
                titles_colors.append({"title": titles, "color": colors})

            data["extensions"] = {"customTitles": titles_colors}

        data = dumps(data)
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{self.auid}",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get tapjoy reward. P.S maybe it doesn't work yet coz sirlez turned off
    # repl
    def get_tapjoy_reward(self, user_id: str = None, repeat: int = 200):
        if not user_id:
            user_id = self.auid
        data = dumps({
            "userId": user_id,
            "repeat": str(repeat)
        })
        return requests.post(
            f"https://samino.sirlez.repl.co/api/tapjoy",
            json=data).text

    # activate account
    def activate_account(self, email: str, verification_code: str):
        data = dumps({
            "type": 1,
            "identity": email,
            "data": {"code": verification_code},
            "deviceID": self.device_Id
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/g/s/auth/activate-email",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get recent blogs
    def get_recent_blogs(self, ndc_id: int, start: int = 0, size: int = 10):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/feed/blog-all?pagingType=t&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # like blog
    def like_blog(self, ndc_id: int, blog_Id: str):
        data = dumps({
            "value": 4,
            "eventSource": "UserProfileView",
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/blog/{blog_Id}/vote?cv=1.2",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # follow user
    def follow_user(self, ndc_id: int, user_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/member",
            headers=self.headers,
            proxies=self.proxy).json()

    # unfollow user
    def unfollow_user(self, ndc_id: int, user_id: str):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/user-profile/{self.auid}/joined/{user_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get user following
    def get_user_following(
            self,
            ndc_id: int,
            user_id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/joined?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get user followers
    def get_user_followers(
            self,
            ndc_id: int,
            user_id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/member?start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # block user
    def block_user(self, ndc_id: int, user_id: str):
        return requests.post(
            f"{self.api}/x{ndc_id}/s/block/{user_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # unblock user
    def unblock_user(self, ndc_id: int, user_id: str):
        return requests.delete(
            f"{self.api}/x{ndc_id}/s/block/{user_id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get online users
    def get_online_users(self, ndc_id: int, start: int = 0, size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/live-layer?topic=ndtopic:x{ndc_id}:online-members&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get blog info
    def get_blog_info(self, ndc_id: int, blog_Id: str):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/blog/{blog_Id}",
            headers=self.headers,
            proxies=self.proxy).json()

    # get user blogs
    def get_user_blogs(
            self,
            ndc_id: int,
            user_id: str,
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/x{ndc_id}/s/blog?type=user&q={user_id}&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()

    # set_activity status, 1 = online, 2 = offline
    def set_activity_status(self, ndc_id: int, status: int = 1):
        data = dumps({
            "onlineStatus": status,
            "duration": 86400,
            "timestamp": int(time() * 1000)
        })
        ndc_msg_sig = self.generate_signature(data=data)
        return requests.post(
            f"{self.api}/x{ndc_id}/s/user-profile/{self.auid}/online-status",
            data=data,
            headers=self.headers,
            proxies=self.proxy).json()

    # get invite codes
    def get_invite_codes(
            self,
            ndc_id: int,
            status: str = "normal",
            start: int = 0,
            size: int = 25):
        return requests.get(
            f"{self.api}/g/s-x{ndc_id}/community/invitation?status={status}&start={start}&size={size}",
            headers=self.headers,
            proxies=self.proxy).json()
