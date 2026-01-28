import enum
from datetime import datetime

from . import Base, db

# class User(Base):
#
#     email = db.Column(db.String(320), nullable=False, index=True)
#     hashed_password = db.Column(db.String(255), nullable=False)
#     is_active = db.Column(db.Boolean, nullable=False, default=True)
#     created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
#     updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     __table_args__ = (db.UniqueConstraint("email", name="uq_users_email"),)
#
#
# class RefreshToken(Base):
#
#     user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
#     # Store refresh tokens by JTI (unique token id) so we can rotate/revoke without storing raw tokens
#     jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
#     revoked = db.Column(db.Boolean, nullable=False, default=False)
#     expires_at = db.Column(db.DateTime, nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
#
#     __table_args__ = (
#         db.Index("ix_refresh_tokens_user_id_revoked", "user_id", "revoked"),
#     )


class Product(Base):

    class UpdateType(enum.Enum):
        ADDITION = "ADDITION"
        REMOVAL = "REMOVAL"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # created_by = db.Column(db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # creator = db.relationship("User")
    inventory = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    inventory_updates = db.relationship(
        "InventoryUpdates",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,  # aligns with ondelete="CASCADE"
    )

    __table_args__ = (db.UniqueConstraint("name", name="uq_product_name"),)

    def update_inventory(
        self, quantity: int, type: UpdateType, reason_code: str = None
    ):
        """
        Update inventory and log the change.
        Inventory cannot be a negative number
        Args:
            quantity (int): The quantity to add or remove.
            type (UpdateType): The type of update (ADDITION or REMOVAL).
            reason_code (str, optional): Reason for the inventory change.
        """
        if type == self.UpdateType.ADDITION:
            self.inventory += quantity
        elif type == self.UpdateType.REMOVAL:
            if self.inventory - quantity < 0:
                raise ValueError("Inventory cannot be negative.")
            self.inventory -= quantity
        else:
            raise ValueError("Invalid update type.")

        update_record = InventoryUpdates(
            product_id=self.id,
            quantity=quantity if type == self.UpdateType.ADDITION else -quantity,
            reason_code=reason_code,
        )
        db.session.add(update_record)
        db.session.commit()


class InventoryUpdates(Base):

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product = db.relationship("Product", back_populates="inventory_updates")
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reason_code = db.Column(db.String(100), nullable=True)
    # updated_by = db.Column(db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
