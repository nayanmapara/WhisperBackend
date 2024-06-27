from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(smtp_config, to_email, subject, html_content):
    """
    Send an email using SMTP with the given configuration.

    Args:
    - smtp_config (dict): Dictionary containing SMTP configuration parameters:
        - 'host': SMTP server host address
        - 'port': SMTP server port number
        - 'user': SMTP username
        - 'password': SMTP password
    - to_email (str): Recipient email address
    - subject (str): Email subject
    - html_content (str): HTML content of the email body

    Returns:
    - bool: True if email was sent successfully, False otherwise.
    """
    
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_config['user']
    msg['To'] = to_email
    msg['Subject'] = subject

    part = MIMEText(html_content, 'html') # Create a MIMEText object with the HTML content
    msg.attach(part) # Attach the MIMEText object to the MIMEMultipart object

    try:
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls() # Enable TLS
            server.login(smtp_config['user'], smtp_config['password'])
            server.sendmail(smtp_config['user'], to_email, msg.as_string()) # Send the email
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

