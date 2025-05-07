from fastapi import APIRouter, Depends, Form, Request
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db.sessions import get_repository
from repositories.customers import CustomerRepository


router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {'request': request}
    )


@router.post('/search', response_class=HTMLResponse)
async def search_customer(
    *,
    phone_code: int = Form(...),
    tag: str = Form(...),
    limit=20,
    offset=0,
    request: Request,
    repository: CustomerRepository = Depends(get_repository(CustomerRepository)),
):
    customers = await repository.list(phone_code=phone_code, tag=tag, limit=limit, offset=offset)
    return templates.TemplateResponse(
        'search_results.html',
        {'request': request, 'customers': customers},
    )
