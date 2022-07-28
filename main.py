from fastapi import FastAPI
import treinador
import requests

app = FastAPI()

API_ENDPOINT = "url da api da rasp"
source_code =
data = {}

@app.get("/")
def home():
    treinador.iniciarTreinamento()
    request = requests.post(url = API_ENDPOINT, data = data)
    response_url = request.text
    return {"Hello": "World"}