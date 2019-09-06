import re
import jinja2 as jinja
from jinja2 import Environment, PackageLoader, select_autoescape
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import importlib.resources as pkg_resources
from attendancenudger import _templates as templates
import logging

class Nudger:
    def __init__(self, cfg, email_server=None):
        self.twilio_sms_client = Client(cfg['twilio']['sid'], cfg['twilio']['auth_token'])
        self.twilio_phone_number = cfg['twilio']['phone']
        self.email_server = email_server
        self.email = cfg['gmail']['email']
        self.email_pass = cfg['gmail']['pass']
        if self.email_server:
            self.email_server.login(self.email,self.email_pass)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized {__name__}")
        self.cfg = cfg
        self.jinja_env = Environment(
            loader = PackageLoader('attendancenudger', '_templates'),
            autoescape = select_autoescape(['html'])
        )
        def firstname(name):
            return re.sub('.*,', '', name, count=1)
        self.jinja_env.filters['firstname'] = firstname

    def render(self, dict_in, template):
        self.logger.debug(f"Rendering jinja template, {template}.")
        return self.jinja_env.from_string(template).render(dict_in)

    def send_text(self, dict_in, avg_att, weekly_avg_att):
        self.logger.debug("Sending text to {dict_in['name']} at {dict_in['phone']}")
        with pkg_resources.open_text(templates, 'attendance.txt') as sms_template:
            avg_att_dict = { 'class_avg_attendance': avg_att, 'weekly_class_avg_attendance': weekly_avg_att }
            dict_in.update(avg_att_dict) 
            message = self.twilio_sms_client.messages.create(body=self.render(dict_in, sms_template.read()), \
                    from_=self.twilio_phone_number, \
                    to=dict_in['phone'])
        return message.sid

    def send_email(self, dict_in, avg_att, weekly_avg_att):
        self.logger.debug("Sending email to {dict_in['name']} at {dict_in['email']}")
        with pkg_resources.open_text(templates, 'attendance.html') as html_template:
            with pkg_resources.open_text(templates, 'attendance.txt') as plaintext_template:
                avg_att_dict = { 'class_avg_attendance': avg_att, 'weekly_class_avg_attendance': weekly_avg_att }
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

    def send_logs(self, log):
        self.logger.debug("Sending logs to {self.cfg['author']['email']}.")
        _to = self.cfg['author']['email']
        _from = self.email

        msg = MIMEMultipart()
        msg['Subject'] = "Ahoy! Log files for you."
        msg['From'] = _from
        msg['To'] = _to

        _body = "Please see the attached log file. \n\n Thank you."
        msg.attach(MIMEText(_body))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(log)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="debug.log"')
        msg.attach(part)

        self.email_server.sendmail(_from, _to, msg.as_string())
    
