import requests
import base64
import json
import datetime
import sys
import time

class Heroku():
    """
    Connect with Heroku to scale dynos
    """
    def __init__(self):
        self.APP = "<heroku_app_name>"
        self.KEY = "<Heroku_api_key>"
        self.PROCESS = "clock"
        self.BASEKEY = None
        self.HEADERS = None
        self.T_API = '<Telegram_bot_token>'
        self.T_CHAT_ID = "<Telegram_chat_id>"
        self.URL = "https://api.telegram.org/bot" + self.T_API + \
                "/sendMessage?chat_id=" + self.T_CHAT_ID + "&text="
        self.generate_basekey()

    def generate_basekey(self):
        data = ":" + self.KEY
        encodedBytes = base64.b64encode(data.encode("utf-8"))
        self.BASEKEY = str(encodedBytes, "utf-8")
        self.HEADERS = {"Accept": "application/vnd.heroku+json; version=3",
                        "Authorization": self.BASEKEY}

    def get_current_dyno_quantity_notify(self):
        if self.HEADERS is None :
            self.generate_basekey()
        url = "https://api.heroku.com/apps/" + self.APP + "/formation"
        try:
            result = requests.get(url, headers=self.HEADERS)
            for formation in json.loads(result.text):
                current_quantity = formation["quantity"]
                self.TeleGram_Notify("Current dyno quantity is " + str(current_quantity) )
                return current_quantity
        except:
            self.TeleGram_Notify("Current dyno quantity is Error Encountered")
            return False

    def get_current_dyno_quantity(self):
        if self.HEADERS is None :
            self.generate_basekey()
        url = "https://api.heroku.com/apps/" + self.APP + "/formation"
        try:
            result = requests.get(url, headers=self.HEADERS)
            for formation in json.loads(result.text):
                current_quantity = formation["quantity"]
                return current_quantity
        except:
            return False

    def scale(self,size):
        if self.HEADERS is None :
            self.generate_basekey()
        payload = {'quantity': size}
        json_payload = json.dumps(payload)
        url = "https://api.heroku.com/apps/" + self.APP + "/formation/" + self.PROCESS
        try:
            result = requests.patch(url, headers=self.HEADERS, data=json_payload)
        except:
            print("Error Encountered")
            self.TeleGram_Notify("Dyno Scaling could not be done ")
            self.get_current_dyno_quantity()
            return False
        if result.status_code == 200:
            self.TeleGram_Notify("Dyno quantity scaled to " + str(size) )
            self.get_current_dyno_quantity()
            return True
        else:
            self.TeleGram_Notify("Dyno Scaling could not be done ")
            self.get_current_dyno_quantity()
            return False

    def restart(self):
        if self.HEADERS is None :
            self.generate_basekey()
        url = 'https://api.heroku.com/apps/' + self.APP + '/dynos'
        try:
            result = requests.delete(url,headers=self.HEADERS)
        except:
            print("Error Encountered")
            self.TeleGram_Notify("Dyno Could not be restarted ")
            self.get_current_dyno_quantity()
            return False
        if result.status_code == 202:
            self.TeleGram_Notify("Dyno restarted" )
            self.get_current_dyno_quantity()
            return True
        else:
            self.TeleGram_Notify("Dyno Could not be restarted ")
            self.get_current_dyno_quantity()
            return False

    def TeleGram_Notify(self,message):
        now = datetime.datetime.now()
        if (now.hour >= 12):
            ampm_tag = 'pm'
            hour = now.hour - 12
        else:
            ampm_tag = 'am'
            hour = now.hour
        MSG = str(hour) + ':' + str(now.minute) + ampm_tag + ' ' + message
#         print(MSG)
        MSG = MSG.replace(' ','%20')
        MSG = MSG.replace('#','%23')
        try:
            response = requests.get(self.URL + MSG, timeout=10)
#             print("Message Sent")
        except:
            print("Message could not be sent")


# heroku = Heroku()
# heroku.get_current_dyno_quantity()
# heroku.scale(0)
# heroku.scale(1)
