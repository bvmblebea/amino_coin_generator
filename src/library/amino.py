# coding = utf-8
import requests

from hmac import new
from os import urandom
from json import loads
from uuid import uuid4
from hashlib import sha1
from typing import BinaryIO
from time import time, timezone
from json_minify import json_minify
from websocket import create_connection
from base64 import b64encode, b64decode
from locale import getdefaultlocale as locale

class Amino:
	def __init__(self, device_id: str = None, proxies: dict = None):
		self.api = "https://service.narvii.com/api/v1"
		self.device_id = self.generate_device_id(urandom(20)) if not device_id else device_id
		self.headers = {
			"NDCDEVICEID": self.device_id,
			"Accept-Language": "en-US",
			"Content-Type": "application/json; charset=utf-8",
			"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; RMX2086 Build/RMX2086_11_C.12; com.narvii.amino.master/3.5.34191)", 
			"Host": "service.narvii.com",
			"Accept-Encoding": "gzip",
			"Connection": "Keep-Alive"
		}
		self.sid = None
		self.user_id = None
		self.proxies = proxies

	def generate_signature(self, data: str):
		self.headers["ndc-msg-sig"] = b64encode(
			bytes.fromhex("42") + new(bytes.fromhex("f8e7a61ac3f725941e3ac7cae2d688be97f30b93"), data.encode("utf-8"), sha1).digest()
		).decode("utf-8")
		return self.headers["ndc-msg-sig"]
	
	def generate_device_id(self, identifier: str):
		return (
			"42" + identifier.hex() + new(bytes.fromhex("02b258c63559d8804321c5d5065af320358d366f"), b"\x42" + identifier, sha1).hexdigest()
		).upper()
	
	def reload_socket(self):
		data = f"{self.device_id}|{int(time() * 1000)}"
		self.ws_headers = {
			"NDCDEVICEID": self.device_id,
			"NDCAUTH": f"sid={self.sid}",
			"NDC-MSG-SIG": self.generate_signature(data)
		}
		self.socket_time = time()
		self.ws = create_connection(f"wss://ws1.narvii.com?signbody={data}".replace("|", "%7C"), header=self.ws_headers)
  
	def login(self, email: str, password: str, socket: bool = True):
		data = {
			"email": email,
			"secret": f"0 {password}",
			"deviceID": self.device_id,
			"clientType": 100,
			"action": "normal",
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		response = requests.post(
			f"{self.api}/g/s/auth/login",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()
		if "sid" in response:
			self.sid = response["sid"]
			self.user_id = response["auid"]
			self.headers["NDCAUTH"] = f"sid={self.sid}"
			if socket:
				self.reload_socket()
		return response

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
		data = json_minify(data)
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/community/stats/user-active-time",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()

	def request_verify_code(self, email: str, reset_password: bool = False):
		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.device_id
		}
		if reset_password:
			data["level"] = 2
			data["purpose"] = "reset-password"
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/g/s/auth/request-security-validation",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()
	
	
	def register(
			self,
			nickname: str,
			email: str, 
			password: str,
			device_id: str,
			verification_code: int):
		data = {
			"secret": f"0 {password}",
			"deviceID": device_id,
			"email": email,
			"clientType": 100,
			"nickname": nickname,
			"latitude": 0,
			"longitude": 0,
			"address": None,
			"clientCallbackURL": "narviiapp://relogin",
			"validationContext": {
				"data": {
					"code": verification_code
				},
				"type": 1,
				"identity": email
            },
			"type": 1,
			"identity": email,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/g/s/auth/register",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()

	def get_from_device_id(self, device_id: str):
		return requests.get(
			f"{self.api}/g/s/auid?deviceId={device_id}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def accept_host(self, ndc_id: int, chat_id: str):
		data = {
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/accept-organizer",
			data=data,
			headers=self.headers, 
			proxies=self.proxies).json() 
		 
	def get_notifications(self, ndc_id: int, start: int = 0, size: int = 10):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/notification?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def check_device_id(self, device_id: str):
		data = {
			"deviceID": device_id,
			"bundleID": "com.narvii.amino.master",
			"clientType": 100,
			"timezone": -int(timezone) // 1000,
			"systemPushEnabled": True,
			"locale": locale()[0],
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/g/s/device",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_wallet_info(self):
		return requests.get(
			f"{self.api}/g/s/wallet",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_wallet_history(self, start: int = 0, size: int = 25):
		return requests.get(
			f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def my_communities(self, start: int = 0, size: int = 25):
		return requests.get(
			f"{self.api}/g/s/community/joined?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def watch_ad(self):
		return requests.post(
			f"{self.api}/g/s/wallet/ads/video/start",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def transfer_host(
			self,
			ndc_id: int,
			chat_id: str,
			user_ids: list):
		data = {
			"uidList": user_ids,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/transfer-organizer",
			data=data,
			headers=self.headers, 
			proxies=self.proxies).json()  

	def join_chat(self, ndc_id: int, chat_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member/{self.user_id}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def get_chat_messages(
			self,
			ndc_id: int,
			chat_id: str,
			size: int = 10):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message?v=2&pagingType=t&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_chat(self, ndc_id: int, chat_id: str):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def send_audio(
			self,
			path: str,
			ndc_id: int,
			chat_id: str):
		audio = b64encode(open(path, "rb").read())
		data = {
			"content": None,
			"type": 2,
			"clientRefId": int(time() / 10 % 1000000000),
			"timestamp": int(time() * 1000),
			"mediaType":110,
			"mediaUploadValue": audio,
			"attachedObject": None
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def ban_user(
			self,
			ndc_id: int,
			user_id: str,
			reason: str,
			ban_type: int = None):
		data = {
			"reasonType": ban_type,
			"note": {
				"content": reason 
			},
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/ban",
			data=data,
			headers=self.headers, 
			proxies=self.proxies).json() 
		 
	def get_banned_users(self, ndc_id: int, start: int = 0, size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/user-profile?type=banned&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def unban_user(
			self,
			ndc_id: int,
			user_id: str,
			reason: str):
		data = {
			"note": { 
				"content": reason 
			},
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/unban",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def create_chat_thread(
			self,
			ndc_id: int,
			message: str,
			user_id: str):
		data = {
			"inviteeUids": [user_id],
			"initialMessageContent": message,
			"type": 0,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()  

	def delete_message(
			self,
			ndc_id: int,
			chat_id: str,
			message_id: str,
			reason: str = None,
			asStaff: bool = False):
		data = {
			"adminOpName": 102,
			"adminOpNote": {"content": reason},
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		if asStaff:
			return requests.delete(
				f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message/{message_id}/admin",
				headers=self.headers,
				proxies=self.proxies).json() 
		else:
			return requests.post(
				f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message/{message_id}",
				data=data,
				headers=self.headers,
				proxies=self.proxies).json()  

	def kick(
			self,
			ndc_id: int,
			chat_id: str,
			user_id: str,
			allowRejoin: int = 0):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member/{user_id}?allowRejoin={allowRejoin}",
			headers=self.headers,
			proxies=self.proxies).json()   

	def create_sticker_pack(
			self,
			ndc_id: int,
			name: str,
			stickers: list):
		data = {
			"collectionType": 3,
			"description": "sticker_pack",
			"iconSourceStickerIndex": 0,
			"name": name, "stickerList": stickers,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/sticker-collection",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def search_user_chat(self, ndc_id: int, user_id: str):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/thread?type=exist-single&cv=1.2&q={user_id}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def change_vc_permission(
			self,
			ndc_id: int,
			chat_id: str,
			permission: int):
		data = {
			"vvChatJoinType": permission,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/vvchat-permission",
			headers=self.headers,
			data=data,
			proxies=self.proxies).json()  

	def send_embed(
			self,
			ndc_id: int,
			chat_id: str,
			message: str = None,
			embed_title: str = None,
			embed_content: str = None,
			link: str = None,
			embed_image: BinaryIO = None):
		data = {
			"type": 0,
			"content": message,
			"clientRefId": int(time() / 10 % 1000000000),
			"attachedObject": { 
				"objectId": None,
				"objectType": 100,
				"link": link,
				"title": embed_title,
				"content": embed_content,
				"mediaList": embed_image
				},
				"extensions": {
					"mentionedArray": None
				},
				"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message",
			headers=self.headers,
			data=data,
			proxies=self.proxies).json() 
		 
	def send_message(
			self,
			ndc_id: int,
			chat_id: str,
			message: str,
			message_type: int = 0,
			reply_message_id: str = None,
			notification : list = None):
		data = {
			"content": message,
			"type": message_type,
			"clientRefId": int(time() / 10 % 1000000000),
			"mentionedArray": [notification], 
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		if reply_message_id:
			data["replyMessageId"] = reply_message_id
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_chat_users(
			self,
			ndc_id: int,
			chat_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member&type=default&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def my_chat_threads(
			self,
			ndc_id: int,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/thread?type=joined-me&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def get_public_chat_threads(
			self,
			ndc_id: int,
			start: int = 0,
			size: int = 10):
		return requests.get(
			f"{self.api}/chat/live-threads?ndcId=x{ndc_id}&start={start}&size={size}",
			headers=self.headers).json()
		 
	def thank_tip(
			self,
			ndc_id: int,
			chat_id: str,
			user_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/tipping/tipped-users/{user_id}/thank",
			headers=self.headers,
			proxies=self.proxies).json()  

	def get_user(self, ndc_id: int, user_id: str):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}?action=visit",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_tipped_users_wall(
			self,
			ndc_id: int,
			blog_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/blog/{blog_id}/tipping/tipped-users-summary?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		
	def send_image(
			self,
			ndc_id: int,
			chat_id: str,
			image: str):
		data = {
			"type": 0,
			"clientRefId": int(time() / 10 % 1000000000),
			"timestamp": int(time() * 1000),
			"mediaType": 100, "mediaUploadValue": b64encode(open(image, "rb").read()).strip().decode(),
			"mediaUploadValueContentType": "image/jpg", 
			"mediaUhqEnabled": False, 
			"attachedObject": None
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def join_community(self, ndc_id: int, invitation_id: str = None):
		data = {
			"timestamp": int(time() * 1000)
		}
		if invitation_id:
			data["invitationId"] = invitation_id
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/community/join",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
	
	def invite_to_chat(
			self,
			ndc_id: int,
			chat_id: str,
			user_id: [str, list]):
		if isinstance(user_id, str):
			user_ids = [user_id]
		elif isinstance(user_id, list):
			user_ids = user_id
		data = {
			"uids": user_ids,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member/invite",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()  

	def get_online_users(
			self,
			ndc_id: int,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/live-layer?topic=ndtopic:x{ndc_id}:online-members&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  

	def get_recent_users(
			self,
			ndc_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/user-profile?type=recent&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
	
	def leave_chat(self, ndc_id: int, chat_id: str):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member/{self.user_id}",
			headers=self.headers,
			proxies=self.proxies).json() 
		
	def send_gif(self, ndc_id: int, chat_id: str, gif: str):
		data = {
			"type": 0,
			"clientRefId": int(time() / 10 % 1000000000),
			"timestamp": int(time() * 1000), 
			"mediaType": 100, 
			"mediaUploadValue": b64encode(open(gif, "rb").read()).strip().decode(), 
			"mediaUploadValueContentType": "image/gif",
			"mediaUhqEnabled": False,
			"attachedObject": None
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/message",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 

	def comment_profile(
			self,
			ndc_id: int,
			content: str,
			user_id: str):
		data = {
			"content": content,
			"mediaList": [], 
			"eventSource": "PostDetailView", 
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/comment",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_from_code(self, code: str):
		return requests.get(
			f"{self.api}/g/s/link-resolution?q={code}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_user_blogs(
			self,
			ndc_id: int,
			user_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/blog?type=user&q={user_id}&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def get_community_info(self, ndc_id: int):
		return requests.get(
			f"{self.api}/g/s-x{ndc_id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount",
			headers=self.headers,
			proxies=self.proxies).json() 
	
	def check_in(
			self,
			ndc_id: int = 0,
			time_zone: int = -int(timezone) // 1000):
		data = {
			"timezone": time_zone,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/check-in",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()  

	def send_coins_blog(
			self,
			ndc_id: int,
			blog_id: str = None, 
			coins: int = None,
			transaction_id: str = uuid4()):
		data = {
			"coins": coins,
			"tippingContext": {
				"transactionId": transaction_id
			},
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/blog/{blog_id}/tipping",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def send_coins_chat(
			self,
			ndc_id: int,
			chat_id: str = None,
			coins: int = None,
			transaction_id: str = uuid4()):
		data = {
			"coins": coins,
			"tippingContext": {
				"transactionId": transaction_id
			},
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/tipping",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()  

	def lottery(
			self,
			ndc_id: int,
			time_zone: str = -int(timezone) // 1000):
		data = {
			"timezone": time_zone,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/check-in/lottery",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def edit_chat(
			self,
			ndc_id: int,
			chat_id: str,
			content: str = None,
			title: str = None,
			background_image: str = None):
		response = []
		data = {
			"timestamp": int(time() * 1000)
		}
		if background_image:
			data["media"] = [100, background_image, None],
			self.generate_signature(data)
			response.append(requests.post(
				f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/member/{self.user_id}/background",
				data=data,
				headers=self.headers,
				proxies=self.proxies).json())
		if content:
			data["content"] = content
		if title:
			data["title"] = title
		generate_signature(data)
		response.append(requests.post(
		 	f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}",
		 	data=data,
		 	headers=self.headers, 
		 	proxies=self.proxies).json())
		return response
	   
	def moderation_history_community(self, ndc_id: int, size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/admin/operation?pagingType=t&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def moderation_history_user(
			self,
			ndc_id: int, 
			user_id: str = None, 
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/admin/operation?objectId={user_id}&objectType=0&pagingType=t&size={size}",
			headers=self.headers, 
			proxies=self.proxies).json() 
		 
	def moderation_history_blog(
			self,
			ndc_id: int,
			blog_id: str,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/admin/operation?objectId={blog_id}&objectType=1&pagingType=t&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def moderation_history_quiz(
			self, 
			ndc_id: int,
			quiz_id: str, 
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/admin/operation?objectId={quiz_id}&objectType=1&pagingType=t&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def moderation_history_wiki(
			self, ndc_id: int,
			wiki_id: str,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/admin/operation?objectId={wiki_id}&objectType=2&pagingType=t&size={size}",
			headers=self.headers,
			proxies=self.proxies).json() 
		 
	def give_curator(self, ndc_id: int, user_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/curator",
			headers=self.headers,
			proxies=self.proxies).json()  
		
	def give_leader(self, ndc_id: int, user_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/leader", 
			headers=self.headers, 
			proxies=self.proxies).json()  
		
	def get_bubble_info(self, ndc_id: int, bubble_id: str):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/chat/chat-bubble/{bubble_id}", 
			headers=self.headers, 
			proxies=self.proxies).json() 
		 
	def buy_bubble(self, ndc_id: int, bubble_id: str):
		data = {
			"objectId": bubble_id,
			"objectType": 116,
			"v": 1,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/store/purchase", 
			data=data, 
			headers=self.headers, 
			proxies=self.proxies).json() 

	def invite_to_vc(
			self,
			ndc_id: int,
			chat_id: str,
			user_id: str):
		data = {
			"uid": user_id
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}/vvchat-presenter/invite", 
			data=data, headers=self.headers, 
			proxies=self.proxies).json()  
	
	def delete_chat(self, ndc_id: int, chat_id: str):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/chat/thread/{chat_id}", 
			headers=self.headers, 
			proxies=self.proxies).json()  
    
	def delete_notification(self, ndc_id: int, notification_id: str):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/notification/{notificationId}", 
			headers=self.headers, 
			proxies=self.proxies).json() 
		 
	def clear_notifications(self, ndc_id: int):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/notification",
			headers=self.headers,
			proxies=self.proxies).json() 
		
	def edit_profile(
			self,
			ndc_id: int,
			nickname: str = None,
			content: str = None,
			chat_request_privilege: str = None,
			background_color: str = None,
			titles: list = None,
			colors: list = None,
			default_bubble_id: str = None):
		data = {
			"timestamp": int(time() * 1000)
		}
		if nickname:
			data["nickname"] = nickname
		if content:
			data["content"] = content
		if chat_request_privilege:
			data["extensions"] = {"privilegeOfChatInviteRequest": chat_request_privilege}
		if background_color:
			data["extensions"] = {"style": {"backgroundColor": background_color}}
		if default_bubble_id:
			data["extensions"] = {"defaultBubbleId": default_bubble_id}
		if titles or colors:
			titles_colors = []
			for titles, colors in zip(titles, colors):
				titles_colors.append(
					{
						"title": titles,
						"color": colors
					}
				)
			data["extensions"] = {"customTitles": titles_colors}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{self.user_id}",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()
		 
	def activate_account(self, email: str, verification_code: str):
		data = {
			"type": 1,
			"identity": email,
			"data": {
				"code": verification_codE
			},
			"deviceID": self.device_id
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/g/s/auth/activate-email",
			data=data,
			headers=self.headers, 
			proxies=self.proxies).json()
	
	def get_recent_blogs(
			self,
			ndc_id: int,
			start: int = 0,
			size: int = 10):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/feed/blog-all?pagingType=t&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	def like_blog(self, ndc_id: int, blog_id: str):
		data = {
			"value": 4,
			"eventSource": "UserProfileView",
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/blog/{blog_id}/vote?cv=1.2",
			data=data,
			headers=self.headers, 
			proxies=self.proxies).json()

	def follow_user(self, ndc_id: int, user_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/member",
			headers=self.headers,
			proxies=self.proxies).json()
		
	def unfollow_user(self, ndc_id: int, user_id: str):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/user-profile/{self.user_id}/joined/{user_id}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	def get_user_following(
			self,
			ndc_id: int,
			user_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/joined?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()

	def get_user_followers(
			self,
			ndc_id: int,
			user_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/user-profile/{user_id}/member?start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	def block_user(self, ndc_id: int, user_id: str):
		return requests.post(
			f"{self.api}/x{ndc_id}/s/block/{user_id}",
			headers=self.headers,
			proxies=self.proxies).json()
		
	def unblock_user(self, ndc_id: int, user_id: str):
		return requests.delete(
			f"{self.api}/x{ndc_id}/s/block/{user_id}",
			headers=self.headers,
			proxies=self.proxies).json()

	def get_online_users(
			self,
			ndc_id: int,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/live-layer?topic=ndtopic:x{ndc_id}:online-members&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()

	def get_blog_info(self, ndc_id: int, blog_id: str):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/blog/{blog_id}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	def get_user_blogs(
			self,
			ndc_id: int,
			user_id: str,
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/x{ndc_id}/s/blog?type=user&q={user_id}&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	# 1 = online, 2 = offline
	def set_activity_status(self, ndc_id: int, status: int = 1):
		data = {
			"onlineStatus": status,
			"duration": 86400,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/user-profile/{self.user_id}/online-status",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()
	
	def get_invite_codes(
			self,
			ndc_id: int,
			status: str = "normal",
			start: int = 0,
			size: int = 25):
		return requests.get(
			f"{self.api}/g/s-x{ndc_id}/community/invitation?status={status}&start={start}&size={size}",
			headers=self.headers,
			proxies=self.proxies).json()
	
	def listen(self, return_data: int = 1):
		if((time() - self.socket_time) > 100):
			self.ws.close()
			self.reload_socket()
		while 1:
			try:
				return loads(self.ws.recv())     
			except:
				continue

	def change_password(self, password: str, new_password: str):
		data = {
			"secret": f"0 {password}",
			"updateSecret": f"0 {newPassword}",
			"validationContext": None,
			"deviceID": self.device_id
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/g/s/auth/change-password",
			data=data,
			headers=self.headers,
			proxies=self.proxies)
	
	def post_blog(
			self,
			ndc_id: int,
			title: str,
			content: str,
			image_list: list = None,
			caption_list: list = None,
			categories_list: list = None,
			background_color: str = None,
			fans_only: bool = False,
			extensions: dict = None):
		media_list = []
		if caption_list:
			for image, caption in zip(image_list, caption_list):
				media_list.append([100, self.upload_media(image, "image"), caption])
		else:
			if image_list:
				for image in image_list:
					media_list.append([100, self.upload_media(image, "image"), None])
					
		data = {
			"address": None,
			"content": content,
			"title": title,
			"mediaList": media_list,
			"extensions": extensions,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "GlobalComposeMenu",
			"timestamp": int(time() * 1000)
		}
		
		if fans_only:
			data["extensions"] = {"fansOnly": fansOnly}
		if background_color:
			data["extensions"] = {"style": {"backgroundColor": background_color}}
		if categories_list:
			data["taggedBlogCategoryIdList"] = categories_list
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/blog",
			data=data,
			headers=self.headers,
			proxies=self.proxies).json()
	
	def repost_blog(
			self,
			ndc_id: int,
			content: str = None,
			blog_id: str = None,
			wiki_id: str = None):
		if blog_id:
			ref_object_id = blog_id
			ref_object_type = 1
		elif wiki_id:
			ref_object_id = wiki_id,
			ref_object_type = 2
		data = {
			"content": content,
			"refObjectId": ref_object_id,
			"refObjectType": ref_object_type,
			"type": 2,
			"timestamp": int(time() * 1000)
		}
		self.generate_signature(data)
		return requests.post(
			f"{self.api}/x{ndc_id}/s/blog",
			data=data, 
			headers=self.headers, 
			proxies=self.proxies).json()
