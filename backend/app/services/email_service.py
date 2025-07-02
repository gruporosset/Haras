from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from app.core.config import settings
from fastapi import HTTPException


class EmailService:
    def __init__(self):
        self.smtp_host = settings.MAIL_HOST
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.smtp_port = settings.MAIL_PORT
        self.from_email = settings.MAIL_FROM_ADDRESS
        self.use_tls = False
        self.start_tls = True

    async def send_email(
        self, to_email: str, subject: str, body: str, is_html: bool = False
    ):
        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject

        if is_html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
                start_tls=self.start_tls,
            ) as smtp:
                await smtp.send_message(message)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}"
            ) from e

    async def send_template_email(
        self, to_email: str, subject: str, template_name: str, context: dict
    ):
        template_path = (
            Path(__file__).parent.parent / "templates" / "email" / template_name
        )
        try:
            with open(template_path, "r", encoding="utf-8") as template_file:
                template_content = template_file.read()
            body = template_content.format(**context)
            await self.send_email(to_email, subject, body)
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=500, detail=f"Template {template_name} não encontrado"
            ) from e
