#!/usr/bin/python3
# metaclass to store settings

from collections import namedtuple


class Settings:
    """
    metaclass to allow for easy storage, editing, and creation of
    settings
    """

    def __init__(self, kwargs):
        self.setattr(arg_dict=kwargs)

    def setattr(self, arg_dict = {}, **kwargs):
        """
            Create a new attribute or set attribute to a different 
            value.
        """
        kwargs.update(arg_dict)
        for name, value in kwargs.items():
            self.__setattr__(name, value)

if __name__ == "__main__":
    settings = Settings("0.1.5a", reset=True, test_mode=True, abc=109)
    for key,val in vars(settings).items():
        print(f"{key}={val}")
