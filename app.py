import datetime
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import sqlalchemy

import database
from models import GameEvents, UpdateData

engine = sqlalchemy.create_engine("sqlite:///z.db", echo=True)
templates = Jinja2Templates(directory="templates")
database.meta.create_all(engine)

te = database.timed_events
we = database.weekly_events
conn = engine.connect()

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="main.html")


@app.post("/add_events")
def add_events(item_data: GameEvents):
    if not item_data.end_date and not item_data.time_left:
        return "failure"

    # fmt: off
    if item_data.end_date is None:
        item_data.end_date = datetime.datetime.now().date() \
                             + datetime.timedelta(item_data.time_left)
    # fmt: on

    data_to_add = item_data.model_dump()
    data_to_add.pop("time_left")

    conn.execute(te.insert().values(data_to_add))
    conn.execute(te.delete().where(te.c.end_date < datetime.datetime.now()))
    conn.commit()

    return "success"


@app.post("/complete")
def update_status(data: UpdateData):
    # fmt: off
    conn.execute(te.update()
        .where(te.c.id == data.id)
        .values(is_completed=data.is_completed)
    )
    # fmt: on


@app.get("/all_events")
def fetch_all_events():
    results = conn.execute(te.select())
    conn.execute(te.delete().where(te.c.end_date < datetime.datetime.now()))
    conn.commit()
    current_events = []
    now = datetime.datetime.now().date()
    for result in results:
        id, game_name, event_name, end_date, game_type, is_completed = result
        current_events.append(
            {
                "id": id,
                "game": game_name,
                "event": event_name,
                "type": game_type,
                "time_left": (end_date - now).days,
                "completed": is_completed,
            }
        )
    return current_events


@app.get("/top_events")
def fetch_sorted_events():
    results = conn.execute(
        te.select().order_by(te.c.end_date).where(te.c.is_completed != 1).limit(5)
    )
    conn.execute(te.delete().where(te.c.end_date < datetime.datetime.now()))
    conn.commit()
    current_events = []
    now = datetime.datetime.now().date()
    for result in results:
        id, game_name, event_name, end_date, game_type, is_completed = result
        time_left = (end_date - now).days

        current_events.append(
            {
                "id": id,
                "game": game_name,
                "event": event_name,
                "type": game_type,
                "time_left": time_left,
                "completed": is_completed,
            }
        )

    return current_events


@app.get("/events/{id}")
def fetch_event(id: int):
    result = conn.execute(te.select().where(te.c.id == id)).all()[0]
    id, game_name, event_name, end_date, game_type, is_completed = result

    return {
        "game": game_name,
        "event": event_name,
        "end_date": end_date,
        "game_type": game_type,
        "is_completed": is_completed,
    }


@app.delete("/{id}")
def delete_event(id: int):
    conn.execute(te.delete().where(te.c.id == id))
    conn.commit()
    return "Success"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

