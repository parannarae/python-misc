from inspect import isclass


class StaticAttrObject:
    """A class which works like struct.

    Intention of this class is to store only data (and not a class method) statically (with familiar interface as in C).
    It has following characteristics:
        1. When it is compared with another object, it explicitly compares key and values but not the object itself.
        2. Attributes are not allowed to add dynamically
            - However, it does not use __slots__ attribute to support other
            modules which requires __dict__ attribute

    Note: private class attributes (i.e. variable with `_` or `__` prefix) are not allowed.
    
    From python 3.7, dataclasses can be used instead of this:
        https://docs.python.org/3.7/library/dataclasses.html
    """
    def __repr__(self):
        return (
            "{}({})".format(
                self.__class__.__name__,
                ', '.join(str("{}={}".format(k, getattr(self, k, None))) for k in sorted(self.__dict__.keys())))
        )

    def _are_variables_equal(self, other):
        """Compare self with other by their key and value pairs, not the object itself.

        Args:
            other (StaticAttrObject): object to be compared

        Returns:
            bool: True if all key value pairs have the same values
        """
        for attr_name in self._get_attr_names():
            if getattr(self, attr_name) != getattr(other, attr_name):
                return False

        return True

    def __eq__(self, other):
        """Override default equal"""
        if isinstance(other, self.__class__):
            return self._are_variables_equal(other)
        return NotImplemented

    def __ne__(self, other):
        """Override default not equal"""
        if isinstance(other, self.__class__):
            return not self._are_variables_equal(other)
        return NotImplemented

    def __hash__(self):
        """Override default hash

        This should be implemented since __eq__ is overwritten (to be useable as items in hashable collections)
        https://docs.python.org/3/reference/datamodel.html#object.__hash__
        """
        # use sort to create equal hash
        attr_names = sorted(list(self._get_attr_names()))
        return hash(tuple(getattr(self, cur_attr) for cur_attr in attr_names))

    @classmethod
    def _get_attr_names(cls):
        """Returns only class attributes' names

        class attributes

        Returns:
            set[str]: names of attributes
        """
        return set(
            key
            for key, value in cls.__dict__.items()
            if (not key.startswith('_')     # This includes all variables start with `_` (i.e. `__double_underline`)
                and not type(value) is classmethod
                and not type(value) is staticmethod
                and not type(value) is property
                and (isclass(value) or not callable(value))      # To remove methods but not object attribute
                )
        )

    def __setattr__(self, key, value):
        """Prevent dynamic addition of attributes
        """
        if key not in self._get_attr_names():
            raise AttributeError("{} is not declared in {}".format(key, self.__class__.__name__))
        object.__setattr__(self, key, value)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
