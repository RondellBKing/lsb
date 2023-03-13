import base64
import logging
import os
import os.path
from pathlib import Path
import pickle
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors
from googleapiclient.discovery import build


def get_service():
    """Gets an authorized Gmail API service instance.

    Returns:
        An authorized Gmail API service instance..
    """    

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
    ]

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            parent_dir = os.fspath(Path(__file__).resolve().parents[1].resolve()) # Relative to point of execution
            secret_loc = os.path.join(parent_dir, 'local', 'client_secrets.json')

            flow = InstalledAppFlow.from_client_secrets_file(secret_loc, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message(service, sender, message):
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
    sent_message = (service.users().messages().send(userId=sender, body=message)
               .execute())
    logging.info('Message Id: %s', sent_message['id'])
    return sent_message
  except errors.HttpError as error:
    logging.error('An HTTP error occurred: %s', error)

def create_message(sender, to, subject, message_text, attachment=None):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEMultipart() #MIMEText(message_text, 'html')
  # attach the body with the msg instance
  message.attach(MIMEText(message_text, 'html')) 

  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  s = message.as_string()
  b = base64.urlsafe_b64encode(s.encode('utf-8'))

  myFile=open(attachment, "rb")

  # attach the body with the msg instance
  # message.attach(MIMEText(b, 'plain'))
  p = MIMEBase('application', 'octet-stream')

  # To change the payload into encoded form
  p.set_payload((myFile).read())
  # encoders.encode_base64(p)
    
  p.add_header('Content-Disposition', "attachment; filename= %s" % attachment)
    
  # attach the instance 'p' to instance 'msg'
  # message.attach(b)
  message.attach(p)

  # raw = encoders.encode_base64(message)
          # encoded message
  encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

  create_message = {
      'raw': encoded_message
  }
  # text = message.as_string()
  return  create_message

def send_mail(recipient, subject, message, sender="kingstack08@gmail.com", filename=None):

  try:
      service = get_service()
      message = create_message(sender, recipient, subject, message, filename)
      send_message(service, sender, message)

  except Exception as e:
      logging.error(e)
      raise

if __name__ == '__main__':
  send_mail("kingstack08@gmail.com","Test subject", "Test body","kingstack08@gmail.com",'/Users/rondellking/PycharmProjects/lsb/lsb-v2/lsb/temp/san_francisco_01162023.csv')
