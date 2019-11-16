import abc
from datetime import date
from typing import NamedTuple
import re


CURRENT_YEAR = date.today().year
YEAR_RE = re.compile(r"20\d{2}")


class DateRange(NamedTuple):
    start: date
    end: date


class DateParser(abc.ABC):
    @abc.abstractclassmethod
    def date_text_to_date(cls, date_text, year=None):
        pass


class DefaultDateParser(DateParser):
    @classmethod
    def date_text_to_date(cls, date_text, year=None):
        date_text = date_text.strip().lower()
        if "-" in date_text:
            parts = date_text.split("-")
            if year is None:
                match = re.search(r"20\d{2}", date_text)
                if not match:
                    year = CURRENT_YEAR
                else:
                    year = int(match.group(0))

            start = cls.date_text_to_date(parts[0], year)
            end = cls.date_text_to_date(parts[1], year)

            if start > end:
                start = date(start.year - 1, start.month, start.day)

            return DateRange(start=start, end=end)
        else:
            match = re.search(
                r"(?P<day_str>\d+)\w*\s*(?P<month_str>\w+)\s*(?P<year_str>\d+)?",
                date_text,
            )
            if not match:
                raise ValueError("error parsing string {}".format(date_text))

            day = int(match.group("day_str"))
            month_str = match.group("month_str")
            month = [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ].index(month_str) % 12

            if year is None and match.group("year_str") is None:
                year = CURRENT_YEAR

            if year is not None:
                return date(year, month + 1, day)
            else:
                year = int(match.group("year_str"))
                return date(year, month + 1, day)


class HippodromeDateParser(DateParser):
    @classmethod
    def date_text_to_date(cls, date_text, year=None):
        date_text = date_text.strip().lower()
        if "-" in date_text or "&" in date_text:
            if "-" in date_text:
                parts = date_text.split("-")
            elif "&" in date_text:
                parts = date_text.split("&")

            start_year_match = YEAR_RE.search(parts[0])
            end_year_match = YEAR_RE.search(parts[1])

            if start_year_match:
                start_year = int(start_year_match.group(0))
                start = cls.date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = cls.date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )

                else:
                    end = cls.date_text_to_date(parts[1], year=start_year)
            else:

                if end_year_match:
                    start_year = int(end_year_match.group(0))
                else:
                    start_year = CURRENT_YEAR
                start = cls.date_text_to_date(parts[0], year=start_year)

                if end_year_match:
                    end = cls.date_text_to_date(
                        parts[1], year=int(end_year_match.group(0))
                    )
                else:
                    end = cls.date_text_to_date(parts[1], year=start_year)

            if start > end:
                start = date(start.year - 1, start.month, start.day)

            return DateRange(start=start, end=end)
        else:
            match = re.search(
                r"(?P<day_str>\d+)\w*\s*(?P<month_str>\w+)\s*(?P<year_str>\d+)?",
                date_text,
            )
            if not match:
                raise ValueError("error parsing string {}".format(date_text))

            day = int(match.group("day_str"))
            month_str = match.group("month_str")
            month = [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ].index(month_str) % 12

            if year is None and match.group("year_str") is None:
                year = CURRENT_YEAR

            if year is not None:
                return date(year, month + 1, day)
            else:
                year = int(match.group("year_str"))
                return date(year, month + 1, day)


class ResortsworldDateParser(DateParser):

    SINGLE_DATE_RE = re.compile(r"(?P<day>\d+)\s+(?P<month>\w+)\s+(?P<year>20\d{2})")
    JOINT_DATE_RE = re.compile(
        r"(?P<start_day>\d+)\s*(?P<start_month>\w+)?\s*-\s*(?P<end_day>\d+)\s+(?P<end_month>\w+)\s+(?P<year>20\d{2})"
    )

    @classmethod
    def date_text_to_date(cls, date_text):
        date_text = date_text.strip()
        single_match = cls.SINGLE_DATE_RE.match(date_text)
        if single_match is not None:
            day = int(single_match.group("day"))
            year = int(single_match.group("year"))
            month = cls.month_text_to_int(single_match.group("month"))
            return date(year, month, day)

        joint_match = cls.JOINT_DATE_RE.match(date_text)
        if joint_match is not None:
            start_day = int(joint_match.group("start_day"))
            end_day = int(joint_match.group("end_day"))
            year = int(joint_match.group("year"))
            end_month = cls.month_text_to_int(joint_match.group("end_month"))
            if joint_match.group("start_month"):
                start_month = cls.month_text_to_int(joint_match.group("start_month"))
            else:
                start_month = end_month

            start = date(year, start_month, start_day)
            end = date(year, end_month, end_day)

            return DateRange(start=start, end=end)

        raise ValueError(f"Cannot parse {date_text}")

    @staticmethod
    def month_text_to_int(textvalue):
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ].index(textvalue) + 1
