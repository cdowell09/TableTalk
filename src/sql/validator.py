import sqlparse
from typing import Dict, Tuple
from src.core.base import BaseResponse

class SQLValidator:
    def __init__(self):
        self.dangerous_keywords = {
            "DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT",
            "REVOKE", "EXECUTE", "EXEC", "COMMIT", "ROLLBACK"
        }

    async def validate_sql(self, sql: str, metadata: Dict) -> BaseResponse:
        """Validate generated SQL query"""
        try:
            # Basic SQL parsing
            parsed = sqlparse.parse(sql)
            if not parsed:
                return BaseResponse(success=False, error="Empty or invalid SQL")

            # Check for dangerous operations
            if self._contains_dangerous_operations(parsed[0]):
                return BaseResponse(
                    success=False,
                    error="SQL contains potentially dangerous operations"
                )

            # Validate against metadata
            tables_valid, error = self._validate_tables(parsed[0], metadata)
            if not tables_valid:
                return BaseResponse(success=False, error=error)

            return BaseResponse(success=True, data={"sql": sql})

        except Exception as e:
            return BaseResponse(success=False, error=str(e))

    def _contains_dangerous_operations(self, parsed_sql: sqlparse.sql.Statement) -> bool:
        """Check for dangerous SQL operations"""
        tokens = parsed_sql.flatten()
        return any(
            token.value.upper() in self.dangerous_keywords
            for token in tokens
            if token.ttype in sqlparse.tokens.Keyword
        )

    def _validate_tables(
        self,
        parsed_sql: sqlparse.sql.Statement,
        metadata: Dict
    ) -> Tuple[bool, str]:
        """Validate table names against metadata"""
        tables = set(metadata.keys())
        sql_tables = set()

        for token in parsed_sql.flatten():
            if token.ttype is None and isinstance(token, sqlparse.sql.Identifier):
                table_name = token.get_real_name()
                if table_name:
                    sql_tables.add(table_name)

        invalid_tables = sql_tables - tables
        if invalid_tables:
            return False, f"Invalid table(s): {', '.join(invalid_tables)}"

        return True, ""
