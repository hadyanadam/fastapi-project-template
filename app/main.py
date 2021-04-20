from fastapi import FastAPI
from app.routers import router
from app.db.session import SessionLocal
from app.db.init_db import init_db

app = FastAPI()


@app.on_event('startup')
def init_data():
    db = SessionLocal()
    init_db(db)


app.include_router(router)
