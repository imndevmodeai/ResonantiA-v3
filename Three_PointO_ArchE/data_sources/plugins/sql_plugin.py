from typing import Dict, Any, List
from ..base import DataSourcePlugin
import logging
import numpy as np
import time

logger = logging.getLogger(__name__)

class SqlPlugin(DataSourcePlugin):
    """
    A data source plugin for interacting with SQL databases.
    This encapsulates the logic of the `interact_with_database` tool.
    NOTE: This is a placeholder/simulator and does not connect to a real database.
    """

    def query(self, statement: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Executes a simulated SQL query. The 'statement' is the SQL query.

        Args:
            statement (str): The SQL query to execute.
            **kwargs: Additional parameters, such as 'db_type'.

        Returns:
            A list of dictionaries representing the simulated query results.
        """
        query = statement
        db_type = kwargs.get("db_type", "SQL")
        logger.info(f"Executing simulated SQL Plugin query on {db_type}: {query}")

        try:
            query_lower = str(query).lower().strip()
            if query_lower.startswith("select"):
                num_rows = np.random.randint(0, 5)
                sim_data = [{"sim_id": i + 1, "sim_value": f"value_{np.random.randint(100)}"} for i in range(num_rows)]
                return sim_data
            elif query_lower.startswith(("insert", "update", "delete")):
                rows_affected = np.random.randint(0, 2)
                return [{"rows_affected": rows_affected}]
            else:
                return [{"error": f"Unsupported simulated SQL query type: {query[:30]}..."}]
        except Exception as e:
            logger.error(f"SQL Plugin query failed: {e}", exc_info=True)
            return [{"error": str(e)}]

    def get_schema(self) -> Dict[str, Any]:
        """
        Returns a schema describing the inputs for this plugin.
        """
        return {
            "type": "sql",
            "inputs": {
                "statement": "string (SQL Query)",
                "db_type": "string (e.g., postgresql, mysql)"
            }
        }
