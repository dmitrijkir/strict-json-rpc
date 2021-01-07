from dataclasses import dataclass
from typing import Optional, Union, Any, Dict, List


@dataclass
class Context:
    method_name: Optional[str] = None
    auth: Optional[dict] = None
    header: Optional[Dict[str, str]] = None
    body: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    request_data: Optional[Dict[str, Any]] = None

    @property
    def is_batch(self):
        return isinstance(self.body, list)
