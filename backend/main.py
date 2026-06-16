from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, subjects, materials, admin, admin_auth
from app.database import engine, Base
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="智练通API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(subjects.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(admin_auth.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "智练通API服务运行中"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)