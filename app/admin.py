from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from starlette.requests import Request

from app.config import settings
from app.models import User, UserRole
from app.security import verify_password


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str, engine: AsyncEngine):
        super().__init__(secret_key=secret_key)
        self.session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        async with self.session_factory() as session:
            # Ищем пользователя по email
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            # Проверяем пароль, активность и роль ADMIN
            if not user or not user.is_active:
                return False

            if user.role != UserRole.ADMIN:
                return False

            if not await verify_password(password, user.hashed_password):
                return False

            # Сохраняем сессию пользователя
            request.session.update({"user_id": user.id})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        async with self.session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or not user.is_active or user.role != UserRole.ADMIN:
                return False

        return True


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    # Не показываем хэш пароля в таблице
    column_list = [User.id, User.email, User.full_name, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.id, User.role, User.created_at]
    form_excluded_columns = [User.created_at]


def setup_admin(app: FastAPI, engine: AsyncEngine) -> Admin:
    # Передаем authentication_backend в Admin
    authentication_backend = AdminAuth(secret_key=settings.secret_key, engine=engine)
    admin = Admin(
        app=app,
        engine=engine,
        title="TakeDone Admin",
        authentication_backend=authentication_backend,
    )
    admin.add_view(UserAdmin)
    return admin