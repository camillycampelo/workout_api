from fastapi import APIRouter, Query, HTTPException, status
from sqlalchemy.future import select
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaResumo
from sqlalchemy.exc import IntegrityError
from workout_api.atleta.schemas import AtletaIn, AtletaOut

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

router = APIRouter()

@router.post(
    '/',
    summary='Criar um novo Atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def create(db_session: DatabaseDependency, atleta_in: AtletaIn) -> AtletaOut:
    """
    Cria um novo atleta no banco de dados.
    Caso o CPF já esteja cadastrado, retorna status 303 e mensagem personalizada.
    """
    try:
        atleta = AtletaModel(**atleta_in.model_dump())
        db_session.add(atleta)
        await db_session.commit()
        await db_session.refresh(atleta)
        return atleta

    except IntegrityError as e:
        await db_session.rollback()

        # 🧠 Detecta se o erro está relacionado ao CPF
        if "cpf" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
            )

        # Caso seja outro tipo de erro de integridade
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro de integridade nos dados fornecidos."
        )
