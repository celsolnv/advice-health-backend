from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    error_data = response.data
    message = ""

    if isinstance(error_data, dict):
        # Pega a primeira mensagem disponível para o campo message
        if "detail" in error_data:
            message = str(error_data["detail"])
        elif "non_field_errors" in error_data:
            message = str(error_data["non_field_errors"][0])
        else:
            # Pega o primeiro erro do primeiro campo
            first_key = next(iter(error_data))
            first_value = error_data[first_key]
            message = str(first_value[0]) if isinstance(first_value, list) else str(first_value)
    elif isinstance(error_data, list):
        message = str(error_data[0])

    response.data = {
        "error": True,
        "message": message,
        "errors": error_data,
        "status_code": response.status_code,
    }

    return response
