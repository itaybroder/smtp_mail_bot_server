import asyncio
import socket
from aiosmtpd.controller import Controller
from email import message_from_bytes
from firebase_handler import FirebaseHandler

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Check if the email address ends with @darkcheese.org
        if not address.endswith("@darkcheese.org"):
            print("Address does not end with @darkcheese.org")
            return "550 not relaying to that domain"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        print(f"Message from {envelope.mail_from}")
        print(f"Message for {envelope.rcpt_tos}")

        # Decode the email content
        email_message = message_from_bytes(envelope.content)
        subject = email_message["Subject"]
        print(f"Subject: {subject}")

        # Extract the plain text part of the email
        plain_text_part = None
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                plain_text_part = part.get_payload(decode=True).decode("utf-8")
                break

        if plain_text_part:
            print("Plain text content:")
            print(plain_text_part)

        # Prepare the email content for Firebase
        text_lines = [f"> {ln}".strip() for ln in envelope.content.decode("utf8", errors="replace").splitlines()]
        email_content = "\n".join(text_lines)

        # Send the email content to Firebase
        firebase_handler: FirebaseHandler = FirebaseHandler()
        print("[+] Sending to firebase")
        firebase_handler.add_email_to_firebase(sender_email_address=envelope.mail_from,
                                                     recipient_email_address=envelope.rcpt_tos[0],
                                                     message=email_content,
                                                     subject=subject)
        print("[+] Sent to firebase.")

# Get the local IP address
hostname = socket.gethostbyname(socket.gethostname())

# Start the SMTP server
controller = Controller(MailHandler(), hostname=hostname, port=25)
controller.start()
print(f"Server is running on {hostname}:25")
asyncio.get_event_loop().run_forever()