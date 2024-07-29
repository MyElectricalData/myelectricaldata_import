"""Manage Contracts table in database."""

from sqlalchemy import delete, select

from db_schema import (
    Contracts,
    UsagePoints,
)

from . import DB


class DatabaseContracts:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id):
        """Initialize DatabaseConfig."""
        self.session = DB.session()
        self.usage_point_id = usage_point_id

    def get(self) -> Contracts:
        """Retrieve the contract associated with the given usage point ID.

        Returns:
            Contracts: The contract object if found, None otherwise.
        """
        query = (
            select(Contracts)
            .join(UsagePoints.relation_contract)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        )
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set(self, data: dict, count: int = 0) -> None:
        """Set the contract details for the given usage point ID.

        Args:
            usage_point_id (int): The ID of the usage point.
            data (dict): A dictionary containing the contract details.
            count (int, optional): The count value. Defaults to 0.

        Returns:
            None
        """
        query = (
            select(Contracts)
            .join(UsagePoints.relation_contract)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        )
        contract: Contracts = self.session.scalars(query).one_or_none()
        if contract is not None:
            contract.usage_point_status = data["usage_point_status"]
            contract.meter_type = data["meter_type"]
            contract.segment = data["segment"]
            contract.subscribed_power = data["subscribed_power"]
            contract.last_activation_date = data["last_activation_date"]
            contract.distribution_tariff = data["distribution_tariff"]
            contract.offpeak_hours_0 = data["offpeak_hours_0"]
            contract.offpeak_hours_1 = data["offpeak_hours_1"]
            contract.offpeak_hours_2 = data["offpeak_hours_2"]
            contract.offpeak_hours_3 = data["offpeak_hours_3"]
            contract.offpeak_hours_4 = data["offpeak_hours_4"]
            contract.offpeak_hours_5 = data["offpeak_hours_5"]
            contract.offpeak_hours_6 = data["offpeak_hours_6"]
            contract.contract_status = data["contract_status"]
            contract.last_distribution_tariff_change_date = data["last_distribution_tariff_change_date"]
            contract.count = count
        else:
            self.session.add(
                Contracts(
                    usage_point_id=self.usage_point_id,
                    usage_point_status=data["usage_point_status"],
                    meter_type=data["meter_type"],
                    segment=data["segment"],
                    subscribed_power=data["subscribed_power"],
                    last_activation_date=data["last_activation_date"],
                    distribution_tariff=data["distribution_tariff"],
                    offpeak_hours_0=data["offpeak_hours_0"],
                    offpeak_hours_1=data["offpeak_hours_1"],
                    offpeak_hours_2=data["offpeak_hours_2"],
                    offpeak_hours_3=data["offpeak_hours_3"],
                    offpeak_hours_4=data["offpeak_hours_4"],
                    offpeak_hours_5=data["offpeak_hours_5"],
                    offpeak_hours_6=data["offpeak_hours_6"],
                    contract_status=data["contract_status"],
                    last_distribution_tariff_change_date=data["last_distribution_tariff_change_date"],
                    count=count,
                )
            )
        self.session.flush()
        self.session.close()

    def delete(self):
        """Delete the contract associated with the given usage point ID.

        Args:
            usage_point_id (int): The ID of the usage point.

        Returns:
            bool: True if the address is successfully deleted, False otherwise.
        """
        self.session.execute(delete(Contracts).where(Contracts.usage_point_id == self.usage_point_id))
        self.session.flush()
        self.session.close()
        return True
