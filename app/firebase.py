import firebase_admin
from firebase_admin import credentials, messaging, storage
from pathlib import Path

pathToCred = "../firebase/tdp-ii-grupo-5-2022-2c-firebase-adminsdk-f71fl-bfacf0ba84.json"
base_path = Path(__file__).parent
file_path = (base_path / pathToCred).resolve()

cred = credentials.Certificate(
    file_path
)
firebaseApp = firebase_admin.initialize_app(
    cred,
    {'storageBucket': 'tdp-ii-grupo-5-2022-2c.appspot.com'})


def sendPush(title: str, description: str, fcmToken: str):
    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=description),
        token=fcmToken,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)


def uploadFile(filePath: str):
    # Put your local file path
    bucket = storage.bucket()
    blob = bucket.blob(filePath)
    blob.upload_from_filename(filePath)

    blob.make_public()
