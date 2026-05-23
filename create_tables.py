from tax_gateway.app.core.config import Config
from tax_gateway.app.db.session import init_db, get_engine
from tax_gateway.app.db.models import Base


def init_models():
    init_db(Config.SQLALCHEMY_DATABASE_URI)
    print("Создаем таблицы...")
    Base.metadata.create_all(get_engine())
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    init_models()