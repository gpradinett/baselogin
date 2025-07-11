# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import pytz

IST = pytz.timezone('America/Lima')
PASS_DAYS = 15


class Dates():

    def get_today():
        result = date.today()
        return result

    def get_next_date():
        result = date.today() + timedelta(days=1)
        return result

    def get_next_month():
        result = date.today() + timedelta(days=30)
        return result

    def expired_token():
        result = datetime.utcnow() + timedelta(seconds=18000)
        return result

    def get_client_today():
        return datetime.strftime(datetime.now(IST),
'%d/%m/%Y')

    def limit_password_change(created_user):
        if isinstance(created_user, datetime):
            created_user = created_user.date()

        today = Dates.get_today()
        
        difference = today - created_user

        return 0 <= difference.days <= PASS_DAYS