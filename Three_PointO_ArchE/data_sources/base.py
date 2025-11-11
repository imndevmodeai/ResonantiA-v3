from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DataSourcePlugin(ABC):
    """
    Abstract base class for all data source plugins.
    Each plugin must implement methods to query the data source
    and to report its own schema.
    """

    @abstractmethod
    def query(self, statement: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute a query against the data source.

        Args:
            statement (str): The query string or statement to execute.
            **kwargs: Additional parameters for the query.

        Returns:
            A list of dictionaries representing the query results.
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the data source.

        Returns:
            A dictionary representing the schema of the data source.
            The structure can be specific to the plugin (e.g., table names and columns for SQL).
        """
        pass
