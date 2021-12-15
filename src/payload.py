"""Summary."""
import json
import pydash
from typing import Dict, List, Optional


class Payload:
    """Summary."""

    def __init__(self, data: Optional[Dict[str, str]] = None) -> None:
        """Summary.

        Args:
            data (Optional[Dict[str, str]], optional): Description

        """
        self._data: Dict[str, str] = data or {}

    def get(self, key: str, default = None) -> Optional[str]:
        """Summary.

        Args:
            key (str): Description

        Returns:
            Optional[str]: Description

        """
        return pydash.get(self._data, key) or default

    def set(self, key: str, value: str) -> None:
        """Summary.

        Args:
            key (str): Description
            value (str): Description

        """
        self._data[key] = value

    def unset(self, key: str) -> str:
        """Summary.

        Args:
            key (str): Description
            value (str): Description

        """
        return self._data.pop(key, None)

    def list(self) -> List[str]:
        """Summary.

        Returns:
            List[str]: Description

        """
        return list(self._data.values())
