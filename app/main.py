from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, SessionLocal
from routers import auth, users, expenses, files
from config import settings
import models
from seed import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   # creates tables in Neon
    db = SessionLocal()
    try:
        seed_users(db)                      # creates head/hr/emp1-3 once
    finally:
        db.close()
    yield


app = FastAPI(title="Expense Tracker API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,   # e.g. every *.vercel.app deployment of this project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(files.router, prefix="/api/files", tags=["files"])


@app.get("/")
def root():
    # Render pings "/" — without this it logs a 404 on every check
    return {"service": "Expense Tracker API", "status": "ok", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}