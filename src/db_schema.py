"""This module defines the database schema for the application."""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()  # Required


class Config(Base):
    __tablename__ = "config"

    key = Column(Text, primary_key=True, index=True, unique=True)
    value = Column(Text, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.value


class UsagePoints(Base):
    __tablename__ = "usage_points"

    usage_point_id = Column(Text, primary_key=True, unique=True, nullable=False, index=True)

    name = Column(Text, nullable=False)
    cache = Column(Boolean, nullable=False, default=False)
    consumption = Column(Boolean, nullable=False, default=True)
    consumption_detail = Column(Boolean, nullable=False, default=False)
    production = Column(Boolean, nullable=False, default=False)
    production_detail = Column(Boolean, nullable=False, default=False)
    consumption_price_base = Column(Float, nullable=False, default=0)
    consumption_price_hc = Column(Float, nullable=False, default=0)
    consumption_price_hp = Column(Float, nullable=False, default=0)
    production_price = Column(Float, nullable=False, default=0)
    offpeak_hours_0 = Column(Text, nullable=True)
    offpeak_hours_1 = Column(Text, nullable=True)
    offpeak_hours_2 = Column(Text, nullable=True)
    offpeak_hours_3 = Column(Text, nullable=True)
    offpeak_hours_4 = Column(Text, nullable=True)
    offpeak_hours_5 = Column(Text, nullable=True)
    offpeak_hours_6 = Column(Text, nullable=True)
    plan = Column(Text, nullable=False, default="BASE")
    refresh_addresse = Column(Boolean, nullable=False, default=False)
    refresh_contract = Column(Boolean, nullable=False, default=False)
    token = Column(Text, nullable=False)
    progress = Column(Integer, nullable=False, default="0")
    progress_status = Column(Text, nullable=False, default="")
    enable = Column(Boolean, nullable=False, default=True)
    consentement_expiration = Column(DateTime, nullable=True)
    call_number = Column(Integer, nullable=True)
    quota_reached = Column(Boolean, nullable=True)
    quota_limit = Column(Integer, nullable=True)
    quota_reset_at = Column(DateTime, nullable=True)
    last_call = Column(DateTime, nullable=True)
    ban = Column(Boolean, nullable=True)
    consumption_max_date = Column(DateTime, nullable=True)
    consumption_detail_max_date = Column(
        DateTime,
        nullable=True,
    )
    production_max_date = Column(DateTime, nullable=True)
    production_detail_max_date = Column(DateTime, nullable=True)
    consumption_max_power = Column(Boolean, nullable=False, default=True)
    last_error = Column(Text, nullable=True)

    relation_addressess = relationship("Addresses", back_populates="usage_point")
    relation_contract = relationship("Contracts", back_populates="usage_point")
    relation_consumption_daily = relationship("ConsumptionDaily", back_populates="usage_point")
    relation_consumption_detail = relationship("ConsumptionDetail", back_populates="usage_point")
    relation_production_daily = relationship("ProductionDaily", back_populates="usage_point")
    relation_production_detail = relationship("ProductionDetail", back_populates="usage_point")
    relation_stats = relationship("Statistique", back_populates="usage_point")
    relation_consumption_daily_max_power = relationship("ConsumptionDailyMaxPower", back_populates="usage_point")

    def __repr__(self):
        return (
            f"UsagePoints("
            f"usage_point_id={self.usage_point_id!r}, "
            f"name={self.name!r}, "
            f"cache={self.cache!r}, "
            f"consumption={self.consumption!r}, "
            f"consumption_detail={self.consumption_detail!r}, "
            f"production={self.production!r}, "
            f"production_detail={self.production_detail!r}, "
            f"production_price={self.production_price!r}, "
            f"consumption_price_base={self.consumption_price_base!r}, "
            f"consumption_price_hc={self.consumption_price_hc!r}, "
            f"consumption_price_hp={self.consumption_price_hp!r}, "
            f"consumption_max_power={self.consumption_max_power!r}, "
            f"offpeak_hours_0={self.offpeak_hours_0!r}, "
            f"offpeak_hours_1={self.offpeak_hours_1!r}, "
            f"offpeak_hours_2={self.offpeak_hours_2!r}, "
            f"offpeak_hours_3={self.offpeak_hours_3!r}, "
            f"offpeak_hours_4={self.offpeak_hours_4!r}, "
            f"offpeak_hours_5={self.offpeak_hours_5!r}, "
            f"offpeak_hours_6={self.offpeak_hours_6!r}, "
            f"plan={self.plan!r}, "
            f"refresh_addresse={self.refresh_addresse!r}, "
            f"refresh_contract={self.refresh_contract!r}, "
            f"token={self.token!r}, "
            f"progress={self.progress!r}, "
            f"progress_status={self.progress_status!r}, "
            f"enable={self.enable!r}, "
            f"consentement_expiration={self.consentement_expiration!r}, "
            f"call_number={self.call_number!r}, "
            f"quota_reached={self.quota_reached!r}, "
            f"quota_limit={self.quota_limit!r}, "
            f"quota_reset_at={self.quota_reset_at!r}, "
            f"last_call={self.last_call!r}, "
            f"ban={self.ban!r}, "
            f"consumption_max_date={self.consumption_max_date!r}, "
            f"consumption_detail_max_date={self.consumption_detail_max_date!r}, "
            f"production_max_date={self.production_max_date!r}, "
            f"production_detail_max_date={self.production_detail_max_date!r}, "
            f"last_error={self.last_error!r}, "
            f")"
        )


class Addresses(Base):
    __tablename__ = "addresses"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    street = Column(Text, nullable=True)
    locality = Column(Text, nullable=True)
    postal_code = Column(Text, nullable=True)
    insee_code = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    geo_points = Column(Text, nullable=True)
    count = Column(Integer, nullable=False)

    usage_point = relationship("UsagePoints", back_populates="relation_addressess")

    def __repr__(self):
        return (
            f"Addresses("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"street={self.street!r}, "
            f"locality={self.locality!r}, "
            f"postal_code={self.postal_code!r}, "
            f"insee_code={self.insee_code!r}, "
            f"city={self.city!r}, "
            f"country={self.country!r}, "
            f"geo_points={self.geo_points!r}, "
            f"count={self.count!r}"
            f")"
        )


class Contracts(Base):
    __tablename__ = "contracts"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    usage_point_status = Column(Text, nullable=False)
    meter_type = Column(Text, nullable=False)
    segment = Column(Text, nullable=False)
    subscribed_power = Column(Text, nullable=False)
    last_activation_date = Column(DateTime, nullable=False)
    distribution_tariff = Column(Text, nullable=False)
    offpeak_hours_0 = Column(Text, nullable=True)
    offpeak_hours_1 = Column(Text, nullable=True)
    offpeak_hours_2 = Column(Text, nullable=True)
    offpeak_hours_3 = Column(Text, nullable=True)
    offpeak_hours_4 = Column(Text, nullable=True)
    offpeak_hours_5 = Column(Text, nullable=True)
    offpeak_hours_6 = Column(Text, nullable=True)
    contract_status = Column(Text, nullable=False)
    last_distribution_tariff_change_date = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)

    usage_point = relationship("UsagePoints", back_populates="relation_contract")

    def __repr__(self):
        return (
            f"Contracts("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"usage_point_status={self.usage_point_status!r}, "
            f"meter_type={self.meter_type!r}, "
            f"segment={self.segment!r}, "
            f"subscribed_power={self.subscribed_power!r}, "
            f"last_activation_date={self.last_activation_date!r}, "
            f"distribution_tariff={self.distribution_tariff!r}, "
            f"offpeak_hours_0={self.offpeak_hours_0!r}, "
            f"offpeak_hours_1={self.offpeak_hours_1!r}, "
            f"offpeak_hours_2={self.offpeak_hours_2!r}, "
            f"offpeak_hours_3={self.offpeak_hours_3!r}, "
            f"offpeak_hours_4={self.offpeak_hours_4!r}, "
            f"offpeak_hours_5={self.offpeak_hours_5!r}, "
            f"offpeak_hours_6={self.offpeak_hours_6!r}, "
            f"contract_status={self.contract_status!r}, "
            f"last_distribution_tariff_change_date={self.last_distribution_tariff_change_date!r}, "
            f"count={self.count!r}, "
            f")"
        )


