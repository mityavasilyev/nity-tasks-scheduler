import datetime as dt
from datetime import datetime


class TimeUtils:

    @staticmethod
    def current_datetime() -> datetime:
        """
        Return current time in UTC timezone.
        :return: current datetime in UTC
        """
        return datetime.now(tz=dt.timezone.utc)
