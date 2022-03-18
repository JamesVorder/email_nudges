import base64
import os.path
import logging
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailClient(object):

    def __init__(self):

        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized {__name__}")

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        config_path = os.path.join(os.path.dirname(__file__), '../../config')
        token_location = os.path.join(config_path, 'token.json')
        creds_location = os.path.join(config_path, 'credentials.json')

        if os.path.exists(token_location):
            creds = Credentials.from_authorized_user_file(token_location, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_location, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_location, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)

        except HttpError as error:
            self.logger.debug(f'An error occurred: {error}')

    def create_message(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text, 'html')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}

    def create_message_with_attachment(self, sender, to, subject, message_text, file):
            """Create a message for an email.

            Args:
              sender: Email address of the sender.
              to: Email address of the receiver.
              subject: The subject of the email message.
              message_text: The text of the email message.
              file: The path to the file to be attached.

            Returns:
              An object containing a base64url encoded email object.
            """
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = sender
            message['subject'] = subject

            msg = MIMEText(message_text)
            message.attach(msg)

            fp = open(file, 'rb')
            msg = MIMEBase('application', 'octet-stream')
            msg.set_payload(fp.read())
            fp.close()

            filename = os.path.basename(file)
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)

            raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
            return {'raw': raw_message.decode('utf-8')}

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message).execute())
            self.logger.debug(f'Message Id: {message["id"]}')
            return message

        except HttpError as error:
            self.logger.debug(f'An error occurred: {error}')