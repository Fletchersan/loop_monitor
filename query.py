from models import StoreHours, StoreStatus, StoreTimezones
from sqlalchemy import extract, case, func, text, and_, or_
import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('postgresql+psycopg2://postgres:decent_password@localhost:54320/loop_db')
session: Session = Session(engine)

# set the timezone to be used for all datetime comparisons
tz_utc = 'UTC'

# get the current timestamp in UTC
now_utc = datetime.utcnow()

# compute the start and end times for the different time periods
start_hour = now_utc - timedelta(hours=1)
start_day = now_utc - timedelta(days=1)
start_week = now_utc - timedelta(weeks=1)


# build the query
query = (
    session.query(
        StoreStatus.store_id.label('store_id'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_hour,
                            StoreStatus.status == 'active'
                        ),
                        func.timestampdiff(
                            text('minute'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('uptime_last_hour'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_day,
                            StoreStatus.status == 'active'
                        ),
                        func.timestampdiff(
                            text('hour'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('uptime_last_day'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_week,
                            StoreStatus.status == 'active'
                        ),
                        func.timestampdiff(
                            text('hour'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('uptime_last_week'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_hour,
                            StoreStatus.status == 'inactive'
                        ),
                        func.timestampdiff(
                            text('minute'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('downtime_last_hour'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_day,
                            StoreStatus.status == 'inactive'
                        ),
                        func.timestampdiff(
                            text('hour'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('downtime_last_day'),
        func.sum(
            case(
                [
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_week,
                            StoreStatus.status == 'inactive'
                        ),
                        func.timestampdiff(
                            text('hour'),
                            StoreStatus.timestamp_utc,
                            now_utc
                        )
                    )
                ],
                else_=0
            )
        ).label('downtime_last_week')
    )
    .join(
        StoreHours,
        and_(
            StoreHours.store_id == StoreStatus.store_id,
            StoreHours.day_of_week == extract('dow', func.convert_tz(now_utc, tz_utc, StoreHours.start_time_local))
        )
    )
    .join(
        StoreTimezones,
        StoreHours.store_id == StoreTimezones.store_id,
        isouter=True
    )
    .filter(
        or_(
            StoreTimezones.timezone_str.is_(None),
            StoreTimezones.timezone_str == '',
            StoreTimezones.timezone_str == 'America/Chicago'  # default timezone
        )
    )
    .group_by(StoreStatus.store_id)
)