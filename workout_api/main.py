from fastapi import FastAPI
from workout_api.routers import api_router

app = FastAPI(title='WorkoutApi')
app.include_router(api_routerprefix="/atletas", tags=["Atletas"])

# 🧠 Adiciona suporte global à paginação
add_pagination(app)
