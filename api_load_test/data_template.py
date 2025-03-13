import json

from string import Template
from typing import Optional


class DataTemplate:
    """Class holding POST body data to be sent to create-bulk API.

    It holds a template thus some keyword strings (${value_to_change}) can be
    substituted.
    """
    __template: Optional[Template] = None

    def __init__(self, file_name: str):
        with open(file_name) as fp:
            self.__template = Template(fp.read().replace('\n', ''))

    def get_formatted_str(self, **kwargs):
        """Returns template string with all keyword strings substituted.
        """
        if not self.__template:
            raise RuntimeError("Template is unexpectedly unset")
        return self.__template.substitute(**kwargs)

    def get_json(self, **kwargs):
        """Returns json created from template string with substituted keyword
        strings.
        """
        return json.loads(self.get_formatted_str(**kwargs))
