from fastapi import FastAPI
from server.rotes.rotes import router

app = FastAPI()
app.include_router(router, prefix="/trabalho") #prefixo adicionado para servir como raiz para acessar todas as rotas