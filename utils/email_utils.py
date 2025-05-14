import smtplib
import ssl
from email.message import EmailMessage
import requests

def create_ethereal_account():
    payload = {
        "requestor": "test@example.com",  # You can use any email here for dev/testing
        "version": "1.0"
    }
    resp = requests.post('https://api.nodemailer.com/user', json=payload)
    try:
        data = resp.json()
    except Exception as e:
        print("Failed to parse Ethereal response:", resp.text)
        raise
    if 'user' not in data:
        print("Ethereal API error:", data)
        raise Exception(f"Ethereal API error: {data}")
    return data['user'], data['pass'], data['smtp']['host'], data['smtp']['port']

def send_verification_email(to_email, code):
    user, password, smtp_host, smtp_port = create_ethereal_account()
    msg = EmailMessage()
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = user
    msg['To'] = to_email
    msg.set_content(f'Your verification code is: {code}')

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls(context=context)
        server.login(user, password)
        response = server.send_message(msg)
        # The message ID is in the response dict, key is the recipient email
        message_id = response.get(to_email)
    print(f"Preview URL: https://ethereal.email/message/{message_id}") 