from fastapi import FastAPI, Response, status, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from instascrape import Post
from requests.cookies import cookiejar_from_dict
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://bianca-s-gourmet-356k.vercel.app/*"],  # Permitir a origem do frontend (Vue.js)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)
@app.get("/handle_redirect")
def handle_redirect(code: str):

    post = Post("https://www.instagram.com/p/C-OkdeTJjsZ/")

    post.scrape()

    comments = post.get_recent_comments()

    return comments


# Roda o servidor FastAPI
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
