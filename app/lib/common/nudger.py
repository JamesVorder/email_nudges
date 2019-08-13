import jinja2 as jinja
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Nudger:
    def __init__(self, cfg, email_server=None):
        self.twilio_sms_client = Client(cfg['twilio']['sid'], cfg['twilio']['auth_token'])
        self.twilio_phone_number = cfg['twilio']['phone']
        self.email_server = email_server
        self.email = cfg['gmail']['email']
        self.email_pass = cfg['gmail']['pass']
        if self.email_server:
            self.email_server.login(self.email,self.email_pass)

    def render(self, dict_in, template):
        return jinja.Template(template).render(dict_in)

    def send_text(self, dict_in, avg_att):
        with open(f'_templates/attendance.txt', 'r') as sms_template:
            avg_att_dict = {'class_avg_attendance': avg_att}
            dict_in.update(avg_att_dict) 
            message = self.twilio_sms_client.messages.create(body=self.render(dict_in, sms_template.read()), \
                    from_=self.twilio_phone_number, \
                    to=dict_in['phone'])
        return message.sid

    def send_email(self, dict_in, avg_att):
        with open(f'_templates/attendance.html', 'r') as html_template:
            with open(f'_templates/attendance.txt', 'r') as plaintext_template:
                avg_att_dict = {'class_avg_attendance': avg_att}
                dict_in.update(avg_att_dict)
                _to = dict_in['email']
                _from = self.email

                msg = MIMEMultipart('alternative')
                msg['Subject'] = "Weekly Attendance Report -- Mind The Gap"
                msg['From'] = _from
                msg['To'] = _to

                text = self.render(dict_in, plaintext_template.read())
                html = self.render(dict_in, html_template.read())
                
                part1 = MIMEText(text, 'plain')
                part2 = MIMEText(html, 'html')

                msg.attach(part1)
                msg.attach(part2)

                self.email_server.sendmail(_from, _to, msg.as_string()) 
        return 1
    
