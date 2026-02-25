from fastapi import FastAPI
from server.app.services.legistar_client import LegistarClient
from server.app.services.form700_parser import load_form700_csv

app = FastAPI(
    title="FPPC Conflict of Interest Identifier",
    version="0.0.1",
)

# After getting the server running, open this url in your browser
# This will open up Swagger, which can be used to showcase the API
print("API Documentation - http://127.0.0.1:8000/docs")


@app.get("/")
def root():
    return {"message": "FPPC API is running successfully!"}


# Below are the demo endpoints


# Use "sonoma-county" for client_name
@app.get("/persons/{client_name}")
def get_persons(client_name: str):
    return LegistarClient(client_name).get_persons()


# Use "sonoma-county" for client name
# Use 2021 for year
@app.get("/officials/{client_name}/{year}")
def get_officials(client_name: str, year: int):
    return load_form700_csv(f"./server/app/data/{client_name}-{year}.csv")
