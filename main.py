from fastapi import FastAPI
import treinador
import requests
from pydantic import BaseModel
import json as js
import pickle
import numpy as np
import psycopg2
import base64
import os

app = FastAPI()

API_ENDPOINT = "http://127.0.0.1:9000/api/encondings"

def conecta_db():
  con = psycopg2.connect(host='localhost', database='catraca',user='postgres', password='1230,123')
  return con

def consultar_db(sql, parametro):
  con = conecta_db()
  cur = con.cursor()
  cur.execute(sql, parametro)
  recset = cur.fetchall()
  registros = []
  for rec in recset:
    registros.append(rec)
  con.close()
  return registros

def default(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    raise TypeError('Unknown type:', type(obj))


class Usuario(BaseModel):
    nome: str
    cpf: str

@app.get("/")
async def home(usuario: Usuario):
    fotos = consultar_db('select * from foto where usuario_cpf = %s', (usuario.cpf,))
    try:
        dir = './dataset/{nomeUsuario}'.format(nomeUsuario = usuario.nome)
        os.mkdir(dir)
    except OSError:
        print("Diretório já existente.")

    for f in fotos:
        id, cpf, ft, tipoFoto = f
        foto = open("./dataset/{nomeUsuario}/{idFoto}.jpg".format(nomeUsuario = usuario.nome, idFoto = id), "wb")
        foto.write(base64.urlsafe_b64decode(bytes(ft)))

    await treinador.iniciarTreinamento()

    with open("encodings.pickle", "rb") as p:
        arquivoPickle = pickle.load(p)
    
    jsonPickle = js.dumps(arquivoPickle, default = default)

    data = jsonPickle
    requisicao = requests.post(url = API_ENDPOINT, data = data)
    pastebin_url = requisicao.text
    print(pastebin_url)

    return {"Encondings enviados"}