from datetime import datetime
import arrow

def get_current_datetime_iso8601():
    current_utc_time = datetime.utcnow()
    iso_format_utc_time = current_utc_time.isoformat() + "Z"
    return iso_format_utc_time

def humanize(dt):
    try:
        return arrow.get(dt).humanize()
    except arrow.parser.ParserError:
        return dt
