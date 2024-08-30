import time
import sys
import os.path
import base64
import requests
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def list_messages(service, user_id='me', label_ids=['INBOX']):
    try:
        response = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_message(service, user_id='me', msg_id=None):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        payload = message.get('payload')
        headers = payload.get('headers')
        parts = payload.get('parts')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown')
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        text_content, html_content = None, None
        if parts:
            for part in parts:
                mime_type = part.get('mimeType')
                data = part.get('body', {}).get('data')
                if mime_type == 'text/plain' and data:
                    text_content = base64.urlsafe_b64decode(data).decode('utf-8')
                elif mime_type == 'text/html' and data:
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
        email_body = html_content if html_content else text_content

        return sender, subject, email_body
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None, None, None

def extract_verification_code(email_body):
    return email_body.split()[0]

known_message_ids = set()
def track_new_emails(service):
    messages = list_messages(service)
    for message in messages:
        msg_id = message['id']
        if msg_id not in known_message_ids:
            known_message_ids.add(msg_id)
            sender, subject, _ = get_message(service, msg_id=msg_id)
            if sender == "Twitch <no-reply@twitch.tv>":
                return int(extract_verification_code(subject))

def reg_account(username, email, gmail_service):
    profile_id = "428954891"
    response = requests.get("http://localhost:3001/v1.0/browser_profiles/"+profile_id+"/start?automation=1").json()
    driver_path = Service("/Users/timstellar/Documents/Programming/Twitch/chromedriver")
    port = str(response['automation']['port'])
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:" + port
    driver = webdriver.Chrome(service=driver_path, options=options)

    password = 'bvq+"YMz)L/3K$'
    driver.get("https://www.twitch.tv/signup")
    time.sleep(1)

    el = driver.find_element("id", "signup-username")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .send_keys(username)\
                .perform()
    time.sleep(1.1)

    el = driver.find_element("id", "password-input")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .send_keys(password)\
                .perform()
    time.sleep(2)

    el = driver.find_element("xpath", "//*[contains(@class, 'cNKHwD')]/div")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .send_keys("1")\
                .perform()
    time.sleep(1.5)

    sel = driver.find_element("xpath", "//*[contains(@class, 'cNKHwD')]/div[contains(@class, 'jPmKIH')]/div/select")
    select = Select(sel)
    time.sleep(1.23)
    select.select_by_value('1')
    time.sleep(2.1)

    el = driver.find_element("xpath", "//*[contains(@class, 'cNKHwD')]/div[contains(@class, 'birthday-picker__input kFGaik')]")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .send_keys("2000")\
                .perform()
    time.sleep(1.3)

    el = driver.find_element("xpath", "//*[contains(@class, 'ScCoreButtonText-sc-ocjdkq-3')]")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .perform()
    time.sleep(1.4)

    el = driver.find_element("id", "email-input")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .send_keys(email)\
                .perform()
    time.sleep(2.15);

    isValidUsername = True

    while isValidUsername:
        try:
            driver.find_element("xpath", "//*[contains(@class, 'kfKMUE')]")
            isValidUsername = True
            element = driver.find_element("id", "signup-username")
            m = str(random.randint(0, 10))
            username = str(username) + str(m)
            ActionChains(driver=driver, duration=20)\
                    .move_to_element(element)\
                    .click(element)\
                    .send_keys(m)\
                    .perform()
            time.sleep(3)
        except:
            isValidUsername = False
            time.sleep(2)
            
    el = driver.find_element("css selector", ".gmCwLG")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .perform()
    time.sleep(10);
    code = track_new_emails(gmail_service)
    if not code:
        time.sleep(5)
        code = track_new_emails(gmail_service)
    for i in str(code):
        ActionChains(driver=driver, duration=20)\
                    .send_keys(i)\
                    .perform()
    time.sleep(7)
    driver.get("https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=3mnd3kbtk15qfq62drjixh5xjpnigj&redirect_uri=https://localhost&scope=user:read:email+user:edit+chat:edit+chat:read+user:write:chat&state=c3ab8aa609ea11e793ae92361f002671")
    el = driver.find_element("css selector", ".js-authorize")
    ActionChains(driver=driver, duration=20)\
                .move_to_element(el)\
                .click(el)\
                .perform()
    time.sleep(3)
    url = driver.current_url
    token = url[32:].split("&")[0]
    accs = open("accounts.txt", "a")
    s = username + ":" + token + ":" + password + ":" + email
    accs.write(s)
    
    driver.get("https://www.twitch.tv")

    profile_button_xpath = "//button[@data-a-target='user-menu-toggle']"
    time.sleep(1)

    profile_button = driver.find_element("xpath", profile_button_xpath)
    profile_button.click()

    signout_button_xpath = "//button[@data-a-target='dropdown-logout']"
    time.sleep(1)

    signout_button = driver.find_element("xpath", signout_button_xpath)
    signout_button.click()

    time.sleep(5)
    
    driver.quit()

if __name__ == '__main__':
    cnt = 1
    if len(sys.argv) != 1:
        cnt = int(sys.argv[1])
    names = open("usernames.txt").readlines()
    emails = open("emails.txt").readlines()
    maxAccs = min(len(names), len(emails), cnt)
    gmail_service = get_gmail_service()
    track_new_emails(gmail_service)
    for i in range(maxAccs):
        username = names[i]
        email = emails[i]
        reg_account(username[:-1], email, gmail_service)
    open("usernames.txt", "w").writelines(names[maxAccs:])
    open("emails.txt", "w").writelines(emails[maxAccs:])
    print("Аккаунты в количестве " + str(maxAccs) + " успешно созданы")
# сделать подтверждение по почте, сделать генерацию имени и пароля, добавить API ключ, запись в файл.