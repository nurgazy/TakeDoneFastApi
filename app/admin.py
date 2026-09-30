from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models import User  # импортируйте здесь ваши модели


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.email]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id]


def setup_admin(app: FastAPI, engine: AsyncEngine) -> Admin:
    admin = Admin(app=app, engine=engine, title="TakeDone Admin")
    admin.add_view(UserAdmin)
    return admin