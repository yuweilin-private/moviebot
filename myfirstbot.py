from slackclient import SlackClient
import json

token = "xoxb-33294948947-fgl7KVmPgdtIGtLYqiWHJs3l"
sc = SlackClient(token)
if sc.rtm_connect():
    message = { "as_user": True,
                "text": "TEST1:",
                "attachments": json.dumps([{
                    "title": "App hangs on reboot",
                    "title_link": "http://domain.com/ticket/123456",
                    "text": "If I restart my computer without quitting your app, it stops the reboot sequence.\nhttp://domain.com/ticket/123456"
                }]),
    }
    sc.api_call("chat.postMessage", channel="#yuwei", **message)
    
    while True:
        in_events = sc.rtm_read()
        for event in in_events:
            if 'type' in event:
                if event['type'] == 'message':
                    channel, message = event['channel'], event['text']
                    print(channel, message)
                    sc.rtm_send_message(channel=channel, message=message)
    
else:
    print("Connection Failed, invalid token?")

