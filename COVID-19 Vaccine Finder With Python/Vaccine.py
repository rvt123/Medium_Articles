import requests
import datetime as dt
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

STATE_ID = 9
DISTRICT_CODE_LIST = [143,146]
PINCODE_CODE_LIST = [110039]
VACCINE_TYPE = 'COVISHIELD' # 'COVAXIN' 'COVISHIELD'
MIN_AGE = 18 # 45
FEE_TYPE = 'Free' #  'Paid' 'Free'
DATE = None # 12-06-2021
if DATE is None:
    date_tody = dt.datetime.now().date()
    DATE = date_tody.strftime('%d-%m-%Y')

HEADER = {'accept': 'application/json',
 'Accept-Language': 'hi_IN',
 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}

APPOINTMENT_BASE_URL_DISTRICT = '''https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={entity}&date={date}'''
APPOINTMENT_BASE_URL_PINCODE = '''https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={entity}&date={date}'''

T_API = '<Inset your own Telegram Bot token here >'
T_CHAT_ID = [<Telegram_chat_id>,eg. 123456]
URL = '''https://api.telegram.org/bot{T_API}/sendMessage?chat_id={T_CHAT_ID}&text='''


def TeleGram_Notify(URL,message):
    now = dt.datetime.now()
    if (now.hour >= 12):
        ampm_tag = 'pm'
        hour = now.hour - 12
    else:
        ampm_tag = 'am'
        hour = now.hour
    MSG = str(hour) + ':' + str(now.minute) + ' ' + ampm_tag +'\n' + message
#         print(MSG)
    MSG = MSG.replace(' ','%20')
    MSG = MSG.replace('#','%23')
    try:
        response = requests.get(URL + MSG, timeout=10)
        print("Message Sent")
        return True
    except:
        print("Message could not be sent")
        return False

def find_vaccine(mode):
    DATA_LIST = []
    MESSAGE = ''
    if mode == 'DISTRICT':
        entity_list = DISTRICT_CODE_LIST
        url = APPOINTMENT_BASE_URL_DISTRICT
    elif mode == 'PINCODE':
        entity_list = PINCODE_CODE_LIST
        url = APPOINTMENT_BASE_URL_PINCODE
    else:
        return False
    for entity_ in entity_list:
        app_url = url.format(entity=entity_,date=DATE)
        data = requests.get(app_url,headers=HEADER)
        if data.status_code == 200:
            data = eval(data.content.decode().replace('true','True'))
            DATA_LIST = DATA_LIST + data['centers']
    if len(DATA_LIST) > 0:
        for center in DATA_LIST:
            if center['fee_type'] == FEE_TYPE:
                for session in center['sessions']:
                    if (session['min_age_limit'] == MIN_AGE) & (session['vaccine']==VACCINE_TYPE) & \
                    (session['available_capacity'] >0 ) & (session['available_capacity_dose1'] >0 ) :
                        message = '''{pincode}  {quantity}  {date} \n{center_name} \n{center_address}\n****\n'''.format(pincode=str(center['pincode']),
                            quantity=str(session['available_capacity']), date=session['date'], center_name=center['name'],
                                                    center_address=center['address'] )
                        MESSAGE+= message
    print(MESSAGE)
    if len(MESSAGE) > 0:
        for chat in T_CHAT_ID:
            url = URL.format(T_API=T_API,T_CHAT_ID=chat)
            TeleGram_Notify(url,MESSAGE)

sched = BlockingScheduler()
sched.add_job(find_vaccine, 'interval',args=['PINCODE'], seconds = 30)
# sched.add_job(find_vaccine, 'interval',args=['DISTRICT'], seconds = 30)

# sched.add_job(find_vaccine, "cron", ['PINCODE'], second="*/30")
# sched.add_job(find_vaccine, "cron", ['DISTRICT'], second="*/30")
sched.start()
