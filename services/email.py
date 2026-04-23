import resend
from settings import settings
from schemas import EmailSchema

resend.api_key = settings.RESEND_API_KEY.get_secret_value()

# Function to send an email using Resend API
def send_email(email: EmailSchema):
    params:resend.Email.SendParams = ({
        "from": "onboarding@resend.dev",
        "to": email.to,
        "subject": email.subject,
        "html": email.html
    })

    response: resend.Emails.SendResponse = resend.Emails.send(params)
    return response

# Function to send password reset email
def password_reset_email(to_email: str, reset_link: str):
    email = EmailSchema(
        to=[to_email],
        subject="Password Reset Request",
        html=f"""
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        <p>If you did not request this, please ignore this email.</p>
        """
    )
    return send_email(email)