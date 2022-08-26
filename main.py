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
import os
from google.cloud import storage

# API_ENDPOINT = "http://127.0.0.1:9000/api/encondings"

app = FastAPI()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'aerial-velocity-359918-e385a21f34a1.json'
storage_client = storage.Client()

class Usuario(BaseModel):
    nome: str
    cpf: str

def upload_pickle(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print('true')
        return True
    except Exception as e:
        print(e)
        return False

def conecta_db():
  con = psycopg2.connect(host='localhost', port = '15432', database='db_catraca',user='postgres', password='password')
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

@app.get("/")
async def home(usuario: Usuario):
    fotos = consultar_db('select * from tb_foto where usuario_cpf = %s', (usuario.cpf,))
    try:
        dir = './dataset/{nomeUsuario}'.format(nomeUsuario = usuario.nome)
        os.mkdir(dir)
    except OSError:
        print("Diretório já existente.")

    for f in fotos:
        id, cpf, ft = f
        ft_byte = bytes(ft, 'utf-8')
        foto = open("./dataset/{nomeUsuario}/{idFoto}.jpg".format(nomeUsuario = usuario.nome, idFoto = id), "wb")
        foto.write(base64.urlsafe_b64decode(bytes(ft_byte)))


    await treinador.iniciarTreinamento()

    file_path = r'/home/kalebe/Desktop/treinador'
    upload_pickle('encodings.pickle', os.path.join(file_path, 'encodings.pickle'), 'pi2-catraca')

    return {"Encondings enviados"}