import asyncio
from tax_gateway.app.db.session import engine
from tax_gateway.app.db.models import Base

async def init_models():
    async with engine.begin() as conn:
        print("Создаем таблицы...")
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_models())