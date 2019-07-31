from twilio.rest import Client

class Nudger:
    def __init__(self, twilio_account_sid, twilio_auth_token, twilio_phone_number):
        self.twilio_sms_client = Client(twilio_account_sid, twilio_auth_token)
        self.twilio_phone_number = twilio_phone_number

    def send_text(self, to_student, message):
        message = self.twilio_sms_client.messages.create(body=message, from_=self.twilio_phone_number, to=to_student.phone_number)
        return message.sid
