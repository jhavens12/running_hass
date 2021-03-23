from pushover import Client #pip install python-pushover
import credentials

client = Client(credentials.push_id, api_token=credentials.push_token)
def notify(title,body,pri):

    client.send_message(body, title=title, priority=pri)
