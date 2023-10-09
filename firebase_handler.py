import firebase_admin
from firebase_admin import credentials, db


class FirebaseHandler:
    instance = None
    ref = None

    def __new__(cls):
        if cls.instance is None:
            service_account_info = credentials.Certificate("serviceAccountKey.json")

            firebase_admin.initialize_app(service_account_info, {
                'databaseURL': 'https://botnet-5fb37-default-rtdb.firebaseio.com/'
            })
            FirebaseHandler.ref = db.reference('/')
            cls.instance = super(FirebaseHandler, cls).__new__(cls)
        return cls.instance

    def add_email_to_firebase(self, sender_email_address: str, recipient_email_address: str, message: str
                              , subject: str):
        """sender_mail_address - string, recipient_email_address - string , message - string,
         subject - string will be uploaded to the firebase server"""

        data_to_write = {
            'Sender': sender_email_address,
            'Recipient': recipient_email_address,
            'Content': message,
            'Subject': subject
        }

        FirebaseHandler.ref.child("mailboxes").child(recipient_email_address.split("@")[0]).set(data_to_write)
        print("[+] Data written to Firebase.")