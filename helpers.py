from models import Reports, StoreHours, StoreStatus, StoreTimezones
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import pandas as pd
from sqlalchemy import extract, case, func, text, and_, or_
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, aliased
from sqlalchemy.types import Time

def generate_report_data(session: Session, report: Reports):
    tz_utc = 'UTC'

    now_utc = datetime(2023, 1, 26)

    # compute the start and end times for the different time periods
    start_hour = now_utc - timedelta(hours=1)
    start_day = now_utc - timedelta(days=1)
    start_week = now_utc - timedelta(weeks=1)
    sh_alias = aliased(StoreHours)

    query = (
    session.query(
        StoreHours.store_id.label('store_id'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_hour,
                            StoreStatus.status == 'active'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 60
                    )
                ],
                else_=0
            )
        ).label('uptime_last_hour'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_day,
                            StoreStatus.status == 'active'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 3600
                    )
                ],
                else_=0
            )
        ).label('uptime_last_day'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_week,
                            StoreStatus.status == 'active'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 3600
                    )
                ],
                else_=0
            )
        ).label('uptime_last_week'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_hour,
                            StoreStatus.status == 'inactive'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 60
                    )
                ],
                else_=0
            )
        ).label('downtime_last_hour'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_day,
                            StoreStatus.status == 'inactive'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 3600
                    )
                ],
                else_=0
            )
        ).label('downtime_last_day'),
        func.sum(
            case(
                *[
                    (
                        and_(
                            StoreStatus.timestamp_utc >= start_week,
                            StoreStatus.status == 'inactive'
                        ),
                        func.extract(
                            'epoch',
                            now_utc - StoreStatus.timestamp_utc
                        ) / 3600
                    )
                ],
                else_=0
            )
        ).label('downtime_last_week')
    )
    .select_from(StoreStatus)
    .join(StoreHours, StoreStatus.store_id == StoreHours.store_id)
    .join(StoreTimezones, StoreStatus.store_id == StoreTimezones.store_id)
    .join(
        sh_alias,
        and_(
            extract('dow', func.timezone(StoreTimezones.timezone_str, func.now())) == sh_alias.day,
            sh_alias.start_time_local <= func.cast(func.timezone(StoreTimezones.timezone_str, func.now()), Time),
            sh_alias.end_time_local > func.cast(func.timezone(StoreTimezones.timezone_str, func.now()), Time)
        )
    )
    # .outerjoin(StoreTimezones, StoreTimezones.store_id == StoreHours.store_id)
    .filter(StoreHours.day == extract('dow', func.timezone(StoreTimezones.timezone_str, func.now())))
    .group_by(StoreHours.store_id)
    ).limit(100)
    return query.all()


if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('postgresql+psycopg2://postgres:decent_password@localhost:54320/loop_db')
    session: Session = Session(engine)

    # get the current timestamp in UTC
    # now_utc = datetime.utcnow()
    
    