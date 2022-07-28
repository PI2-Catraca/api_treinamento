from fastapi import FastAPI
import treinador
import requests
import base64

app = FastAPI()

API_ENDPOINT = "url da api da rasp"
data = open(encodings.pickle, "rb").read()
data_bytes = data.encode("ascii")
base64_bytes = base64.b64encode(data_bytes)
base64_string = base64_bytes.decode("ascii")

@app.get("/")
def home():
    treinador.iniciarTreinamento()
    request = requests.post(url = API_ENDPOINT, data = data)
    response_url = request.text
    return {"Hello": "World"}