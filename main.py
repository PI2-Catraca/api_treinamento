from fastapi import FastAPI
import treinador
import requests
from pydantic import BaseModel
import json as js
import pickle
import numpy as np

app = FastAPI()

API_ENDPOINT = "http://127.0.0.1:9000/api/encondings"

def default(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    raise TypeError('Unknown type:', type(obj))

@app.get("/")
async def home():
    await treinador.iniciarTreinamento()

    with open("encodings.pickle", "rb") as p:
        arquivoPickle = pickle.load(p)
    
    jsonPickle = js.dumps(arquivoPickle, default = default)

    data = jsonPickle
    requisicao = requests.post(url = API_ENDPOINT, data = data)
    pastebin_url = requisicao.text
    print(pastebin_url)

    return {"Encondings enviados"}