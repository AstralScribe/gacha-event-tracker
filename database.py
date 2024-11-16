from sqlalchemy import Boolean, Table, Column, Integer, String, Date, MetaData

meta = MetaData()

timed_events = Table(
    "timed_events",
    meta,
    Column("id", Integer, primary_key=True),
    Column("game_name", String, nullable=False),
    Column("event_name", String, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("game_type", String, nullable=False),
    Column("is_completed", Boolean),
)


weekly_events = Table(
    "weekly_events",
    meta,
    Column("id", Integer, primary_key=True),
    Column("game_name", String, nullable=False),
    Column("weekly_name", String, nullable=False),
    Column("is_completed", Boolean),
)
