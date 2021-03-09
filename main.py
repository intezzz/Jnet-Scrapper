from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from typing import List, Dict
from bs4 import BeautifulSoup
import requests
import re
import guestShow
import regularShow
import datesAndTime


def read_file(file_name: str) -> List:
    r = []
    with open(file_name, "r", encoding="utf-8") as file:
        curr = file.readline().strip("\n")
        while curr:
            r.append(curr)
            curr = file.readline().strip("\n")
    return r


html_text = requests.get(
    "https://www.johnnys-net.jp/page?id=media&artist=13").text
soup = BeautifulSoup(html_text, 'lxml')
groups = read_file("groups.txt")
calendar_links = read_file("calendar_links.txt")
webpage_links = read_file("webpage_links.txt")
guest = {}
regular = {}
logged = {}

SCOPES = ['https://www.googleapis.com/auth/calendar']


def find_table_type(html: str) -> str:
    if "詳細" in html:
        if "発売日" in html:
            return "magazine"
        elif "放送日" not in html:
            return "cm"
    if "配信" in html:
        return "web"
    if "放送日" in html:
        if "毎週" in html:
            return "regular"
        else:
            return "guest"
    return "unknown"


def read_logged_events(group: str) -> Dict:
    r = {}
    with open("schedules/" + group + ".txt", "r", encoding="utf8") as file:
        curr = file.readline()
        while curr:
            key = tuple(curr.replace("\n", " ").strip("' ").split("', '"))
            data = file.readline().replace("\n", " ").strip("' ").split("', '")
            r[key] = data
            file.readline()
            curr = file.readline()
    return r


def write_logged_event(info: List, group: str):
    with open("schedules/" + group + ".txt", "a", encoding="utf8") as file:
        date_time = str(info[0]).strip("[]()")
        details = str(info[1]).strip("[]()")
        if file.tell() != 0:
            file.write("\n")
        file.write(date_time)
        file.write("\n")
        file.write(details)
        file.write("\n")


def scraping(group: str) -> None:
    tables = soup.find_all("table",
                           class_="table-border table-appearance mt-15")
    table_bodies = soup.find_all("tbody")
    for index, table_body in enumerate(table_bodies):
        rows = table_body.find_all("tr")
        table_type = find_table_type(str(tables[index]))
        for row in rows:
            if table_type == "guest":  # if this is guest show
                data = row.find_all('td')
                guestShow.log_guest_show(data, guest, logged, group)
            if table_type == "regular" and datetime.date.today().weekday() == 6:
                data = row.find_all('td')
                regularShow.log_regular_show(data, regular, logged)

    # print the whole guest
    # for key in guest.keys():
    #     for item in key:
    #         print(item)
    #     for item in guest[key]:
    #         print(item)
    #     print("\n")
    # print(guest)


def api_setup(group: str):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if group == 'kanjani':
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        return service
    else:
        if os.path.exists('token1.pickle'):
            with open('token1.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials1.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token1.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        return service


def add_event_to_cal(service, schedule: Dict, group: str, calendar: str):
    count = 0
    for key in schedule.keys():
        summary = schedule[key][0]
        description = ''
        if len(schedule[key]) > 1:
            for i in range(1, len(schedule[key])):
                description = description + "\n" + schedule[key][i]
            description = description[1:]
        time_zone = "Japan"
        start_date_time = datesAndTime.get_date_time(key)[0]
        end_date_time = datesAndTime.get_date_time(key)[1]
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_date_time,
                'timeZone': time_zone,
            },
            'end': {
                'dateTime': end_date_time,
                'timeZone': time_zone,
            },
        }
        event = service.events().insert(calendarId=calendar,
                                        body=event).execute()
        details = [key, schedule[key]]
        write_logged_event(details, group)
        count += 1
        print(f"**{group} -- {count}/{len(schedule)} added**")
        log_success(f"**{group} -- {count}/{len(schedule)} added**")


def log_success(string: str):
    with open("log.txt", "a", encoding="utf8") as file:
        file.write(string)
        file.write("\n")


if __name__ == "__main__":
    for i in range(len(groups)):
        # for i in range(1):
        html_text = requests.get(
            webpage_links[i]).text
        soup = BeautifulSoup(html_text, 'lxml')
        guest = {}
        regular = {}
        logged = read_logged_events(groups[i])
        scraping(groups[i])

        # print(guest)
        # print(regular)
        # # print(read_logged_events() == guest)

        try:
            service = api_setup(groups[i])
            add_event_to_cal(service, guest, groups[i], calendar_links[i])
            add_event_to_cal(service, regular, groups[i], calendar_links[i])
        except:
            log_success("Error - " + str(datetime.date.today()))
            input("Error occurred. Press enter to exit")
            quit()
        log_success(str(datetime.date.today()) + "----" + groups[i])

        # for key in guest.keys():
        #     print(get_date_time(key))

        # service = api_setup(groups[i])
        # add_event_to_cal(service, guest, groups[i], calendar_links[i])
        # add_event_to_cal(service, regular, groups[i], calendar_links[i])
