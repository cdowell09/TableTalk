import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine

# Using a module-level cache dictionary instead of method-level lru_cache
_metadata_cache = {}


class MetadataManager:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self._metadata = sa.MetaData()

    async def get_table_metadata(self, table_names: list[str] | None = None) -> dict:
        """Retrieve and cache table metadata"""
        cache_key = tuple(sorted(table_names)) if table_names else None
        if cache_key in _metadata_cache:
            return _metadata_cache[cache_key]

        try:
            async with self.engine.connect() as conn:
                await conn.run_sync(self._metadata.reflect)
                metadata = {}

                for table_name, table in self._metadata.tables.items():
                    if table_names and table_name not in table_names:
                        continue

                    columns = {}
                    for column in table.columns:
                        columns[column.name] = {
                            "type": str(column.type),
                            "nullable": column.nullable,
                            "primary_key": column.primary_key,
                            "foreign_key": bool(column.foreign_keys),
                        }

                    metadata[table_name] = {
                        "columns": columns,
                        "primary_key": [k.name for k in table.primary_key],
                        "foreign_keys": [
                            {
                                "column": fk.parent.name,
                                "references": {
                                    "table": fk.column.table.name,
                                    "column": fk.column.name,
                                },
                            }
                            for fk in table.foreign_keys
                        ],
                    }

                # Cache the result
                _metadata_cache[cache_key] = metadata
                return metadata

        except Exception as e:
            raise Exception(f"Failed to retrieve metadata: {str(e)}") from e

    def invalidate_cache(self):
        """Clear the metadata cache"""
        _metadata_cache.clear()
