#!/usr/bin/env python3
import re
import datetime
import locale
import calendar
import os
from jinja2 import Environment, FileSystemLoader
import configparser
import sys

# set language to system default language (for weekday display)
locale.resetlocale()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WEEK_DAY_NAMES = list(calendar.day_abbr)
TEMPLATE_DIR = 'templates'
DEFAULT_TEMPLATE_FILE = 'week_report.txt'


class MsgStruct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class WorkPeriod:
    def __init__(self, start_hour, start_minute, end_hour, end_minute, description):
        self.start_hour = float(start_hour)
        self.start_minute = int(start_minute)
        self.end_hour = int(end_hour)
        self.end_minute = int(end_minute)
        self.description = description
        self.minutes = (self.end_hour * 60 + self.end_minute) - (self.start_hour * 60 + self.start_minute)
        self.hours = float(self.minutes / 60)
    def __repr__(self):
        range_str = "{}:{}-{}:{}".format(self.start_hour, self.start_minute, self.end_hour, self.end_minute)
        return "Period({})".format(range_str)


class WorkWeek:
    def __init__(self, year, week_no):
        self.year = int(year)
        self.week_no = int(week_no)
    def __eq__(self, other):
        return self.year == other.year and self.week_no == other.week_no
    def __lt__(self, other):
        return self.week_no < other.week_no if self.year == other.year else self.year < other.year
    def __repr__(self):
        return str(self.year) + " CW" + self.week_no


class WorkDay:
    def __init__(self, year, month, day, periods):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.date = datetime.date(year, month, day)
        self.periods = periods
        (week_year, week_no, self.weekday) = self.date.isocalendar()
        self.week = WorkWeek(week_year, week_no)
        self.day_name = WEEK_DAY_NAMES[self.weekday - 1]
        self.day_no = self.date.strftime('%d')
        self.month_no = self.date.strftime('%m')
        self.year_no = self.date.strftime('%y')
        self.description = " | ".join([p.description for p in periods if p.description])
        self.minutes = sum([p.minutes for p in self.periods])
        self.hours = float(self.minutes / 60)
    def __eq__(self, other):
        return self.date == other.date
    def __repr__(self):
        return str(self.date) + (", ".join(self.periods))


def filter_workdays(workdays, day_filters = [], period_filters = []):
    if not (day_filters or period_filters):
        return workdays
    results = []
    for src_day in [d for d in workdays if all(f(d) for f in day_filters)]:
        tgt_periods = [p for p in src_day.periods if all(f(p) for f in period_filters)]
        tgt_day = WorkDay(src_day.year, src_day.month, src_day.day, tgt_periods)
        if len(tgt_day.periods) > 0:
            results.append(tgt_day)
    return results


def get_language():
    try:
        return locale.getdefaultlocale()[0][:2]
    except:
        return 'en'


def load_template_messages(template_filename):
    template_msg_file = os.path.join(THIS_DIR, template_filename + '.config')
    config = configparser.ConfigParser()
    config.read(template_msg_file)
    lang = get_language()
    d = dict(config[lang]) if config.has_section(lang) else {}
    # d = {s:dict(config.items(s)) for s in config.sections()}
    return MsgStruct(**d) if d else None


def read_workdays(config_parser):
    month_year_pattern = r'^(\d\d)/(\d\d\d\d)$'
    period_pattern = r'^(\d\d\d\d)-(\d\d\d\d)\s*(.*)$'
    bad_format_err = Exception('bad format!')
    items = []
    for section in config_parser.sections():
        match = re.search(month_year_pattern, section)
        if not match:
            raise bad_format_err
        (month, year) = [int(x) for x in match.groups()]
        for key in config_parser[section]:
            day = int(key[:2])
            periods = []
            for period_str in config_parser[section][key].split("\n"):
                match = re.search(period_pattern, period_str)
                if not match:
                    raise bad_format_err
                (start_time, end_time, description) = match.groups()
                periods.append(WorkPeriod(start_time[:2], start_time[2:], end_time[:2], end_time[2:], description))
            items.append(WorkDay(year, month, day, periods))
    return items


def _get_args():
    import argparse
    from  datetime import datetime
    def valid_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)
    parser = argparse.ArgumentParser()
    parser.add_argument('workfile', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-t', '--text', help='filter work period by text')
    parser.add_argument("-s", "--startdate", help="start date - format YYYY-MM-DD", type=valid_date)
    parser.add_argument("-e", "--enddate", help="end date - format YYYY-MM-DD", type=valid_date)
    parser.add_argument("-d", "--date", help="date - format YYYY-MM-DD", type=valid_date)
    return parser.parse_args()


def _get_day_filters(args):
    filters = []
    if args.startdate:
        filters.append(lambda day: day.date >= args.startdate)
    if args.enddate:
        filters.append(lambda day: day.date <= args.enddate)    
    if args.date:
        filters.append(lambda day: day.date == args.date)    
    return filters    


def _get_period_filters(args):
    filters = []
    if args.text:
        filters.append(lambda period: args.text in period.description)
    return filters    


def _get_workfile_parser(files):
    parser = configparser.ConfigParser(delimiters = ['.'], strict=False)
    text = "".join(["".join(line for line in file) for file in files]) 
    # TODO improve
    fallback_section='[01/0001]'
    parser.read_string(fallback_section + '\n' + text)
    return parser


def main():
    args = _get_args()
    workfile_parser = _get_workfile_parser(args.workfile)
    unfiltered_items = read_workdays(workfile_parser)
    items = filter_workdays(unfiltered_items, 
        day_filters = _get_day_filters(args),
        period_filters = _get_period_filters(args)
    )
    total_hours = sum([x.hours for x in items])
    template_file = TEMPLATE_DIR + "/" + DEFAULT_TEMPLATE_FILE
    messages = load_template_messages(template_file)
    template = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True).get_template(template_file)
    print(template.render(
        items = items,
        total_hours= total_hours,
        total_days = total_hours / 8,
        msg = messages
    ))


# if sys.version_info < (3,4): sys.exit('Python < 3.4 is not supported')

if __name__ == "__main__":
    main()
