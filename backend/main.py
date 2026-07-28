from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import Base, engine
from app.routes import user_route, workbook_routes, inventory_routes, job_route, flow

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workflow Orchestrator API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Workflow Orchestrator API"
    }

app.include_router(user_route.router)
app.include_router(workbook_routes.router)
app.include_router(inventory_routes.router)
app.include_router(job_route.router)
app.include_router(flow.router)