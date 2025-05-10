from datetime import datetime

from db.sessions import get_repository
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.mailouts import MailoutRepository
from repositories.messages import MessageRepository
from repositories.phone_codes import PhoneCodeRepository
from repositories.tags import TagRepository
from schemas.mailouts import Mailout, MailoutCreate, MailoutRead, MailoutUpdate
from schemas.phone_codes import PhoneCodeCreate
from schemas.tags import TagCreate
from utils.logging import logger

# We might need User for create/update later if API requires authentication for repo actions
# from schemas.users import User
# from routers.users import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin UI"],
    default_response_class=HTMLResponse,
)

# This assumes you have templates configured in your main app instance
# If you named your Jinja2Templates instance something other than 'templates' in main.py,
# you might need to pass it around or re-initialize it here.
# For simplicity, we'll rely on it being available via Request.app.state.templates or similar
# or ensure main.py's 'templates' object is accessible here.

# A more robust way if 'templates' is globally available in main.py:
# from main import templates # This might cause circular import issues depending on structure

# Let's assume 'templates' is correctly set up in main.py and accessible via Request for now.
# If not, we'll adjust. For now, we will instantiate it directly here for this router.
# This duplicates the setup from main.py but ensures this router is self-contained for now.
# In a larger app, you'd typically pass the templates instance or configure it globally.
templates = Jinja2Templates(directory="templates")


@router.get("/", name="admin_root")
async def admin_root_page(
    request: Request,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
):
    mailouts: list[MailoutRead] = await repository.list(limit=100, offset=0)
    return templates.TemplateResponse(
        "admin/list_mailouts.html", {"request": request, "mailouts": mailouts}
    )


@router.get("/mailouts", name="list_mailouts_admin")
async def list_mailouts_admin(
    request: Request,
    repository: MailoutRepository = Depends(get_repository(MailoutRepository)),
):
    mailouts: list[MailoutRead] = await repository.list(limit=100, offset=0)
    return templates.TemplateResponse(
        "admin/list_mailouts.html", {"request": request, "mailouts": mailouts}
    )


@router.get("/mailouts/create", name="create_mailout_form_admin")
async def create_mailout_form_admin(request: Request):
    return templates.TemplateResponse("admin/create_mailout.html", {"request": request})


@router.get("/mailouts/{mailout_id}", name="view_mailout_admin", response_model=None)
async def view_mailout_admin(
    request: Request,
    mailout_id: int,
    mailout_repo: MailoutRepository = Depends(get_repository(MailoutRepository)),
):
    mailout: MailoutRead | None = await mailout_repo.get(model_id=mailout_id)
    if not mailout:
        raise HTTPException(
            status_code=404, detail=f"Mailout with ID {mailout_id} not found."
        )

    # To display messages, MailoutRead should already have them if the relationship is eager-loaded
    # or if they are accessed (triggering a lazy load which should work in an async context here).
    # If messages are not loaded, we might need to explicitly fetch them or adjust the repository get method.
    # For now, assuming mailout.messages will be populated.

    return templates.TemplateResponse(
        "admin/view_mailout_details.html", {"request": request, "mailout": mailout}
    )


@router.get(
    "/mailouts/{mailout_id}/edit", name="edit_mailout_form_admin", response_model=None
)
async def edit_mailout_form_admin(
    request: Request,
    mailout_id: int,
    mailout_repo: MailoutRepository = Depends(get_repository(MailoutRepository)),
):
    mailout = await mailout_repo.get(model_id=mailout_id)
    if not mailout:
        raise HTTPException(
            status_code=404, detail=f"Mailout with ID {mailout_id} not found."
        )
    return templates.TemplateResponse(
        "admin/edit_mailout.html", {"request": request, "mailout": mailout}
    )


