from fastapi import APIRouter, Query, HTTPException, status
from sqlalchemy.future import select
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaResumo

router = APIRouter()

@router.get(
    '/',
    summary='Consultar todos os Atletas (retorno customizado)',
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaResumo],
)
async def query(
    db_session: DatabaseDependency,
    nome: str | None = Query(None, description="Filtrar atletas pelo nome"),
    cpf: str | None = Query(None, description="Filtrar atletas pelo CPF")
) -> list[AtletaResumo]:
    """
    Retorna todos os atletas com filtros opcionais e resposta customizada:
    - nome
    - centro_treinamento
    - categoria
    """
    query_stmt = select(AtletaModel)

    if nome:
        query_stmt = query_stmt.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query_stmt = query_stmt.filter(AtletaModel.cpf == cpf)

    atletas = (await db_session.execute(query_stmt)).scalars().all()

    # Converte a lista de modelos SQLAlchemy para o formato de resposta desejado
    atletas_resumo = [
        AtletaResumo(
            nome=atleta.nome,
            centro_treinamento=atleta.centro_treinamento.nome,
            categoria=atleta.categoria.nome
        )
        for atleta in atletas
    ]

    return atletas_resumo
