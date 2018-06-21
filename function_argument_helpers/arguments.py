"""
Decorator module for rudimentary type checks in methods.
Provides a decorator to protect incoming data to methods for basic type
safety. Decorator takes in a dict of {variable_name:type} and raises a
SystemError when a type mismatch is encountered.
"""

# pylint: disable=C0413

__all__ = ("protect_types",)
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"

import sys
sys.dont_write_bytecode = True
from re import match


TYPE_MAP = {
    "int": int,
    "str": str,
    "dict": dict,
    "tuple": tuple,
    "list": list,
    "float": float
}


def get_mix_data(arguments_info):
    """
    Helper to get the mixed argument data types from the arguments info
    by parsing the <type>.<type> format.
    """
    mix_data = {}
    for key, value in arguments_info.items():
        if isinstance(value, str) and match(r".*?\<\w+\>$", value):
            _data = list(filter(None, map(
                lambda _: TYPE_MAP.get(_.strip(">")),
                filter(None, value.split("<"))
            )))
            mix_data[key] = _data
    return mix_data


def protect_types(arguments_info):
    """
    Main decorator to run type checks for incoming arguments in a method.

    :param arguments_info: Arguments type information for decorated function.
    :type  arguments_info: dict
    """

    def real_decorator(function):
        """
        Inner decorator to work with the decorator overloaded with
        arguments
        """

        types_data_error = " ".join([
            "{}. arguments info needs",
            "to be a dict of <argument>:<type>"
        ])

        def wrapper(*args, **kwargs):
            """Function wrapper"""
            if not isinstance(arguments_info, dict):
                raise SystemError(types_data_error.format("Invalid usage"))
            valid_arguments_info = {
                key: value for key, value in arguments_info.items()
                if isinstance(key, str) and isinstance(value, type)
            }

            mix_data = get_mix_data(arguments_info)
            original_map = {}
            original_map.update(mix_data)


            valid_arguments_info.update(mix_data)
            valid_arguments_info.update(arguments_info)

            if not valid_arguments_info:
                raise SystemError(types_data_error.format(
                    "No valid arguments"
                ))

            function_name = function.__name__
            local_data = locals()
            local_data.update(
                dict(zip(function.__code__.co_varnames, args))
            )
            local_data.update(kwargs)
            for argument, argument_type in valid_arguments_info.items():
                argument_value = local_data.get(argument)
                if isinstance(argument_type, list):
                    base_type = argument_type[0]
                    if not isinstance(argument_value, base_type):
                        raise SystemError(
                            "{} needs to be of type {}. Got {}".format(
                                argument, base_type, type(argument_value)
                            )
                        )
                    if base_type == type([]) and len(argument_type) > 1:
                        secondary_type = argument_type[1]
                        invalids = [
                            _ for _ in argument_value
                            if not isinstance(_, secondary_type)
                        ]
                        if invalids:
                            error = \
                                ". ".join([
                                    "All values in {} need to be of type {}",
                                    "Got {} as invalid data."
                                ])
                            raise SystemError(
                                error.format(
                                    argument, secondary_type, invalids
                                )
                            )
                else:
                    if not isinstance(argument_value, argument_type):
                        raise SystemError(
                            "{} requires {} to be {}. Got {}".format(
                                function_name, argument, argument_type,
                                type(argument_value)
                            )
                        )

            return function(*args, **kwargs)

        return wrapper

    return real_decorator
