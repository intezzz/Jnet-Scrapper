from typing import List, Dict
import re


def is_logged_event(info: List, logged: Dict) -> bool:
    keys = logged.keys()
    date_time = info[0]
    details = info[1]
    if date_time in keys and logged[date_time] == details:
        return True
    return False


def extract_event(cell: str) -> List:
    data3 = re.sub("NEW", " ", cell).strip()
    data4 = re.sub("  +", ",", data3)
    return data4.split(",")


def log_guest_show(data, guest: Dict, logged: Dict, group: str) -> None:
    info = [tuple(extract_event(data[0].get_text("  "))),
            extract_event(data[-1].get_text("  "))]
    if is_song_of_tokyo(info):
        info = extract_song_of_tokyo(info)
    if is_shounenclub(info):
        info = extract_shounenclub(info)
    flag = True
    if is_logged_event(info, logged):
        return None
    for item in info:
        if is_filter_guest_show(item, group):
            flag = False
    if flag:
        guest[info[0]] = info[-1]


def is_filter_guest_show(data, group: str) -> bool:
    if group == "kanjani":
        for item in data:
            if ("SONGS OF TOKYO" in item and "[" in item) \
                    or "知ってるワイフ" in item:
                return True
        return False
    for item in data:
        if "★" in item or "放送予定" in item or \
                ("SONGS OF TOKYO" in item and "[" in item) or ("[再放送]" in item):
            return True
    return False


def is_song_of_tokyo(info) -> bool:
    for item in info:
        for detail in item:
            if "SONGS OF TOKYO" in detail and "[" not in detail:
                return True
    return False


def extract_song_of_tokyo(info) -> List:
    bs_date_time = info[0][1]
    bs_date = bs_date_time[:bs_date_time.find(")") + 1]
    bs_time = bs_date_time[bs_date_time.find(')') + 1:]
    bs_tpl = (bs_date, bs_time)
    info[1][1] = info[0][0].strip(":")
    bs_lst = info[1].copy()
    return [bs_tpl, bs_lst]

    # bs4k_date_time = info[0][4]
    # bs4k_date = bs4k_date_time[:bs4k_date_time.find(")") + 1]
    # bs4k_time = bs4k_date_time[bs4k_date_time.find(")") + 1:]
    # bs4k_tpl = (bs4k_date, bs4k_time)
    # info[1][1] = info[0][2].strip(":")
    # bs4k_lst = info[1].copy()


def is_shounenclub(info) -> bool:
    for item in info:
        for detail in item:
            if "少年倶楽部" in detail:
                return True
    return False


def extract_shounenclub(info) -> List:
    date_time = info[0][1]
    date = date_time[:date_time.find(")") + 1]
    time = date_time[date_time.find(")") + 1:]
    tpl = (date, time)
    lst = info[1].copy()
    return [tpl, lst]
