# PLANO DO PROJETO (explicado fácil)

## O que a gente está fazendo?
Um **bot do Telegram** que mexe no seu Gmail. Você **escreve** pra ele (só texto, sem voz), e ele:
- lê seus e-mails
- diz quais são importantes
- faz um resumo curto
- sugere uma resposta

## Como as peças se encaixam (desenho)

```
[Você no Telegram] <-> BOT (recebe e manda mensagens)
                         |
                         v
                      SERVER (FastAPI, o cérebro)
                         |
          +--------------+--------------+
          v                             v
   Gmail (e-mails)              llama-server (a IA)
```

- **Bot** = o programa que conversa com você no Telegram.
- **Server** = o cérebro. Recebe o pedido do bot, mexe no Gmail e pergunta pra IA.
- **llama-server** = a IA (gpt-oss-20b) rodando no próprio PC. O arquivo `server/modelAI/llamacpp.py` já conversa com ela.
- **Gmail API** = a porta que o Google dá pra gente mexer no e-mail.

## O que precisa ter instalado

**Programas e contas**
- Python 3.10 ou mais novo e Git
- llama.cpp com um modelo `.gguf` (já temos o gpt-oss-20b rodando na porta 8888)
- Um bot no Telegram: falar com o `@BotFather`, criar o bot e copiar o token
- Uma conta Google com projeto no Google Cloud (Gmail API ligada e `credentials.json`)
- Um jeito de deixar o server acessível na internet pro Google devolver o login (ngrok ou Cloudflare Tunnel), só enquanto estiver testando

**Bibliotecas Python (`pip install -r requirements.txt`)**
| Biblioteca | Pra que serve |
|---|---|
| `python-telegram-bot` | fazer o bot do Telegram |
| `google-api-python-client` | falar com o Gmail |
| `google-auth-oauthlib` e `google-auth-httplib2` | botão "Entrar com o Google" |
| `fastapi` e `uvicorn` | montar e rodar o server |
| `pydantic` | conferir se os dados estão no formato certo |
| `httpx` | falar com o llama-server e com o server |
| `cryptography` | trancar os tokens antes de guardar |
| `beautifulsoup4` | limpar o HTML dos e-mails |
| `python-dotenv` | guardar senhas e tokens fora do código (`.env`) |
| `pytest` | testes |

O banco de dados é o SQLite, que já vem com o Python.

---

## O que precisa ser feito

### 1. Login do Google (cada pessoa com a sua conta) 
- O usuário manda `/login` pro bot. O bot responde com um link do Google.
- A pessoa entra no link, autoriza, e o Google devolve o resultado pro server (rota `/oauth/callback`).
- O link leva um código secreto (`state`) que liga o login àquele usuário do Telegram. Sem isso, a conta de um poderia cair no outro.
- O Google só devolve pra um endereço da internet (ver ngrok acima).
- Pedir só as permissões necessárias (ler, modificar, enviar).

### 2. Guardar o login de cada usuário (charlito)
- Banco SQLite com: id do Telegram, token do Google.
- O token é trancado (`cryptography`) antes de salvar. A chave fica no `.env`.
- Renovar o token quando vencer.
- Comando `/logout` apaga tudo daquele usuário.

### 3. Ler e mexer no Gmail (ana)
- Listar e-mails (não lidos, últimos 10, buscar por nome ou assunto).
- Abrir um e-mail e tirar o texto limpo (sem HTML, sem assinatura e sem citações).
- Criar rascunho, enviar, marcar como lido, arquivar.
- Fazer também e-mails falsos (mock) pra testar sem Gmail de verdade.

### 4. A IA — **já pronta** (joao cappellari)
- `server/modelAI/llamacpp.py` com `perguntar_ia()` e `perguntar_ia_stream()`. Não precisa mudar.

### 5. Resumir e sugerir resposta (joao cappellari)
- Prompts: "resuma este e-mail em até 3 linhas" e "sugira uma resposta educada e curta, em português" (formal ou informal).
- A IA devolve em formato fixo (JSON) pra o programa entender.
- Testar com 20 e-mails falsos e ajustar.

### 6. Detectar e-mail importante + entender o pedido
- Regras simples: remetente conhecido, palavras como "urgente", "prazo", "reunião" = importante; propaganda = não.
- A IA dá nota de 0 a 10 e diz o motivo.
- Entender frases soltas: "leia meu último e-mail" → LER; "responde dizendo que sim" → RESPONDER; "o que tem de importante?" → LISTAR_IMPORTANTES.

### 7. Server (FastAPI) (joao vitor)
- Rotas: `/chat`, `/emails`, `/resumir`, `/responder`, `/oauth/callback`.
- Juntar os itens 1 a 6 dentro dele.
- Responder com erro claro se o login faltar (403) ou a IA estiver fora (503).

### 8. Bot do Telegram (charlito)
- Comandos: `/start`, `/login`, `/emails`, `/importantes`, `/resumir`, `/logout`.
- Mensagem normal (sem comando) vai pro `/chat` do server.
- Antes de enviar qualquer e-mail, mostrar a resposta com botões **Enviar / Editar / Cancelar**.
- O Telegram aceita no máximo 4096 caracteres por mensagem: dividir as longas.
- Mostrar "digitando..." enquanto a IA pensa.

### 9. Segurança
- Lista de usuários permitidos (só gente do grupo usa o bot).
- **Nunca enviar e-mail sem o usuário apertar "Enviar".**
- `credentials.json`, `.env`, token do bot e o banco no `.gitignore`.
- O app do Google fica em modo "Testing": só e-mails cadastrados como "usuário de teste" entram.

### 10. Testes e README
- Testar cada parte sozinha com e-mails falsos.
- Depois testar tudo junto com Gmail de verdade.
- README: como instalar, criar o bot, configurar o Google Cloud e o ngrok.

---

## Em que ordem fazer

1. **Combinar:** nomes das funções e pastas. Cada parte usa e-mails falsos.
2. **Partes separadas:** itens 1, 2, 3, 5, 6 e 8 não dependem uns dos outros (o 4 já está pronto).
3. **Juntar:** item 7 junta tudo. Testar pelo Telegram só com texto.
4. **Arrumar:** testar com Gmail de verdade, consertar bugs, README.

## Pastas sugeridas
```
server/    -> main.py, gmail_auth.py, gmail_service.py, llamacpp.py,
              resumo.py, resposta.py, importancia.py, intencao.py, db.py
bot/       -> bot.py (Telegram)
tests/     -> testes de cada parte
```

## Regras pra não dar briga
- Cada um trabalha na **sua branch** do Git e abre Pull Request.
- Nunca subir senha, token ou `credentials.json`.
- Cada função tem que ter um exemplo de uso escrito em comentário.
- Dúvida? Pergunta no grupo antes de ficar 1 dia travado.

## Cuidados
- Tudo da IA roda no PC, então os e-mails não vão pra nenhuma empresa de IA (só Gmail e Telegram são na internet).
- Mensagens no Telegram não são criptografadas de ponta a ponta nos bots: não mandar dados muito sensíveis.
