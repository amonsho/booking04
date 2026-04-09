from sib_api_v3_sdk import TransactionalEmailsApi, ApiClient, Configuration
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailSender
from app.core.config import settings

class EmailService:
    def __init__(self):
        configuration = Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_client = ApiClient(configuration)
        self.client = TransactionalEmailsApi(api_client)

    def send_email(self, to_email: str, subject: str, html_content: str):
        sender = SendSmtpEmailSender(
            name="Booking",
            email=settings.EMAIL_FROM
        )

        email = SendSmtpEmail(
            to=[{"email": to_email}],
            sender=sender,
            subject=subject,
            html_content=html_content
        )

        try:
            self.client.send_transac_email(email)
        except Exception as e:
            print(f"Error sending email: {e}")




# from sib_api_v3_sdk import TransactionalEmailsApi
# from sib_api_v3_sdk.rest import ApiException
# from sib_api_v3_sdk.models import SendSmtpEmail
# from sib_api_v3_sdk import ApiClient, Configuration
# from app.core.config import settings

# class EmailService:
#     def __init__(self):
#         # Настройка API клиента Brevo
#         configuration = Configuration()
#         configuration.api_key['api-key'] = settings.BREVO_API_KEY
#         api_client = ApiClient(configuration)
#         self.client = TransactionalEmailsApi(api_client)

#     def send_email(self, to_email: str, subject: str, html_content: str):
#         """
#         Отправка письма через Brevo (синхронно)
#         """
#         email = SendSmtpEmail(
#             to=[{"email": to_email}],
#             sender={"email": settings.EMAIL_FROM, "name" : "Booking"},
#             subject=subject,
#             html_content=html_content,
#         )
#         try:
#             self.client.send_transac_email(email)
#         except ApiException as e:
#             print(f"Error sending email: {e}")