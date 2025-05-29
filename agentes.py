from typing import Callable, List,Union
import pickle
from pydantic import BaseModel
class Agente:
    def __init__(self, nome:str,descricao:str,prompt_base:Union[str,None], arquivos_base:Union[str,List[str],None],ferramentas:Union[List[Callable],Callable,None],formato_output:Union[BaseModel,None]):
        self.nome = nome
        self.descricao = descricao
        self.ferramentas = ferramentas
        self.prompt_base = prompt_base
        self.arquivos_base = arquivos_base
        self.formato_output = formato_output

    def carregar(nome:str):
        try:
            with open(f"agentes/{nome}.pkl", "rb") as f:
                agente = pickle.load(f)
                return agente
        except FileNotFoundError:
            print(f"Agente {nome} não encontrado.")
            return None
        except Exception as e:
            print(f"Erro ao carregar o agente: {e}")
            return None
        
    def salvar(self):
        with open(f"agentes/{self.nome}.pkl", "wb") as f:
            pickle.dump(self, f)
