from datetime import datetime

def get_current_datetime_iso8601():
    current_utc_time = datetime.utcnow()
    iso_format_utc_time = current_utc_time.isoformat() + "Z"
    return iso_format_utc_time
