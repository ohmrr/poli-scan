from fastapi import FastAPI

app = FastAPI(
    title="FPPC Conflict of Interest Identifier",
    description="Backend API for checking potential conflicts of interest for public officials",
    version="0.0.1"
)

@app.get("/")
def root():
    return { "message": "App is running successfully!" }