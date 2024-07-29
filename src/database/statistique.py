"""Manage Config table in database."""


from sqlalchemy import delete, select

from db_schema import Statistique, UsagePoints

from . import DB


class DatabaseStatistique:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id):
        """Initialize DatabaseConfig."""
        self.session = DB.session()
        self.usage_point_id = usage_point_id

    def get(self, key):
        """Retrieve the value associated with the given key."""
        return self.session.scalars(
            select(Statistique)
            .join(UsagePoints.relation_stats)
            .where(Statistique.usage_point_id == self.usage_point_id)
            .where(Statistique.key == key)
        ).all()

    def set(self, key, value):
        """Set the value associated with the given key.

        If the key already exists, the value will be updated.
        If the key does not exist, it will be created.
        """
        current_value = self.get(key)
        if current_value:
            for item in current_value:
                item.value = value
        else:
            self.session.add(Statistique(usage_point_id=self.usage_point_id, key=key, value=value))
        self.session.flush()
        return True

    def delete(self):
        """Delete the statistics associated with the usage point."""
        self.session.execute(delete(Statistique).where(Statistique.usage_point_id == self.usage_point_id))
