# PLANO DO PROJETO (explicado fácil)

## O que a gente está fazendo?
Um robô que mexe no seu e-mail do Gmail. Você **fala ou escreve** pra ele, e ele:
- lê seus e-mails
- diz quais são importantes
- faz um resumo curto
- sugere uma resposta

A **tela (UI)** quem faz é a IA. Aqui só tem o resto.

## Como as peças se encaixam (desenho)

```
[Você fala] -> CLIENT (ouvido: voz vira texto) -> manda texto -> SERVER (cérebro)
                                                                    |
                                  Gmail <- pega e-mails <-----------+-> LLM (a IA que pensa)
                                                                    |
[Você escuta] <- CLIENT (boca: texto vira voz) <- recebe resposta <-+
```

- **Client** = o que fica no computador da pessoa. Tem ouvido e boca.
- **Server** = o cérebro. Recebe o texto, pensa, responde.
- **LLM** = a inteligência artificial (llama.cpp), roda no próprio PC.
- **Gmail API** = a porta que o Google dá pra gente mexer no e-mail (biblioteca `google-api-python-client`).

## O que precisa ter instalado

**Programas**
- Python 3.10 ou mais novo
- Git
- llama.cpp (roda a IA) e um modelo `.gguf` (ex: Qwen2.5 7B Instruct Q4_K_M)
- Uma conta Google com projeto no Google Cloud (Gmail API ligada e `credentials.json`)
- Um microfone e uma caixa de som/fone

**Bibliotecas Python (`pip install`)**
| Biblioteca | Pra que serve |
|---|---|
| `google-api-python-client` | falar com o Gmail |
| `google-auth-oauthlib` e `google-auth-httplib2` | botão "Entrar com o Google" |
| `keyring` | guardar o token com segurança |
| `fastapi` e `uvicorn` | montar e rodar o server |
| `pydantic` | conferir se os dados estão no formato certo |
| `httpx` ou `requests` | o client conversar com o server |
| `websockets` | resposta chegando aos poucos (opcional) |
| `llama-cpp-python` | usar o llama.cpp dentro do Python (ou rodar o `llama-server` e chamar por HTTP) |
| `faster-whisper` | ouvido: voz vira texto |
| `kokoro` e `soundfile` | boca: texto vira voz |
| `sounddevice` e `numpy` | gravar e tocar áudio |
| `openwakeword` | chamar por "Jarvis" (opcional) |
| `beautifulsoup4` | limpar o HTML dos e-mails |
| `python-dotenv` | guardar configurações fora do código |
| `pytest` | testes |

> O Kokoro SÓ fala, não ouve. Pra ouvir usa o `faster-whisper`.

---

## O que precisa ser feito

### 1. Login do Google
Fazer o botão "Entrar com o Google" funcionar e guardar o crachá.
- Criar o projeto no Google Cloud e ligar a Gmail API (pegar o arquivo `credentials.json`).
- Fazer o login abrir a janela do Google (`google-auth-oauthlib`).
- Salvar o token num lugar seguro (biblioteca `keyring`), **nunca no GitHub**.
- Renovar o token quando vencer.
- Resultado: função `login()` que devolve "pode usar o Gmail".

### 2. Ler e mexer no Gmail
Pegar e-mails e mandar e-mails.
- Listar e-mails (não lidos, últimos 10, buscar por nome ou assunto).
- Abrir um e-mail e tirar o texto limpo (o e-mail vem bagunçado, com HTML; deixar só o texto).
- Criar rascunho e enviar e-mail.
- Marcar como lido, arquivar.
- Resultado: arquivo `gmail_service.py` com essas funções + e-mails falsos (mock) pra todo mundo testar.

### 3. A IA (llama.cpp)
Fazer a IA rodar e responder.
- Baixar um modelo (sugestão: Qwen2.5 7B ou Llama 3.1 8B, versão GGUF Q4) e rodar com llama.cpp.
- Deixar o modelo trocável por configuração (pra comparar modelos sem mexer no código).
- Criar função `perguntar_ia(texto)` que devolve a resposta.
- Fazer a resposta chegar aos poucos (palavra por palavra, "streaming").
- Resultado: arquivo `llm.py` e documento explicando como instalar o modelo.

### 4. Resumir e sugerir resposta
Ensinar a IA a fazer as tarefas de e-mail.
- Escrever os prompts: "resuma este e-mail em até 3 linhas".
- Escrever o prompt de sugerir resposta (educada, curta, em português; opção de tom formal ou informal).
- Fazer a IA devolver resposta em formato fixo (JSON) pra o programa entender.
- Testar com 20 e-mails falsos e ajustar até ficar bom.
- Resultado: `resumo.py` e `resposta.py` (usam a função `perguntar_ia`).

### 5. Detectar e-mail importante + entender o pedido
Decidir o que é importante e entender o que o usuário quis dizer.
- Regras simples: remetente conhecido, palavras como "urgente", "prazo", "reunião" = importante; propaganda e newsletter = não importante.
- Pedir pra IA dar nota de 0 a 10 de importância e dizer o motivo.
- Entender frases: "leia meu último e-mail" → ação LER; "responde dizendo que sim" → ação RESPONDER; "o que tem de importante?" → ação LISTAR_IMPORTANTES.
- Regra de segurança: **nunca enviar e-mail sem o usuário confirmar** ("Quer mesmo enviar?").
- Resultado: `importancia.py` e `intencao.py`.

### 6. Server (FastAPI)
Ligar todas as peças.
- Montar o server com FastAPI: rotas `/chat`, `/emails`, `/resumir`, `/responder`, `/login`.
- Juntar os itens 1 a 5 dentro do server.
- Resultado: pasta `server/` rodando.

### 7. Voz (no client)
Dar ouvido e boca ao robô.
- Gravar o microfone e transformar em texto (STT, `faster-whisper`).
- Transformar a resposta em voz (TTS, `Kokoro`) e tocar o áudio.
- Mandar o texto pro server e receber a resposta.
- Opcional (extra): chamar pelo nome "Jarvis" (wake word, `openWakeWord`).
- Resultado: `client/voz.py`.

### 8. Testes e README
- Testar cada parte sozinha com e-mails falsos.
- Testar tudo junto, primeiro digitando, depois falando, depois com Gmail de verdade.
- Escrever o README explicando como instalar e rodar.

---

## Em que ordem fazer

1. **Combinar:** decidir os nomes das funções e as pastas (ver abaixo). Cada parte é feita usando e-mails falsos.
2. **Fazer as partes separadas:** itens 1 a 5 e 7 não dependem uns dos outros.
3. **Juntar:** item 6 junta tudo. Testar digitando.
4. **Voz e arrumar:** ligar a voz, testar com Gmail de verdade, consertar bugs, escrever o README.

## Pastas sugeridas
```
server/    -> main.py, gmail_auth.py, gmail_service.py, llm.py,
              resumo.py, resposta.py, importancia.py, intencao.py
client/    -> voz.py e a tela (feita pela IA)
tests/     -> testes de cada parte
```

## Regras pra não dar briga
- Cada um trabalha na **sua branch** do Git e abre Pull Request.
- Nunca subir `credentials.json`, token ou senha (colocar no `.gitignore`).
- Cada função tem que ter um exemplo de uso escrito em comentário.
- Dúvida? Pergunta no grupo antes de ficar 1 dia travado.

## Cuidados
- O app do Google fica em modo "Testing": só e-mails cadastrados como "usuário de teste" conseguem entrar.
- Tudo da IA roda no PC, então os e-mails não vão pra nenhuma empresa de IA (só o Gmail em si é na internet).
