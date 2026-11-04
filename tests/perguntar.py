# da pra usar pra fazer perguntas e testar agora
# USO: 
# precisa do modulo httpx e estar na raiz do projeto
# após instalar o moculo pode usar o comando e fazer a pergunta que quiser 
# esse script se comunica com o llamacpp.py e faz a requisição do que tu falou
# comando: python -m tests.perguntar "prompt"


import sys

from server.modelAI.llamacpp import perguntar_ia_stream

def main():
    query = " ".join(sys.argv[1:]) or input("Pergunta: ")
    for pedacin in perguntar_ia_stream(query):
        print(pedacin, end="", flush=True)
    print()
# sera?
if __name__ == "__main__":
    main()
