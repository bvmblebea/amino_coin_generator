import AminoLab, secmail, os
import names, requests, time
from bs4 import BeautifulSoup

def device_Id_generator():
	try:	return requests.get("https://aminohub.sirlez.repl.co/deviceId").text
	except:	device_Id_generator()
	
def get_verification_link(mail: str, email: str):
	time.sleep(2.50)
	inbox = mail.get_messages(email=email).id
	verify_messageId = inbox[0]
	readed_message = mail.read_message(email, verify_messageId).htmlBody
	beautiful_soup = BeautifulSoup(readed_message, "html.parser")
	quotes = beautiful_soup.find_all("a"); verification_link = quotes[0].get("href")
	os.system(f"termux-open-url {verification_link}")
	print(f"Verification Link >> {verification_link}")
	
def auto_register(password: str):
	while True:
		device_Id = device_Id_generator()
		client = AminoLab.Client(device_Id=device_Id)
		sec_mail = secmail.SecMail()
		email = sec_mail.generate_email()
		nickname = names.get_last_name()
		print(f"Email >> {email}, \nPassword >> {password}, \ndeviceID >> {device_Id}")
		try:
			client.request_security_validation(email=email)
			get_verification_link(sec_mail, email)
			verification_code = input("Verification Code >> ")
			print(client.register(email=email, password=password, nickname=nickname, verification_code=verification_code))
		except Exception as e:
			print(e)
			return
