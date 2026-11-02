from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Servidor funcionando."}

@router.get("/emails")
async def emails():
    return {"emails" : []}

@router.post("/login")
async def login():
    pass

@router.get("/resumir")
async def resumir():
    return {"Resumo": ""}

@router.get("/resposta")
async def responder():
    return {"Resposta": ""}