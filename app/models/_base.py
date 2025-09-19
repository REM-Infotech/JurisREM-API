from sqlalchemy import func

from app import db


class BaseModel(db.Model):
    """Implemente funcionalidades comuns a todos os modelos da aplicação."""

    __abstract__ = True  # Esta classe não criará tabela no banco de dados

    # Campos de auditoria presentes em todas as tabelas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def save(self):
        """Salve o objeto atual no banco de dados."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Remova o objeto atual do banco de dados."""
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        """Atualize campos do objeto com os valores fornecidos."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def to_dict(self):
        """Converta o objeto para dicionário Python."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
