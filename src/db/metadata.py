from typing import Dict, List, Optional
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine
from functools import lru_cache
from sqlalchemy import inspect

class MetadataManager:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self._metadata = sa.MetaData()

    @lru_cache(maxsize=100)
    async def get_table_metadata(self, table_names: Optional[List[str]] = None) -> Dict:
        """Retrieve and cache table metadata"""
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
                            "foreign_key": bool(column.foreign_keys)
                        }

                    metadata[table_name] = {
                        "columns": columns,
                        "primary_key": [k.name for k in table.primary_key],
                        "foreign_keys": [
                            {
                                "column": fk.parent.name,
                                "references": {
                                    "table": fk.column.table.name,
                                    "column": fk.column.name
                                }
                            }
                            for fk in table.foreign_keys
                        ]
                    }

                return metadata

        except Exception as e:
            raise Exception(f"Failed to retrieve metadata: {str(e)}")

    def invalidate_cache(self):
        """Clear the metadata cache"""
        self.get_table_metadata.cache_clear()