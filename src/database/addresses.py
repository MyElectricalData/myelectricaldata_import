"""Manage Addresses table in database."""
from sqlalchemy import delete, select

from database import DB
from db_schema import (
    Addresses,
    UsagePoints,
)


class DatabaseAddresses:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id):
        """Initialize DatabaseConfig."""
        self.session = DB.session
        self.usage_point_id = usage_point_id

    def get(
        self,
    ):
        """Retrieve the address associated with the given usage point ID."""
        query = (
            select(Addresses)
            .join(UsagePoints.relation_addressess)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        )
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set(self, data, count=0):
        """Set the address associated with the given usage point ID.

        Args:
            data (dict): The address data.
            count (int, optional): The count value. Defaults to 0.
        """
        query = (
            select(Addresses)
            .join(UsagePoints.relation_addressess)
            .where(Addresses.usage_point_id == self.usage_point_id)
        )
        addresses = self.session.scalars(query).one_or_none()
        if addresses is not None:
            addresses.street = data["street"]
            addresses.locality = data["locality"]
            addresses.postal_code = data["postal_code"]
            addresses.insee_code = data["insee_code"]
            addresses.city = data["city"]
            addresses.country = data["country"]
            addresses.geo_points = data["geo_points"]
            addresses.count = count
        else:
            self.session.add(
                Addresses(
                    usage_point_id=self.usage_point_id,
                    street=data["street"],
                    locality=data["locality"],
                    postal_code=data["postal_code"],
                    insee_code=data["insee_code"],
                    city=data["city"],
                    country=data["country"],
                    geo_points=data["geo_points"],
                    count=count,
                )
            )
        self.session.flush()
        self.session.close()

    def delete(self):
        """Delete the address associated with the given usage point ID.

        Returns:
            bool: True if the address is successfully deleted, False otherwise.
        """
        self.session.execute(delete(Addresses).where(Addresses.usage_point_id == self.usage_point_id))
        self.session.flush()
        self.session.close()
        return True
