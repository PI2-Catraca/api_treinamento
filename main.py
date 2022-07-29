from fastapi import FastAPI
import treinador
import requests
from pydantic import BaseModel
# import base64

class Pickle(BaseModel):
    imagem: str

app = FastAPI()

API_ENDPOINT = "http://127.0.0.1:8000/teste"

@app.get("/")
def home():
    treinador.iniciarTreinamento()
    pickle = open("encodings.pickle", "rb").read()
    data = {"imagem": pickle}
    requisicao = requests.post(url = API_ENDPOINT, data = data)
    pastebin_url = requisicao.text
    print(pastebin_url)

    return {"Hello": "World"}

@app.post("/teste")
async def teste(pickle: Pickle):
    return {pickle.imagem}