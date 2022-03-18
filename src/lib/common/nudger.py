import re
import logging
import importlib.resources as pkg_resources
from jinja2 import Environment, PackageLoader, select_autoescape
from attendancenudger import _templates as templates
from twilio.rest import Client
from lib.common.gmail_mailer import GmailClient


class Nudger:
    def __init__(self, cfg):
        self.twilio_sms_client = Client(cfg['twilio']['sid'], cfg['twilio']['auth_token'])
        self.twilio_phone_number = cfg['twilio']['phone']

        self.email_client = GmailClient()

        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized {__name__}")
        self.cfg = cfg
        self.jinja_env = Environment(
            loader=PackageLoader('attendancenudger', '_templates'),
            autoescape=select_autoescape(['html'])
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
            avg_att_dict = {'class_avg_attendance': avg_att, 'weekly_class_avg_attendance': weekly_avg_att}
            dict_in.update(avg_att_dict)
            message = self.twilio_sms_client.messages.create(
                body=self.render(dict_in, sms_template.read()),
                from_=self.twilio_phone_number,
                to=dict_in['phone']
            )
        return message.sid

    def send_email(self, dict_in, avg_att, weekly_avg_att):
        self.logger.debug(f"Sending email to {dict_in['name']} at {dict_in['email']}")
        with pkg_resources.open_text(templates, 'attendance.html') as html_template:
            with pkg_resources.open_text(templates, 'attendance.txt') as plaintext_template:
                avg_att_dict = {'class_avg_attendance': avg_att, 'weekly_class_avg_attendance': weekly_avg_att}
                dict_in.update(avg_att_dict)
                _to = dict_in['email']
                _from = "me"  # special string used when sending via gmail
                _subject = "Weekly Attendance Report -- Mind The Gap"
                _html = self.render(dict_in, html_template.read())

                msg = self.email_client.create_message(_from, _to, _subject, _html)
                self.email_client.send_message(_from, msg)

    def send_logs(self, log):
        _to = self.cfg['author']['email']
        _from = "me"
        _subject = "Ahoy! Log files for you."
        _body = "Please see the attached log file. \n\n Thank you."
        _file = log

        msg = self.email_client.create_message_with_attachment(_from, _to, _subject, _body, _file)
        self.email_client.send_message(_from, msg)
