#!/usr/bin/env python3


def get_model_field_names(model_or_instance):
    """
    Returns a list of field names for the given Django model or model instance.

    Parameters:
    model_or_instance: A Django model class or an instance of a Django model.

    Returns:
    list: A list of field names for the given model.
    """
    # If it's an instance, get its class
    if not isinstance(model_or_instance, type):
        model_or_instance = model_or_instance.__class__

    # Retrieve and return the field names
    return [field.name for field in model_or_instance._meta.get_fields()]
