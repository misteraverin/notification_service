from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from db.errors import UserCredentialsError
from db.sessions import get_session, get_repository
from repositories.users import UserRepository
from schemas.tokens import Token
from schemas.users import User, UserRead

URL_PREFIX = '/auth'
router = APIRouter(prefix=URL_PREFIX)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{URL_PREFIX}/token')


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_repository(UserRepository)),
) -> UserRead:
    try:
        return await repository.get(token)
    except UserCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )


@router.post(
    '/token',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    name='login_user',
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repository: UserRepository = Depends(get_repository(UserRepository)),
):
    try:
        return await repository.login(form_data)
    except UserCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password',
        )
