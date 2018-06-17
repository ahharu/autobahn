from datetime import datetime
from src.DynamoUpserter.utils.UTCConvert import UTC_time_to_epoch
from src.Environment.get_env_variables import get_ban_time

class TimeDecision():

    @staticmethod
    def should_unban(timestamp):
        now_dt = datetime.utcnow()
        event_dt = datetime.utcfromtimestamp(timestamp)
        
        timedelta = now_dt - event_dt
        minutes = abs(timedelta.total_seconds()) // 60

        if minutes > get_ban_time():
            return True
        else:
            return False
