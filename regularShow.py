from typing import Dict
import guestShow
import datetime


def log_regular_show(data, regular: Dict, logged: Dict):
    info = [guestShow.extract_event(data[0].get_text("  ")),
            guestShow.extract_event(data[-1].get_text("  "))]
    for i in range(len(info[0])):
        if "変更の場合あり" in info[0][i]:
            info[0][i] = info[0][i][:info[0][i].find("(")]
            info[0] = info[0][:2]
            break
        if "再放送" in info[0][i] or "放送予定" in info[0][i] or "★" in info[0][i]\
                or "※" in info[0][i]:
            return None
    for i in range(len(info[0])):
        if "毎週" in info[0][i]:
            if "月曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 1) + "()"
            if "火曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 2) + "()"
            if "水曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 3) + "()"
            if "木曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 4) + "()"
            if "金曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 5) + "()"
            if "土曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 6) + "()"
            if "日曜" in info[0][i]:
                info[0][i] = str(datetime.date.today().month) + "/" + str(
                    datetime.date.today().day + 7) + "()"
            if not guestShow.is_logged_event([tuple(info[0]), info[1]], logged):
                regular[tuple(info[0])] = info[-1]
