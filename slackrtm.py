from slackclient import SlackClient
import json
import time

class SlackRTM():
    ''' A simple wrapper to handle slack rtm. 
        For now, only support recieving and sending (rich) message.
    '''
    def __init__(self, token, name):
        self.sc = SlackClient(token)
        self.name = name
        self.states = {}
        self.set_handle() # set message_hadle to None
        # get users info, map user ID to user name
        self.users = {}
        user_list = self.sc.api_call('users.list', token=token)
        if user_list.get('ok', False):
            for info in user_list['members']:
                self.users[info['id']] = info['name']
                if self.name == info['name']:
                    self.id = info['id']

    def set_handle(self, func=None):
        ''' func: take user ID and text as input, 
            return message to be sent back
            @ user state: dict
            @ user name: string
            @ text: string
            * new state: dict
            * message: string
            * attachments: list
                - detail: https://api.slack.com/docs/formatting
        '''
        self.message_handle = func
    
    def event_handle(self, event):
        ''' Handle a 'message' event: https://api.slack.com/events/message
        '''
        if event.get('type', '') == 'message':
            userID = event.get('user', '')
            channel = event.get('channel', '')
            text = event.get('text', '')
            state = self.states.get('userID', {})
            if userID == self.id: 
                # do nothing if the message comes from this bot
                return
            else:
                new_state, text, attachments = self.message_handle(
                        state, self.users[userID], text)
                message = { 
                    'channel': channel,
                    'as_user': True,
                    'text': text,
                    'attachments': json.dumps(attachments)
                }
                self.states[userID] = new_state
                chat = self.sc.api_call('chat.postMessage', **message)
                return


    def run(self):
        if self.sc.rtm_connect():
            while True:
                for event in self.sc.rtm_read():
                    self.event_handle(event)
                time.sleep(0.01)
        else:
            print("Connection Failed, invalid token?")

# unit testing
if __name__ == '__main__':
    token = "xoxb-33294948947-fgl7KVmPgdtIGtLYqiWHJs3l"
    rtm = SlackRTM(token, 'myfirstbot')
    def copycat(state, user, text):
        return {}, '<@'+user+'>: '+text, []
    rtm.set_handle(copycat)
    rtm.run()
