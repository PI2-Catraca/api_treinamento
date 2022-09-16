from fastapi import FastAPI
import treinador
from pydantic import BaseModel
import psycopg2
import base64
import os 
import shutil
from xml.etree.ElementTree import Element, SubElement, ElementTree
from google.cloud import storage

app = FastAPI()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'aerial-velocity-359918-e385a21f34a1.json'
storage_client = storage.Client()

class Usuario(BaseModel):
    nome: str
    cpf: str

def upload_file(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print('enviado')
        return True
    except Exception as e:
        print(e)
        return False

def delete_file(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        print('deletado')
        return True
    except Exception as e:
        print(e)
        return False

def conecta_db():
  con = psycopg2.connect(host='localhost', database = 'db_catraca' ,port = '15432', user='postgres', password='password')
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

@app.get("/criar")
async def home(usuario: Usuario):
    fotos = consultar_db('select * from tb_foto where usuario_cpf = %s', (usuario.cpf,))
    try:
        dir = './dataset/{cpfUsuario}'.format(cpfUsuario = usuario.cpf)
        os.mkdir(dir)
    except OSError:
        print("Diretório dataset já existente.")

    try:
        dir = './biometria'
        os.mkdir(dir)
    except OSError:
        print("Diretório biometria já existente.")

    cpfUsuario = ''
    for f in fotos:
        idFoto, cpfUsuario, ft, tipo = f
        ft_byte = bytes(ft, 'utf-8')
        
        #verifico se o tipo da foto é igual = b (biometria)
        if tipo == 'b' :
            bio = open("./biometria/{cpfUsuario}.dat".format(nomeUsuario = usuario.nome, cpfUsuario = cpfUsuario), "wb")
            bio.write(base64.urlsafe_b64decode(bytes(ft_byte)))
            bio.close()
            cpfUsuario = cpfUsuario
            continue

        foto = open("./dataset/{cpfUsuario}/{idFoto}.jpg".format(cpfUsuario = usuario.cpf, idFoto = idFoto), "wb")
        foto.write(base64.urlsafe_b64decode(bytes(ft_byte)))
        foto.close()

    await treinador.iniciarTreinamento()
    
    file_path = r'/home/others/Desktop/api_treinamento'
    file_path_biometria = r'/home/others/Desktop/api_treinamento/biometria'

    upload_file('encodings.pickle', os.path.join(file_path, 'encodings.pickle'), 'pi2-catraca')
    upload_file(('{cpfUsuario}.dat').format(cpfUsuario = cpfUsuario), os.path.join(file_path_biometria, './{cpfUsuario}.dat').format(cpfUsuario = cpfUsuario), 'biometria-pi2')

    return {"Encondings enviados"}

@app.get("/excluir")
async def home(usuario: Usuario):
    # fotos = consultar_db('select * from tb_foto where usuario_cpf = %s', (usuario.cpf,))
    try:
        shutil.rmtree('./dataset/{cpfUsuario}'.format(cpfUsuario = usuario.cpf))
        # dir = './dataset/{cpfUsuario}'.format(cpfUsuario = usuario.cpf)
        # os.mkdir(dir)
    except OSError:
        print("Não foi possível excluir o diretório.")

    try:
        os.remove('./biometria/{cpfUsuario}.dat'.format(cpfUsuario = usuario.cpf))
        # dir = './biometria'
        # os.mkdir(dir)
    except OSError:
        print("Não foi possível excluir o arquivo.")

    # cpfUsuario = ''
    # for f in fotos:
    #     idFoto, cpfUsuario, ft, tipo = f
    #     ft_byte = bytes(ft, 'utf-8')
        
    #     #verifico se o tipo da foto é igual = b (biometria)
    #     if tipo == 'b' :
    #         bio = open("./biometria/{cpfUsuario}.dat".format(nomeUsuario = usuario.nome, cpfUsuario = cpfUsuario), "wb")
    #         bio.write(base64.urlsafe_b64decode(bytes(ft_byte)))
    #         bio.close()
    #         cpfUsuario = cpfUsuario
    #         continue

    #     foto = open("./dataset/{nomeUsuario}/{idFoto}.jpg".format(nomeUsuario = usuario.nome, idFoto = idFoto), "wb")
    #     foto.write(base64.urlsafe_b64decode(bytes(ft_byte)))
    #     foto.close()

    await treinador.iniciarTreinamento()
    
    file_path = r'/home/others/Desktop/api_treinamento'
    # file_path_biometria = r'/home/others/Desktop/api_treinamento/biometria'

    upload_file('encodings.pickle', os.path.join(file_path, 'encodings.pickle'), 'pi2-catraca')
    delete_file(usuario.cpf+'.dat', '', 'biometria-pi2')
    # delete_file(('{cpfUsuario}.dat').format(cpfUsuario = cpfUsuario), os.path.join(file_path_biometria, './{cpfUsuario}.dat').format(cpfUsuario = cpfUsuario), 'biometria-pi2')

    return {"Encondings enviados"}