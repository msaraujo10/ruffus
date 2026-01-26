from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
engine_ref = None

# Permitir qualquer origem (apenas em ambiente local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/snapshot")
def snapshot():
    if engine_ref is None:
        return {"error": "Engine not attached"}
    return engine_ref.cognitive_snapshot()
