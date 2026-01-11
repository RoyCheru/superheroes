from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


db = SQLAlchemy()

class Hero(db.Model, SerializerMixin):
    __tablename__ = "heroes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship(
        "HeroPower",
        back_populates="hero",
        cascade="all, delete-orphan"
    )

    powers = db.relationship(
        "Power",
        secondary="hero_powers",
        back_populates="heroes",
        viewonly=True
    )

    serialize_rules = ("-hero_powers.hero",)

class Power(db.Model, SerializerMixin):
    __tablename__ = "powers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship(
        "HeroPower",
        back_populates="power",
        cascade="all, delete-orphan"
    )

    heroes = db.relationship(
        "Hero",
        secondary="hero_powers",
        back_populates="powers",
        viewonly=True
    )

    serialize_rules = ("-hero_powers.power",)

    @validates("description")
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return value
    

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = "hero_powers"

    id = db.Column(db.Integer, primary_key=True)

    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(
        db.Integer,
        db.ForeignKey("heroes.id", ondelete="CASCADE"),
        nullable=False
    )

    power_id = db.Column(
        db.Integer,
        db.ForeignKey("powers.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    hero = db.relationship("Hero", back_populates="hero_powers")
    power = db.relationship("Power", back_populates="hero_powers")

    serialize_rules = ("-hero.hero_powers", "-power.hero_powers")

    @validates("strength")
    def validate_strength(self, key, value):
        if value not in ["Strong", "Weak", "Average"]:
            raise ValueError("Strength must be Strong, Weak, or Average")
        return value


