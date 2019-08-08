import jinja2 as jinja
from twilio.rest import Client

class Nudger:
    def __init__(self, twilio_account_sid, twilio_auth_token, twilio_phone_number):
        self.twilio_sms_client = Client(twilio_account_sid, twilio_auth_token)
        self.twilio_phone_number = twilio_phone_number

    def render(self, dict_in, template):
        return jinja.Template(template).render(dict_in)

    def send_text(self, dict_in, avg_att):
        with open(f'_templates/attendance.txt', 'r') as sms_template:
            avg_att_dict = {'class_avg_attendance': avg_att}
            dict_in.update(avg_att_dict)
            #print(self.render(dict_in, sms_template.read()))
            message = self.twilio_sms_client.messages.create(body=self.render(dict_in, sms_template.read()), \
                    from_=self.twilio_phone_number, \
                    to=dict_in['phone'])
        return message.sid
    
