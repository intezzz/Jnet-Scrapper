import datetime
from typing import List


def fix_date(number):
    if len(number) == 1:
        number = "0" + number
    return number


def fix_month_and_day(month_day: tuple) -> tuple:
    smonth = month_day[0]
    emonth = month_day[1]
    sday = month_day[2]
    eday = month_day[3]
    if str(smonth) in "1 3 5 7 8 10" or str(smonth) == "12":
        if sday > 31:
            smonth += 1
            emonth += 1
            sday -= 31
            eday -= 31
        elif sday <= 31 and eday > 31:
            emonth += 1
            eday -= 31
    elif str(smonth) in "4 6 9 11":
        if sday > 30:
            smonth += 1
            emonth += 1
            sday -= 30
            eday -= 30
        elif sday <= 30 and eday > 30:
            emonth += 1
            eday -= 30
    else:
        if is_leap_year():
            if sday > 29:
                smonth += 1
                emonth += 1
                sday -= 29
                eday -= 29
            elif sday <= 29 and eday > 29:
                emonth += 1
                eday -= 29
        else:
            if sday > 28:
                smonth += 1
                emonth += 1
                sday -= 28
                eday -= 28
            elif sday <= 28 and eday > 28:
                emonth += 1
                eday -= 28
    return smonth, emonth, sday, eday


def is_leap_year() -> bool:
    now = datetime.datetime.today().year
    if (now % 4 == 0 and now % 100 != 0) or now % 400 == 0:
        return True
    return False


def fix_time_day(time_date: tuple) -> tuple:
    time = time_date[0]
    day = time_date[-1]
    if "24:" in time:
        time = time.replace("24:", "00:")
        day += 1
    elif "25:" in time:
        time = time.replace("25:", "01:")
        day += 1
    elif "26:" in time:
        time = time.replace("26:", "02:")
        day += 1
    elif "27:" in time:
        time = time.replace("27:", "03:")
        day += 1
    return time, day


def get_date_time(key: tuple) -> List:
    if not (len(key) == 2 and len(key[0]) <= 8):
        first = key[0][:key[0].index(")") + 1]
        leftover = key[0][key[0].index(")") + 1:]
        key = (first, leftover)
    if len(key) == 2 and len(key[0]) <= 8:
        date = key[0]
        time = key[1]
        month = date[:date.index("/")]

        start_day = int(date[date.index("/") + 1:date.index("(")])
        end_day = int(date[date.index("/") + 1:date.index("(")])
        start_time = time[:time.index("-")]
        if time[-1] == "-":
            end_time = start_time
        else:
            end_time = time[time.index("-") + 1:]
        new_std = fix_time_day((start_time, start_day))
        start_time = new_std[0]
        start_day = new_std[-1]
        new_etd = fix_time_day((end_time, end_day))
        end_time = new_etd[0]
        end_day = new_etd[-1]

        fixed_month_day = fix_month_and_day((int(month), int(month), start_day, end_day))
        smonth = fix_date(str(fixed_month_day[0]))
        emonth = fix_date(str(fixed_month_day[1]))
        start_day = fix_date(str(fixed_month_day[2]))
        end_day = fix_date(str(fixed_month_day[3]))

        str_start_time = f"2021-{smonth}-{start_day}T{start_time}:00+09:00"
        str_end_time = f"2021-{emonth}-{end_day}T{end_time}:00+09:00"
        return [str_start_time, str_end_time]
