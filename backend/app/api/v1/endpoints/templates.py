"""Agent template endpoints for the public alpha."""
from fastapi import APIRouter, Depends

from ....core.dependencies import get_public_alpha_service
from ....models import AgentTemplate
from ....services.public_alpha_service import PublicAlphaService


router = APIRouter()


@router.get("/agents", response_model=list[AgentTemplate], summary="Listar agent templates")
def list_agent_templates(
    service: PublicAlphaService = Depends(get_public_alpha_service),
):
    """Return the curated agent templates used in the public alpha."""
    return service.list_templates()