@router.post(
    "/mailouts/{mailout_id}/edit", name="handle_edit_mailout_admin", response_model=None
)
async def handle_edit_mailout_admin(
    request: Request,
    mailout_id: int,
    mailout_repo: MailoutRepository = Depends(get_repository(MailoutRepository)),
    start_at_str: str = Form(..., alias="start_time"),
    finish_at_str: str = Form(..., alias="end_time"),
    text_message: str = Form(..., alias="message_text"),
    available_start_at_str: str = Form(None, alias="available_start_at"),
    available_finish_at_str: str = Form(None, alias="available_finish_at"),
):
    try:
        start_at = datetime.fromisoformat(start_at_str)
        finish_at = datetime.fromisoformat(finish_at_str)

        available_start_at = None
        if available_start_at_str:
            available_start_at = datetime.strptime(
                available_start_at_str, "%H:%M"
            ).time()

        available_finish_at = None
        if available_finish_at_str:
            available_finish_at = datetime.strptime(
                available_finish_at_str, "%H:%M"
            ).time()

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime or time format. Please use YYYY-MM-DDTHH:MM for datetimes and HH:MM for times.",
        )

    mailout_update_data = MailoutUpdate(
        start_at=start_at,
        finish_at=finish_at,
        text_message=text_message,
        available_start_at=available_start_at,
        available_finish_at=available_finish_at,
    )

    updated_mailout = await mailout_repo.update(
        model_id=mailout_id, model_update=mailout_update_data
    )
    if not updated_mailout:
        raise HTTPException(
            status_code=404,
            detail=f"Mailout with ID {mailout_id} not found during update or update failed.",
        )

    return RedirectResponse(url=request.url_for("list_mailouts_admin"), status_code=303)


@router.post("/mailouts/create", name="handle_create_mailout_admin")
async def handle_create_mailout_admin(
    request: Request,
    mailout_repo: MailoutRepository = Depends(get_repository(MailoutRepository)),
    tag_repo: TagRepository = Depends(get_repository(TagRepository)),
    phone_code_repo: PhoneCodeRepository = Depends(get_repository(PhoneCodeRepository)),
    start_at_str: str = Form(..., alias="start_time"),
    finish_at_str: str = Form(..., alias="end_time"),
    text_message: str = Form(..., alias="message_text"),
    filter_tag: str = Form(None, alias="filter_tag"),
    filter_operator_code: str = Form(None, alias="filter_operator_code"),
    # user: User = Depends(get_current_user)
):
    try:
        start_at = datetime.fromisoformat(start_at_str)
        finish_at = datetime.fromisoformat(finish_at_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Please use YYYY-MM-DDTHH:MM.",
        )

    mailout_data = MailoutCreate(
        start_at=start_at,
        finish_at=finish_at,
        text_message=text_message,
    )

    created_mailout: MailoutRead = await mailout_repo.create(model_create=mailout_data)
    mailout_id_for_logging = (
        created_mailout.id if created_mailout else None
    )  # Get ID for logging

    if mailout_id_for_logging:
        # Associate Tag if provided
        if filter_tag and filter_tag.strip():
            try:
                tag_create_schema = TagCreate(tag=filter_tag.strip())
                await tag_repo.create(
                    model_id=mailout_id_for_logging,
                    tag_create=tag_create_schema,
                    parent_model=Mailout,
                )
            except Exception as e:
                logger.error(
                    f"Error associating tag '{filter_tag}' with mailout {mailout_id_for_logging}: {e}"
                )

        # Associate Phone Code if provided
        if filter_operator_code and filter_operator_code.strip():
            try:
                phone_code_create_schema = PhoneCodeCreate(
                    phone_code=filter_operator_code.strip()
                )
                await phone_code_repo.create(
                    model_create=phone_code_create_schema,
                    parent_model=Mailout,
                    model_id=mailout_id_for_logging,
                )
            except Exception as e:
                logger.error(
                    f"Error associating phone code '{filter_operator_code}' with mailout {mailout_id_for_logging}: {e}"
                )
    else:
        logger.error(
            "Failed to create mailout or retrieve its ID for tag/code association."
        )

    return RedirectResponse(url=request.url_for("list_mailouts_admin"), status_code=303)


@router.get("/statistics", name="view_statistics_admin")
async def view_statistics_admin(
    request: Request,
    mailout_repo: MailoutRepository = Depends(get_repository(MailoutRepository)),
    message_repo: MessageRepository = Depends(get_repository(MessageRepository)),
):
    total_mailouts = await mailout_repo.count_all()
    total_messages = await message_repo.count_all()

    message_stats_raw = (
        await message_repo.get_general_stats()
    )  # Returns list of (status_enum, count)

    # Convert status_enum (which is likely an Enum member) to its string value for the template
    messages_by_status = {
        str(status.value if hasattr(status, "value") else status): count
        for status, count in message_stats_raw
    }

    stats_data = {
        "total_mailouts": total_mailouts,
        "total_messages_sent": total_messages,
        "messages_by_status": messages_by_status,
    }
    return templates.TemplateResponse(
        "admin/view_statistics.html", {"request": request, "statistics": stats_data}
    )


# We'll need to create the actual HTML template files next.