class ConsumptionDaily(Base):
    __tablename__ = "consumption_daily"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(String, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    blacklist = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)

    usage_point = relationship("UsagePoints", back_populates="relation_consumption_daily")

    def __repr__(self):
        return (
            f"ConsumptionDaily("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"date={self.date!r}, "
            f"value={self.value!r}, "
            f"blacklist={self.blacklist!r}, "
            f"fail_count={self.fail_count!r}"
            f")"
        )


class ConsumptionDetail(Base):
    __tablename__ = "consumption_detail"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(String, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    interval = Column(Integer, nullable=False)
    measure_type = Column(Text, nullable=False)
    blacklist = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)

    usage_point = relationship("UsagePoints", back_populates="relation_consumption_detail")

    def __repr__(self):
        return (
            f"ConsumptionDetail("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"date={self.date!r},"
            f"value={self.value!r}, "
            f"interval={self.interval!r}, "
            f"measure_type={self.measure_type!r}, "
            f"blacklist={self.blacklist!r}, "
            f"fail_count={self.fail_count!r}"
            f")"
        )


class ProductionDaily(Base):
    __tablename__ = "production_daily"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(String, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    blacklist = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)

    usage_point = relationship("UsagePoints", back_populates="relation_production_daily")

    def __repr__(self):
        return (
            f"ProductionDaily("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"date={self.date!r}, "
            f"value={self.value!r}, "
            f"blacklist={self.blacklist!r}, "
            f"fail_count={self.fail_count!r}"
            f")"
        )


