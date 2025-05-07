from datetime import datetime

from db.sessions import get_async_session
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.mailouts import MailoutRepository
from repositories.phone_codes import PhoneCodeRepository
from repositories.tags import TagRepository
from schemas.mailouts import Mailout, MailoutCreate, MailoutRead
from schemas.phone_codes import PhoneCode
from schemas.tags import Tag
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/admin", tags=["Admin"])

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def admin_root(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/mailouts", response_model=list[MailoutRead])
async def list_mailouts(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    mailout_repo = MailoutRepository(session)
    mailouts = await mailout_repo.list(limit=100)  # Get up to 100 mailouts for now
    return templates.TemplateResponse(
        "admin/mailouts_list.html", {"request": request, "mailouts": mailouts}
    )


@router.get("/mailouts/create")
async def create_mailout_form(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    tag_repo = TagRepository(session)
    phone_code_repo = PhoneCodeRepository(session)
    tags = await tag_repo.list(Tag, limit=1000)
    phone_codes = await phone_code_repo.list(limit=1000)
    return templates.TemplateResponse(
        "admin/mailout_create.html",
        {"request": request, "tags": tags, "phone_codes": phone_codes},
    )


@router.post("/mailouts/create")
async def create_mailout(
    request: Request,
    text_message: str = Form(...),
    start_at: datetime = Form(...),
    finish_at: datetime = Form(...),
    local_time_start_hour: int = Form(None),
    local_time_end_hour: int = Form(None),
    tag_ids: list[int] = Form([]),
    phone_code_ids: list[int] = Form([]),
    session: AsyncSession = Depends(get_async_session),
):
    mailout_repo = MailoutRepository(session)
    tag_repo = TagRepository(session)
    phone_code_repo = PhoneCodeRepository(session)

    mailout_data = MailoutCreate(
        text_message=text_message,
        start_at=start_at,
        finish_at=finish_at,
        local_time_start_hour=local_time_start_hour,
        local_time_end_hour=local_time_end_hour,
    )

    try:
        # Create the basic mailout object
        created_mailout_read = await mailout_repo.create(mailout_data)

        # Fetch the actual ORM model instance to update relationships
        db_mailout = await mailout_repo.get(Mailout, model_id=created_mailout_read.id)
        if not db_mailout:
            raise HTTPException(
                status_code=404, detail="Newly created mailout not found"
            )

        # Process and link tags
        if tag_ids:
            db_mailout.tags = []  # Clear existing, if any (should be none for new mailout)
            for tag_id in tag_ids:
                tag = await tag_repo.get(Tag, model_id=tag_id)
                if tag:
                    db_mailout.tags.append(tag)

        # Process and link phone codes
        if phone_code_ids:
            db_mailout.phone_codes = []  # Clear existing
            for pc_id in phone_code_ids:
                phone_code = await phone_code_repo.get(PhoneCode, model_id=pc_id)
                if phone_code:
                    db_mailout.phone_codes.append(phone_code)

        session.add(db_mailout)
        await session.commit()
        await session.refresh(db_mailout)

    except Exception as e:
        await session.rollback()  # Rollback in case of error
        # Consider more specific error logging here
        raise HTTPException(status_code=500, detail=f"Error creating mailout: {str(e)}")

    return RedirectResponse(url="/admin/mailouts", status_code=303)
