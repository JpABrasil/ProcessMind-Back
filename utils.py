import os
from dotenv import load_dotenv
import pickle
from typing import List,Callable,Union
from fastapi import UploadFile
import google.genai as genai
from datetime import datetime

def gemini_client() -> genai.Client:
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return client

async def gemini_enviar_mensagem(
    id_usuario: str,
    id_chat: str,
    agente,
    prompt: str,
    anexos: List[UploadFile],  # ← CORREÇÃO AQUI
    modelo: str,
    tools: Union[List[Callable], Callable, None]) :
    '''
    Envia uma mensagem para o modelo Gemini e retorna a resposta.

    Args:
        id_usuario (str): ID do usuário.
        id_chat (str): ID do chat.
        prompt (str): Mensagem a ser enviada.
        anexos (List[str]): Lista de anexos.
        modelo (str): Modelo a ser utilizado.
        historico (List[str]): Histórico de mensagens.

    Returns:
        str: Resposta do modelo.
    '''
    #############################################
    # Cria o diretório do usuário se não existir
    if not os.path.exists(f"chats/{id_usuario}/{agente.nome}/"):
        os.makedirs(f"chats/{id_usuario}/{agente.nome}/")
    if f"{id_chat}.pkl" not in os.listdir(f"chats/{id_usuario}/{agente.nome}/"):
        arquivos_existentes = [
            nome for nome in os.listdir(f"chats/{id_usuario}/{agente.nome}/") 
            if nome.endswith(".pkl") and nome.startswith("Criado_")
        ]
        contador = len(arquivos_existentes)
        data_str = datetime.now().strftime("Criado_%d_%m_%Y")
        nome_arquivo = f"{data_str}_{contador}"
        with open(f"chats/{id_usuario}/{agente.nome}/{nome_arquivo}.pkl", "wb") as f:
            pickle.dump([], f)

        id_chat = nome_arquivo
    # Carrega o histórico do chat
    with open(f"chats/{id_usuario}/{agente.nome}/{id_chat}.pkl", "rb") as f:
        historico = pickle.load(f)
    #############################################

    client = gemini_client()
    #############################################
    if tools is None:
        config = genai.types.GenerateContentConfig()
    elif isinstance(tools, list):
        config = genai.types.GenerateContentConfig(
            tools=tools,
        )
    elif isinstance(tools, Callable):
        config = genai.types.GenerateContentConfig(
            tools=[tools],
        )
    ##############################################
    chat = client.chats.create(
        model=modelo,
        config=config,
        history=historico
    )

    message = [genai.types.Part.from_text(text=prompt)]
    if anexos:
        for anexo in anexos:
            print("Debug 1")
            content = await anexo.read()
            caminho = f"chats/{id_usuario}/{agente.nome}/{id_chat}/"
            os.makedirs(caminho, exist_ok=True)
            with open(f"{caminho}{anexo.filename}", "wb") as f:
                f.write(content)

           
            try:
                arquivo_upado = client.files.upload(
                    file=f"{caminho}/{anexo.filename}",
                    config={'mime_type': anexo.content_type}
                )

                message.append(genai.types.Part.from_uri(file_uri=arquivo_upado.uri,mime_type=arquivo_upado.mime_type))
            except Exception as e:
                print(f"Erro ao fazer upload do arquivo {anexo.filename}: {e}")
                return

    resposta = chat.send_message(message=message)
    historico = chat.get_history()

    with open(f"chats/{id_usuario}/{agente.nome}/{id_chat}.pkl", "wb") as f:
        pickle.dump(historico, f)

    return [resposta.text,id_chat]

def gemini_serializar_mensagem(obj):
    if isinstance(obj, list):
        return [gemini_serializar_mensagem(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return {k: gemini_serializar_mensagem(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: gemini_serializar_mensagem(v) for k, v in obj.items()}
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)  # fallback para objetos como Enum, etc.




