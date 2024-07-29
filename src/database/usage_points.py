"""Manage UsagePoints table in database."""

from datetime import datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import scoped_session

from const import TIMEZONE_UTC
from db_schema import (
    Addresses,
    ConsumptionDaily,
    ConsumptionDailyMaxPower,
    ConsumptionDetail,
    Contracts,
    ProductionDaily,
    ProductionDetail,
    Statistique,
    UsagePoints,
)

from . import DB


class UsagePointsConfig:  # pylint: disable=R0902
    """Default configuration for UsagePoints."""

    def __init__(self) -> None:
        self.usage_point_id: str = "------ SET_YOUR_USAGE_POINT_ID ------"
        self.enable: bool = True
        self.name: str = "Maison"
        self.token: str = "------- SET_YOUR_TOKEN --------"
        self.cache: bool = True
        self.consumption: bool = True
        self.consumption_detail: bool = True
        self.consumption_price_base: float = 0
        self.consumption_price_hc: float = 0
        self.consumption_price_hp: float = 0
        self.consumption_max_power: bool = True
        self.production: bool = False
        self.production_detail: bool = False
        self.production_price: float = 0
        self.offpeak_hours_0: str = None
        self.offpeak_hours_1: str = None
        self.offpeak_hours_2: str = None
        self.offpeak_hours_3: str = None
        self.offpeak_hours_4: str = None
        self.offpeak_hours_5: str = None
        self.offpeak_hours_6: str = None
        self.plan: str = "BASE"
        self.refresh_addresse: bool = False
        self.refresh_contract: bool = False
        self.consumption_max_date: datetime = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=1095)
        self.consumption_detail_max_date: datetime = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=1095)
        self.production_max_date: datetime = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=1095)
        self.production_detail_max_date: datetime = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=1095)
        self.call_number: int = 0
        self.quota_reached: bool = False
        self.quota_limit: bool = False
        self.quota_reset_at: datetime = None
        self.ban: bool = False
        self.consentement_expiration: datetime = None
        self.progress: int = 0
        self.progress_status: str = ""


class DatabaseUsagePoints:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id=None):
        """Initialize DatabaseConfig."""
        self.usage_point_id = usage_point_id
        self.session: scoped_session = DB.session()
        self.usage_point_config = None

    def get_all(self):
        """Get all data from usage point table."""
        query = select(UsagePoints)
        data = self.session.scalars(query).all()
        self.session.close()
        return data

    def get(self):
        """Get data from usage point table."""
        query = select(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id)
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def get_plan(
        self,
    ):
        """Get plan from usage point table."""
        data = self.get()
        if data.plan in ["HP/HC"]:
            return "HC/HP"
        return data.plan.upper()

    def set_value(self, key, value):
        """Set value in usage point table."""
        values = {key: value}
        self.session.execute(
            update(UsagePoints, values=values).where(UsagePoints.usage_point_id == self.usage_point_id)
        )
        self.session.flush()
        self.session.close()

    def set(self, data: dict) -> None:
        """Set data from usage point table."""
        query = select(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id)
        usage_points: UsagePoints = self.session.execute(query).scalar_one_or_none()
        if usage_points is not None:
            self.session.execute(
                update(UsagePoints, values=data).where(UsagePoints.usage_point_id == self.usage_point_id)
            )
        else:
            usage_points = UsagePoints(usage_point_id=self.usage_point_id)
            for key, value in data.items():
                setattr(usage_points, key, value)
            self.session.add(usage_points)
        self.session.flush()
        self.session.close()

    def progress(self, increment):
        """Update progress in database."""
        query = select(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        usage_points.progress = usage_points.progress + increment
        self.session.close()

    def last_call_update(self) -> None:
        """Update last call in database."""
        query = select(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        usage_points.last_call = datetime.now(tz=TIMEZONE_UTC)
        self.session.flush()
        self.session.close()

    def update(  # noqa: PLR0913
        self,
        consentement_expiration=None,
        call_number=None,
        quota_reached=None,
        quota_limit=None,
        quota_reset_at=None,
        last_call=None,
        ban=None,
    ) -> None:
        """Update usage point in database."""
        query = select(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        if consentement_expiration is not None:
            usage_points.consentement_expiration = consentement_expiration
        if call_number is not None:
            usage_points.call_number = call_number
        if quota_reached is not None:
            usage_points.quota_reached = quota_reached
        if quota_limit is not None:
            usage_points.quota_limit = quota_limit
        if quota_reset_at is not None:
            usage_points.quota_reset_at = quota_reset_at
        if last_call is not None:
            usage_points.last_call = last_call
        if ban is not None:
            usage_points.ban = ban
        self.session.flush()
        self.session.close()

    def delete(self) -> True:
        """Delete usage point from database."""
        self.session.execute(delete(Addresses).where(Addresses.usage_point_id == self.usage_point_id))
        self.session.execute(delete(Contracts).where(Contracts.usage_point_id == self.usage_point_id))
        self.session.execute(
            delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.usage_point_id == self.usage_point_id)
        )
        self.session.execute(delete(ConsumptionDetail).where(ConsumptionDetail.usage_point_id == self.usage_point_id))
        self.session.execute(delete(ConsumptionDaily).where(ConsumptionDaily.usage_point_id == self.usage_point_id))
        self.session.execute(delete(ProductionDetail).where(ProductionDetail.usage_point_id == self.usage_point_id))
        self.session.execute(delete(ProductionDaily).where(ProductionDaily.usage_point_id == self.usage_point_id))
        self.session.execute(delete(UsagePoints).where(UsagePoints.usage_point_id == self.usage_point_id))
        self.session.execute(delete(Statistique).where(Statistique.usage_point_id == self.usage_point_id))
        self.session.flush()
        self.session.close()
        return True

    def get_error_log(self):
        """Get error log in usage point table."""
        data = self.get()
        return data.last_error

    def set_error_log(self, message):
        """Set error log in usage point table."""
        values = {UsagePoints.last_error: message}
        self.session.execute(
            update(UsagePoints, values=values).where(UsagePoints.usage_point_id == self.usage_point_id)
        )
        self.session.flush()
        return True
