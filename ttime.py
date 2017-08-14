#!/usr/bin/env python3
import re
import datetime
import fileinput
import locale
import calendar


def get_language():
    try:
        return locale.getdefaultlocale()[0][:2]
    except:
        return 'en'

texts = {
    'en': {
        'calendar_week': 'CW',
        'total': 'total',
        'totalHours': 'total hrs.',
        'totalDays': 'total days'
    },
    'de': {
        'calendar_week': 'KW',
        'total': 'gesamt',
        'totalHours': 'gesamt Std.',
        'totalDays': 'gesamt Tage'
    }
}[get_language()]


class WorkPeriod:
    def __init__(self, start_hour, start_minute, end_hour, end_minute, description):
        self.start_hour = int(start_hour)
        self.start_minute = int(start_minute)
        self.end_hour = int(end_hour)
        self.end_minute = int(end_minute)
        self.description = description
        self.minutes = (self.end_hour * 60 + self.end_minute) - (self.start_hour * 60 + self.start_minute)
        self.hours = self.minutes() / 60
    def __repr__(self):
        range_str = "{}:{}-{}:{}".format(self.start_hour, self.start_minute, self.end_hour, self.end_minute)
        return "Period({})".format(range_str)


class WorkDay:
    def __init__(self, year, month, day, periods):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.date = datetime.date(year, month, day)
        self.periods = periods
        (_, self.week, self.weekday) = self.date.isocalendar()
        self.day_no = self.date.strftime('%d')
        self.week_no = self.date.strftime('%w')
        self.descriptions = " * ".join([p.description for p in periods])
        self.minutes = sum([p.minutes() for p in self.periods])
        self.hours = self.minutes / 60
    def __eq__(self, other):
        return self.date == other.date


def read_workdays(file_input = fileinput.input()):
    month_year_pattern='^\[(\d\d)/(\d\d\d\d)]$'
    log_work_pattern='^(\d\d\.)?\s+(\d\d\d\d)-(\d\d\d\d)\s+(.*)$'
    bad_format_err = Exception('bad format!')
    last_day = None
    year = None
    month = None
    items =[]
    for line in file_input:
        # month & jear definition, e.g. '[08/2015]'
        match = re.search(month_year_pattern, line)
        if match:
            (month, year) = [int(x) for x in match.groups()]
            continue
        # log entry, e.g. '21. 0930-1230 T&I-Zugriffsproblem, Liste'
        match = re.search(log_work_pattern, line)
        if match:
            if not (month and year):
                raise bad_format_err
            (day, start_time, end_time, description) = match.groups()
            day = int(day[:2]) if day else last_day
            if not day:
                raise bad_format_err
            period = WorkPeriod(start_time[:2], start_time[2:], end_time[:2], end_time[2:], description)
            # sys.stdout.write(day, period.hours(), description)
            item = items.pop() if day == last_day else WorkDay(year, month, day, [])
            item.periods.append(period)
            items.append(item)
            last_day = day
            continue
    return items


def main():
    template_text = ''
    with open('text_template_de.txt', 'r') as f:
      template_text = f.read()
    # set language to system default language (for weekday display)
    locale.resetlocale()
    week_day_names = list(calendar.day_abbr)
    items = read_workdays()
    week_summary = lambda hours: "----------\n{}:  \t{}\n".format(texts['total'], hours)
    last_week = None
    week_hours = 0
    total_hours = 0
    for item in items:
        #print(item)
        sum_hours = sum([x.hours() for x in item.periods])
        desc_text = " * ".join(item.descriptions)
        if item.week != last_week:
            if last_week:
                print(week_summary(week_hours))
            print(texts['calendar_week'] + format(item.week) + ":")
            print("----------")
            week_hours = 0
            last_week = item.   week
        print("{}, {}\t{}\t{}".format(week_day_names[item.weekday-1], item.date.strftime('%d.%m.'), sum_hours, desc_text))
        week_hours += sum_hours
        total_hours += sum_hours
    print(week_summary(week_hours))
    print("=======================================================")
    print("{}:  \t{}".format(texts['totalHours'], total_hours))
    print("{}:  \t{}".format(texts['totalDays'], total_hours/8))



if __name__ == "__main__":
    main()
