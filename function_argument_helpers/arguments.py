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
        def wrapper(*args, **kwargs):
            """Function wrapper"""
            types_data_error = " ".join([
                "{}. arguments info needs",
                "to be a dict of <argument>:<type>"
            ])
            if not isinstance(arguments_info, dict):
                raise SystemError(types_data_error.format("Invalid usage"))
            valid_arguments_info = {
                key: value for key, value in arguments_info.items()
                if isinstance(key, str) and isinstance(value, type)
            }
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
