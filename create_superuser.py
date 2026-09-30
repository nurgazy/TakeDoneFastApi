import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

# Импортируем только engine, который точно есть в app.database
from app.database import engine
from app.models import User, UserRole
from app.security import hash_password

# Создаем фабрику сессий напрямую из движка
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_admin():
    email = input("Введите email администратора: ").strip()
    password = input("Введите пароль: ").strip()
    full_name = input("Введите имя (необязательно): ").strip() or None

    async with async_session_factory() as session:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Пользователь с таким email уже существует! Назначаем роль ADMIN...")
            existing_user.role = UserRole.ADMIN
            existing_user.is_active = True
            await session.commit()
            print("Роль успешно обновлена!")
            return

        user = User(
            email=email,
            hashed_password=await hash_password(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print(f"Администратор {email} успешно создан!")


if __name__ == "__main__":
    asyncio.run(create_admin())