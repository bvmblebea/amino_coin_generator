# coding = utf-8
import json
import time
import string
import base64
import random
import requests
from uuid import uuid4
from typing import BinaryIO
from json_minify import json_minify
from locale import getdefaultlocale as locale


class Client:
	def __init__(self, device_Id: str = "32DB0120CBB3C3FDC585A637104CBFBDB10D1D3F93158049AE921DA40A88318DB3DDEA6BCD9F9A31C7", proxy: dict = None):
		self.api = "https://service.narvii.com/api/v1"
		self.device_Id = device_Id
		self.proxy = proxy
		self.headers = {
		"NDCDEVICEID": self.device_Id,
		"Accept-Language": "en-US",
		"Content-Type": "application/json; charset=utf-8",
		"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)", 
		"Host": "service.narvii.com",
		"Accept-Encoding": "gzip",
		"Connection": "Keep-Alive"
		}
		self.sid = None
		self.auid = None

	# Generate NDC-MSG-SIG 
	
	
	def generate_signature(self, data):
		try:
			signature = requests.get(f"https://emerald-dream.herokuapp.com/signature/{data}").json()["signature"]
			self.headers["NDC-MSG-SIG"] = signature
			return signature
		except:
			self.generate_signature(data=data)
		

	# authorization
	def auth(self, email: str, password: str):
		data = {
		"email": email,
		"secret": f"0 {password}",
		"deviceID": self.device_Id,
		"clientType": 100,
		"action": "normal",
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/g/s/auth/login", data=data, headers=self.headers, proxies=self.proxy)
		try:
			self.sid = request.json()["sid"]
			self.auid = request.json()["auid"]
		except:
			print(f">> {request.json()['api:message']}")
		return request.json()

	# send active object
	def send_active_object(self, ndc_Id: int, start_time: int = None, end_time: int = None, timers: list = None):
		data = {
		"userActiveTimeChunkList": [{
			"start": start_time,
			"end": end_time
		}],
		"timestamp": int(time.time() * 1000),
		"optInAdsFlags": 2147483647,
		"timezone": -time.timezone // 1000
		}

		if timers:
			data["userActiveTimeChunkList"] = timers

		data = json_minify(json.dumps(data))
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/community/stats/user-active-time?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

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
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/g/s/auth/request-security-validation", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# register account
	def register(self, nickname: str = None, email: str = None, password: str = None, device_Id: str = None):
		data = {
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
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/g/s/auth/register", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# get from device_Id
	def get_from_device_Id(self, device_Id: str):
		request = requests.get(f"{self.api}/g/s/auid?deviceId={device_Id}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# accept host in thread(chat)
	def accept_host(self, ndc_Id, thread_Id: str):
		data = {"timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/accept-organizer?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# get notification list
	def get_notifications(self, ndc_Id, start: int = 0, size: int = 10):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/notification?start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# check device_Id 
	def check_device_Id(self, device_Id: str):
		data = {
		"deviceID": device_Id,
		"bundleID": "com.narvii.amino.master",
		"clientType": 100,
		"timezone": -int(time.timezone) // 1000,
		"systemPushEnabled": True,
		"locale": locale()[0],
		"timestamp": int(time.time() * 1000)
		}
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/g/s/device", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# get wallet info
	def get_wallet_info(self):
		request = requests.get(f"{self.api}/g/s/wallet?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get wallet history
	def get_wallet_history(self, start:int = 0, size:int = 25):
		request = requests.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get joined communities list
	def my_communities(self, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/g/s/community/joined?start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# watch ad
	def watch_ad(self):
		request = requests.post(f"{self.api}/g/s/wallet/ads/video/start?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
	
	# transfer host in thread(chat)
	def transfer_host(self, ndc_Id, thread_Id: str, user_Ids: list):
		data = {
		"uidList": user_Ids,
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/transfer-organizer?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# join thread(chat)
	def join_thread(self, ndc_Id, thread_Id: str):
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member/{self.auid}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get thread(chat) messages list
	def get_thread_messages(self, ndc_Id, thread_Id: str, size: int = 10):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?v=2&pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get thread(chat)
	def get_thread(self, ndc_Id, thread_Id: str):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# send audio
	def send_audio(self, path, ndc_Id, thread_Id: str):
		audio = base64.b64encode(open(path, "rb").read())
		data = {"content": None,"type": 2,"clientRefId": 827027430,"timestamp": int(time.time() * 1000), "mediaType":110, "mediaUploadValue": audio, "attachedObject": None}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# ban user
	def ban(self, ndc_Id, user_Id: str, reason: str, ban_type: int = None):
		data = {
		"reasonType": ban_type,
		"note": {
			"content": reason 
		},
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{user_Id}/ban?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# get banned users list
	def get_banned_users(self, ndc_Id, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/user-profile?type=banned&start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# unban user
	def unban(self, ndc_Id, user_Id: str, reason: str):
		data = {
		"note": { 
			"content": reason 
		},
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{user_Id}/unban?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# start chat
	def create_chat_thread(self, ndc_Id, message: str, user_Id: str):
		data = {"inviteeUids": [user_Id], "initialMessageContent": message, "type": 0, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# delete message from thread(chat)
	def delete_message(self, ndc_Id, thread_Id: str, message_Id: str, reason: str = None, asStaff: bool = False):
		data = {
		"adminOpName": 102,
		"adminOpNote": {"content": reason},
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		if not asStaff:
			request = requests.delete(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message/{message_Id}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		else:
			request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message/{message_Id}/admin?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# kick user from thread(chat)
	def kick(self, ndc_Id, thread_Id: str, user_Id: str, allowRejoin: int = 0):
		request = requests.delete(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member/{user_Id}?allowRejoin={allowRejoin}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# load sticker Image
	def load_sticker_Image(self, link: str):
		data = requests.get(link).content
		request = requests.post(f"{self.api}/g/s/media/upload/target/sticker?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# create sticker pack
	def create_sticker_pack(self, ndc_Id, name, stickers):
		data = {"collectionType": 3, "description": "sticker_pack", "iconSourceStickerIndex": 0, "name": name, "stickerList": stickers, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/sticker-collection?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# search user thread
	def search_user_thread(self, ndc_Id, user_Id: str):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/thread?type=exist-single&cv=1.2&q={user_Id}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# change vs permission
	def change_vc_permission(self, ndc_Id, thread_Id: str, permission: int):
		data = {"vvChatJoinType": permission, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/vvchat-permission?sid={self.sid}", headers=self.headers, data=data, proxies=self.proxy)
		return request.json()

	# send embed
	def send_embed(self, ndc_Id, thread_Id: str, message: str = None, embed_title: str = None, embed_content: str = None, link: str = None, embed_Image: BinaryIO = None):
		data = {
		"type": 0,
		"content": message,
		"clientRefId": int(time.time() / 10 % 1000000000),
		"attachedObject": { 
			"objectId": None,
			"objectType": 100,
			"link": link,
			"title": embed_title,
			"content": embed_content,
			"mediaList": embed_Image
			},
			"extensions": {"mentionedArray": None},
			"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?sid={self.sid}", headers=self.headers, data=data, proxies=self.proxy)
		return request.json()
	
	# send message to thread(chat)
	def send_message(self, ndc_Id, thread_Id: str, message: str, message_type: int = 0, reply_message_Id: str = None, notification : list = None, client_ref_Id: int = 43196704):
		data = {"content": message, "type": message_type, "clientRefId": client_ref_Id, "mentionedArray": [notification], "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		if reply_message_Id != None:	data["replyMessageId"] = reply_message_Id
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# admin delete message
	def admin_delete_message(self, ndc_Id, thread_Id: str, message_Id: str):
		data = {"adminOpName": 102, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message/{message_Id}/admin?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
	
	# get thread(chat) users
	def get_thread_users(self, ndc_Id, thread_Id: str, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member?sid={self.sid}&type=default&start={start}&size={size}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get joined threads(chats) list
	def my_chat_threads(self, ndc_Id, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/thread?type=joined-me&start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get public chats list
	def get_public_chat_threads(self, ndc_Id, start: int = 0, size: int = 10):
		request = requests.get(f"{self.api}/chat/live-threads?ndcId=x{ndc_Id}&start={start}&size={size}", headers=self.headers)
		return request.json()

	# thank tip
	def thank_tip(self, ndc_Id, thread_Id: str, user_Id: str):
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/tipping/tipped-users/{user_Id}/thank?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get user
	def get_user(self, ndc_Id, user_Id: str):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/user-profile/{user_Id}?action=visit&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get tipped users wall
	def get_tipped_users_wall(self, ndc_Id, blog_Id: str, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/blog/{blog_Id}/tipping/tipped-users-summary?start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# send Image
	def send_Image(self, ndc_Id, thread_Id: str, image: str):
		image = base64.b64encode(open(image, "rb").read())
		data = {"type": 0, "clientRefId": 43196704, "timestamp": int(time.time() * 1000), "mediaType": 100, "mediaUploadValue": image.strip().decode(), "mediaUploadValueContentType": "image/jpg", "mediaUhqEnabled": False, "attachedObject": None}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# join community
	def join_community(self, ndc_Id, invitation_Id: str = None):
		data = {"timestamp": int(time.time() * 1000)}
		if invitation_Id:	data["invitationId"] = invitationId
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/community/join?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# invite to chat
	def invite_to_chat(self, ndc_Id, thread_Id: str, user_Id: [str, list]):
		if isinstance(user_Id, str): user_Ids = [user_Id]
		elif isinstance(user_Id, list): user_Ids = user_Id
		data = {
		"uids": user_Ids,
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member/invite?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# get online users
	def get_online_members(self, ndc_Id, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/live-layer?topic=ndtopic:x{ndc_Id}:online-members&start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
	
	# get recent users
	def get_recent_members(self, ndc_Id: str, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/user-profile?type=recent&start={start}&size={size}", headers=self.headers)
		return request.json()
	
	# leave chat
	def leave_thread(self, ndc_Id, thread_Id: str):
		request = requests.delete(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member/{self.auid}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# send gif
	def send_gif(self, ndc_Id, thread_Id: str, gif: str):
		image = base64.b64encode(open(gif, "rb").read())
		data = {"type": 0, "clientRefId": 43196704, "timestamp": int(time.time() * 1000), "mediaType": 100, "mediaUploadValue": image.strip().decode(), "mediaUploadValueContentType": "image/gid", "mediaUhqEnabled": False, "attachedObject": None}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/message?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# comment profile
	def comment_profile(self, ndc_Id, content: str, user_Id: str):
		data = {"content": content, "mediaList": [ ], "eventSource": "PostDetailView", "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{user_Id}/comment?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# get from link
	def get_from_link(self, link: str):
		request = requests.get(f"{self.api}/g/s/link-resolution?q={link}", headers=self.headers, proxies=self.proxy)
		return request.json()
	
	# get user blogs
	def get_user_blogs(self, ndc_Id, user_Id: str, start: int = 0, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/blog?type=user&q={user_Id}&start={start}&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# get community info
	def get_community_info(self, ndc_Id: int):
		request = requests.get(f"{self.api}/g/s-x{ndc_Id}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.headers, proxies=self.proxy)
		return request.json()

	# check in
	def check_In(self, ndc_Id:int = 0, tz: int = -int(time.timezone) // 1000):
		data = {"timezone": tz,"timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/check-in?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# send coins to blog
	def send_coins_blog(self, ndc_Id, blog_Id: str = None, coins: int = None, transaction_Id: str = None):
		if transaction_Id is None:	transaction_Id = str(uuid4())
		data = {"coins": coins, "tippingContext": {"transactionId": transaction_Id}, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/blog/{blog_Id}/tipping?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# send coins to thread
	def send_coins_thread(self, ndc_Id, thread_Id: str = None, coins: int = None, transaction_Id: str = None):
		if transaction_Id is None:	transaction_Id = str(uuid4())
		data = {"coins": coins, "tippingContext": {"transactionId": transaction_Id}, "timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/tipping?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	# play lottery
	def lottery(self, ndc_Id, time_zone: str = -int(time.timezone) // 1000):
		data = {
		"timezone": time_zone,
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/check-in/lottery?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# edit chat
	def edit_thread(self, ndc_Id, thread_Id: str, content: str = None, title: str = None, backgroundImage: str = None):
		result = [ ]
		
		if backgroundImage is not None:
			data = {"media": [100, backgroundImage, None], "timestamp": int(time.time() * 1000)}
			data = json.dumps(data)
			ndc_msg_sig = self.generate_signature(data=data)
			self.headers["NDC-MSG-SIG"] = ndc_msg_sig
			request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/member/{self.auid}/background?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
			result.append(request.json())

		data = {"timestamp": int(time.time() * 1000)}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		if content:	data["content"] = content
		if title:   data["title"]   = title
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		result.append(request.json())
		return result
	
	   
	
	# Moder:{ from zakovskiy library

	def moderation_history_community(self, ndc_Id, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/admin/operation?pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def moderation_history_user(self, ndc_Id:int = 0, user_Id: str = None, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/admin/operation?objectId={user_Id}&objectType=0&pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def moderation_history_blog(self, ndc_Id:int = 0, blog_Id: str = None, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/admin/operation?objectId={blog_Id}&objectType=1&pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def moderation_history_quiz(self, ndc_Id:int = 0, quiz_Id: str = None, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/admin/operation?objectId={quiz_Id}&objectType=1&pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def moderation_history_wiki(self, ndc_Id, wiki_Id: str = None, size: int = 25):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/admin/operation?objectId={wiki_Id}&objectType=2&pagingType=t&size={size}&sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def give_curator(self, ndc_Id, user_Id: str):
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{uid}/curator?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def give_leader(self, ndc_Id, user_Id: str):
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{uid}/leader?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# }

	# Bubble:{ from zakovskiy library

	def upload_bubble_1(self, file: str):
		data = open(file, "rb").read()
		request = requests.post(f"{self.api}/g/s/media/upload/target/chat-bubble-thumbnail?sid={self.sid}", data=data, headers=self.headers, lroxies=self.proxy)
		return request.json()

	def upload_bubble_2(self, ndc_Id, template_Id, file: str):
		data = open(file, "rb").read()
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/chat-bubble/{template_Id}?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()

	def generate_bubble(self, ndc_Id, file: str, template_Id: str = "fd95b369-1935-4bc5-b014-e92c45b8e222"):
		data = open(file, "rb").read()
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/chat-bubble/templates/{template_Id}/generate?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	def get_bubble_info(self, ndc_Id, bubble_Id):
		request = requests.get(f"{self.api}/x{ndc_Id}/s/chat/chat-bubble/{bubble_Id}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	def buy_bubble(self, ndc_Id, bubble_Id):
		data = {
		"objectId": bubble_Id,
		"objectType": 116,
		"v": 1,
		"timestamp": int(time.time() * 1000)
		}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/store/purchase?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
		
	# } 
	
	# invite to voice chat
	def invite_to_vc(self, ndc_Id, thread_Id: str, user_Id: str):
		data = {"uid": user_Id}
		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}/vvchat-presenter/invite?sid={self.sid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
	
	# delete thread (chat)
	def delete_thread(self, ndc_Id, thread_Id: str):
		request = requests.delete(f"{self.api}/x{ndc_Id}/s/chat/thread/{thread_Id}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()
    
    # delete notification
	def delete_notification(self, ndc_Id, notification_Id: str):
		request = requests.delete(f"{self.api}/x{ndc_Id}/s/notification/{notificationId}?sid={self.sid}", headers=self.headers, proxies=self.proxy)
		return request.json()

	# clear notifications
	def clear_notifications(self, ndc_Id: int):
		request = requests.delete(f"{self.api}/x{ndc_Id}/s/notification", headers=self.headers, proxies=self.proxy)
		return request.json()

	# edit profile
	def edit_profile(self, ndc_Id, nickname: str = None, content: str = None, chat_request_privilege: str = None, background_color: str = None, titles: list = None, colors: list = None, default_bubble_Id: str = None):
		data = {"timestamp": int(timestamp() * 1000)}
		if nickname:	data["nickname"] = nickname
		elif content:	data["content"] = content
		elif chat_request_privilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		elif background_color: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		elif default_bubble_Id: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		if titles or colors:
			idk_but_list = [ ] # hahahaha variable name
			for titles, colors in zip(titles, colors):
				idk_but_list.append({"title": titles, "color": colors})

			data["extensions"] = {"customTitles": idk_but_list}

		data = json.dumps(data)
		ndc_msg_sig = self.generate_signature(data=data)
		request = requests.post(f"{self.api}/x{ndc_Id}/s/user-profile/{self.auid}", data=data, headers=self.headers, proxies=self.proxy)
		return request.json()
	
	def get_tapjoy_reward(self, user_Id: str = None, repeat: int = 200):
		if not user_Id: user_Id = self.auid
		data = {
		"userId": user_Id,
		"repeat": str(repeat) 
		}
		request = requests.post(f"https://samino.sirlez.repl.co/api/tapjoy", json=data)
		return request.text