class ProductionDetail(Base):
    __tablename__ = "production_detail"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(String, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    value = Column(Integer, nullable=False)
    interval = Column(Integer, nullable=False)
    measure_type = Column(Text, nullable=False)
    blacklist = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)

    usage_point = relationship("UsagePoints", back_populates="relation_production_detail")

    def __repr__(self):
        return (
            f"ProductionDetail("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"date={self.date!r},"
            f"value={self.value!r}, "
            f"interval={self.interval!r}, "
            f"measure_type={self.measure_type!r}, "
            f"blacklist={self.blacklist!r}, "
            f"fail_count={self.fail_count!r}"
            f")"
        )


class Statistique(Base):
    __tablename__ = "statistique"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    key = Column(Text, nullable=False)
    value = Column(Integer, nullable=False)

    usage_point = relationship("UsagePoints", back_populates="relation_stats")

    def __repr__(self):
        return (
            f"Statistique("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"key={self.key!r},"
            f"value={self.value!r}, "
            f")"
        )


class ConsumptionDailyMaxPower(Base):
    __tablename__ = "consumption_daily_max_power"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(String, primary_key=True, index=True, unique=True)
    usage_point_id = Column(Text, ForeignKey("usage_points.usage_point_id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    event_date = Column(DateTime, nullable=True)
    value = Column(Integer, nullable=False)
    blacklist = Column(Integer, nullable=False, default=0)
    fail_count = Column(Integer, nullable=False, default=0)

    usage_point = relationship("UsagePoints", back_populates="relation_consumption_daily_max_power")

    def __repr__(self):
        return (
            f"ConsumptionDailyMaxPower("
            f"id={self.id!r}, "
            f"usage_point_id={self.usage_point_id!r}, "
            f"date={self.date!r}, "
            f"event_date={self.event_date!r}, "
            f"value={self.value!r}, "
            f"blacklist={self.blacklist!r}, "
            f"fail_count={self.fail_count!r}"
            f")"
        )


class Tempo(Base):
    __tablename__ = "tempo"

    date = Column(DateTime, primary_key=True, index=True, unique=True)
    color = Column(Text, nullable=False, index=True)

    def __repr__(self):
        return f"Tempo(" f"date={self.date!r}, " f"color={self.color!r}, " f")"


class TempoConfig(Base):
    __tablename__ = "tempo_config"

    key = Column(Text, primary_key=True, index=True, unique=True)
    value = Column(Text, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.value


class Ecowatt(Base):
    __tablename__ = "ecowatt"

    date = Column(DateTime, primary_key=True, index=True, unique=True)
    value = Column(Integer, nullable=False, index=True)
    message = Column(Text, nullable=False, index=True)
    detail = Column(Text, nullable=False, index=True)

    def __repr__(self):
        return (
            f"Ecowatt("
            f"date={self.date!r}, "
            f"value={self.value!r}, "
            f"message={self.message!r}, "
            f"detail={self.detail!r}, "
            f")"
        )
