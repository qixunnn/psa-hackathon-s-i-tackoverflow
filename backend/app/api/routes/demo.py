from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.models.responses import (
    DemoArticleSummary,
    ErrorDetail,
    ErrorResponse,
    ProcessArticleResponse,
)
from app.services.demo_replay_service import (
    ArticleAlreadyProcessedError,
    DemoArticleNotFoundError,
    DemoReplayService,
    get_demo_replay_service,
)


router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/articles", response_model=list[DemoArticleSummary])
def list_demo_articles(
    service: Annotated[DemoReplayService, Depends(get_demo_replay_service)],
) -> list[DemoArticleSummary]:
    return service.list_articles()


@router.post(
    "/replay/{articleId}",
    response_model=ProcessArticleResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def replay_demo_article(
    articleId: str,
    service: Annotated[DemoReplayService, Depends(get_demo_replay_service)],
) -> ProcessArticleResponse | JSONResponse:
    try:
        return service.replay(articleId)
    except DemoArticleNotFoundError:
        error = ErrorResponse(
            error=ErrorDetail(
                code="ARTICLE_NOT_FOUND",
                message="The requested demo article could not be found.",
                details=None,
            )
        )
        return JSONResponse(status_code=404, content=error.model_dump(mode="json"))
    except ArticleAlreadyProcessedError as exception:
        error = ErrorResponse(
            error=ErrorDetail(
                code="ARTICLE_DUPLICATE",
                message="This article has already been processed.",
                details={"existingArticleId": exception.article_id},
            )
        )
        return JSONResponse(status_code=409, content=error.model_dump(mode="json"))
