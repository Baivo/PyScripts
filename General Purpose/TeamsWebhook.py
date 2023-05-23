import requests
import json
import os

def send_teams_message(title, body):
    # This is needed to get around self signed cert SSL errors. You may need to provide your own.
    cert_path = os.path.join(os.getcwd(), 'cert.pem')
    os.environ["REQUESTS_CA_BUNDLE"] = cert_path
    os.environ["SSL_CERT_FILE"] = cert_path

    # Teams webhook URL
    #webhook_url = "https://outlook.office.com/webhook/..."  

    # Message card
    message_card = {
        "@context": "https://schema.org/extensions",
        "@type": "MessageCard",
        "title": title,
        "text": "<pre>" + body + "</pre>",
        "contentType": "text/html"
    }
    # Send the message card
    response = requests.post(
        webhook_url,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(message_card)
    )

    # Print the response
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code}, {response.text}")

# Call the function
send_teams_message("Hello, World!", ["This is the first line of the body.", "This is the second line of the body."])
