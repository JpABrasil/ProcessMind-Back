import tools
from utils import *
from google.genai import types
import pickle
import os
import json
from fastapi import FastAPI,File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/enviar_mensagem")
async def enviar_mensagem(
    prompt: str = Form(...),
    id_usuario: str = Form(...),
    id_chat: str = Form(...),
    agente: str = Form(...),
    modelo: str = Form("gemini-2.0-flash"),
    anexos: List[UploadFile] = File(None)
):
    '''
    Rota para gerar conteúdo usando o modelo Gemini.
    Args:
        request (dict): Dados da requisição.
    '''
    try:
        with open(f"agentes/{agente}.pkl", "rb") as f:
            agente = pickle.load(f)
        
        if prompt == "":
            if agente.prompt_base is None:
                return JSONResponse(content={"error": "Prompt base não definida."}, status_code=400)
            prompt = agente.prompt_base 

        #Segue o padrão a depender do modelo escolhido
        if "gemini" in modelo:
            resposta,nome_arquivo =  await gemini_enviar_mensagem(id_usuario=id_usuario, id_chat=id_chat, prompt=prompt, anexos=anexos, modelo=modelo, agente=agente,tools=agente.ferramentas)
            #Retorna Resposta em JSON
            return JSONResponse(content={"response": resposta,"novo_id":nome_arquivo}, status_code=200)
    

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": f"Erro {e}"}, status_code=500)

@app.get('/listar_chats')
def listar_chats(id_usuario:str,agente:str):
    '''
    Rota para listar os chats de um usuário.
    Args:
        id_usuario (str): ID do usuário.
    '''
    try:
        arquivos = os.listdir(f"chats/{id_usuario}/{agente}/")
        chats_usuario = []
        for arquivo in arquivos:     
            if arquivo.endswith(".pkl"):
                # Adiciona o nome do arquivo (sem extensão) à lista  
                chats_usuario.append(arquivo.split(".")[0])
        return JSONResponse(content={"chats": chats_usuario}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": f"Erro {e}"}, status_code=500)
    
@app.get('/retornar_chat')
def retornar_chat(id_usuario:str, agente:str,id_chat:str,modelo:str="gemini-2.0-flash"):
    '''
    Rota para retornar o histórico de um chat.
    Args:
        id_usuario (str): ID do usuário.
        id_chat (str): ID do chat.
    '''
    try:
        print(id_usuario, agente, id_chat)
        # Carrega o histórico do chat
        with open(f"chats/{id_usuario}/{agente}/{id_chat}.pkl", "rb") as f:
            historico = pickle.load(f)
        if 'gemini' in modelo:
            # Converte o histórico para o formato JSON
            historico = gemini_serializar_mensagem(historico)
        
        return JSONResponse(content={"historico": historico}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": f"Erro {e}"}, status_code=500)
    