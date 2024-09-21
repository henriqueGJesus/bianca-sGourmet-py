from fastapi import FastAPI, Response, status, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from requests.cookies import cookiejar_from_dict
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir a origem do frontend (Vue.js)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)
media_id = '1238261930922576'
client_secret = '7499887e6d7fb01466d03c5faeb694f1'
redirect_uri = 'https://bianca-s-gourmet-py-6p2c.vercel.app/handle_redirect'  # URL de redirecionamento
redrect_front = 'http://localhost:5173'


# Passo 1: Redirecionar o usuário para o Instagram para obter autorização
@app.get("/login")
def login():
    auth_url = "https://api.instagram.com/oauth/authorize"
    auth_params = {
        'client_id': media_id,
        'client_secret': client_secret,
        'redirect_uri': 'https://bianca-s-gourmet-py-6p2c.vercel.app/handle_redirect',
        'scope': 'user_profile',
        'response_type': 'code',
    }

    full_auth_url = requests.Request('GET', auth_url, params=auth_params).prepare().url

    return RedirectResponse(url=full_auth_url)


@app.get("/handle_redirect")
def handle_redirect(code: str):
    if not code:
        return {"error": "Código de autorização não fornecido"}

    # Trocar o código de autorização pelo token de acesso
    token_url = 'https://api.instagram.com/oauth/access_token'
    body_of_request_post = {
        'client_id': media_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }

    # Fazer a requisição para o Instagram para obter o token de acesso
    response_post = requests.post(token_url, data=body_of_request_post)
    response= ""
    if response_post.status_code == 200:
        # Sucesso, obtenha o token de acesso
        access_token_data = response_post.json()
        # Criar um dicionário para representar os cookies
        response = Response("Authentication successful", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=access_token_data['access_token'], httponly=True, secure=True,
                            samesite="Strict")
    retorno = get_media_ids(response.headers.get('Set-Cookie'))

    return retorno


# Função para obter os posts de um usuário e encontrar o media_id
@app.get("/get_media_ids")
def get_media_ids(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=403, detail="Acesso negado. Token de acesso não fornecido.")

    # URL da API para obter as mídias do usuário
    media_url = 'https://graph.instagram.com/me/media'
    params = {
        'access_token': access_token,
        'fields': 'id,caption,media_type,media_url'  # Os campos que queremos obter
    }

    # Fazer a requisição para obter as mídias
    response = requests.get(media_url, params=params)

    if response.status_code == 200:
        media_data = response.json()
        # Retorna os IDs de todas as mídias
        return media_data
    else:
        return {"error": "Erro ao obter mídias", "details": response.json()}


# Roda o servidor FastAPI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
