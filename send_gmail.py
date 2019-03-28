#!/usr/bin/env python3
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import os
import base64
import mimetypes

from apiclient import errors

class gmail:
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        #SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        self.SCOPES = 'https://www.googleapis.com/auth/gmail.send'

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,'token.json')
        store = file.Storage(credential_path)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', self.SCOPES)
            creds = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return creds

    def SendMessage(self, sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
        credentials = self.get_credentials()
        http = credentials.authorize(Http())
        service = build('gmail', 'v1', http=http)
        if attachmentFile:
            message1 = self.createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
        else: 
            message1 = self.CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
        result = self.SendMessageInternal(service, "me", message1)
        return result

    def SendMessageInternal(self, service, user_id, message):
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"
        return "OK"

    def CreateMessageHtml(self, sender, to, subject, msgHtml, msgPlain):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg.attach(MIMEText(msgPlain, 'plain'))
        msg.attach(MIMEText(msgHtml, 'html'))
        #return {'raw': base64.urlsafe_b64encode(msg.as_string())}
        return {'raw': base64.urlsafe_b64encode(bytes(msg.as_string(),'UTF-8')).decode('ascii')}

    def createMessageWithAttachment(
        self, sender, to, subject, msgHtml, msgPlain, attachmentFile):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          msgHtml: Html message to be sent
          msgPlain: Alternative plain text message for older email clients          
          attachmentFile: The path to the file to be attached.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEMultipart('mixed')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        messageA = MIMEMultipart('alternative')
        messageR = MIMEMultipart('related')

        messageR.attach(MIMEText(msgHtml, 'html'))
        messageA.attach(MIMEText(msgPlain, 'plain'))
        messageA.attach(messageR)

        message.attach(messageA)

        print("create_message_with_attachment: file: %s" % attachmentFile)
        content_type, encoding = mimetypes.guess_type(attachmentFile)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(attachmentFile, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(attachmentFile, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(attachmentFile, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(attachmentFile, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(attachmentFile)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        #return {'raw': base64.urlsafe_b64encode(message.as_string())}
        return {'raw': base64.urlsafe_b64encode(bytes(message.as_string(),'UTF-8')).decode('ascii')}

if __name__ == '__main__':
    to = "TTTT@gmail.com"
    sender = "SSSS@gmail.com"
    subject = "test"
    url = "https://www.google.com.tw/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
    msgHtml = 'Hi<br/>Html Email<br><img src="{}" width="480" border="0">'.format(url)
    msgPlain = "Hi\nPlain Email"
    gmail().SendMessage(sender, to, subject, msgHtml, msgPlain)
    # Send message with attachment: 
    #SendMessage(sender, to, subject, msgHtml, msgPlain, '/path/to/file.pdf')
