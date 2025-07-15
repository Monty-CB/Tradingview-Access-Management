from dateutil import parser
from dateutil.relativedelta import relativedelta

def get_access_extension(currentExpirationDate: str, extension_type: str, extension_length: int) -> str:
    """
    Esta función recibe la fecha de expiración actual, el tipo de extensión (años, meses, semanas, días),
    y la longitud de la extensión. Devuelve la nueva fecha de expiración extendida.
    """
    try:
        # Intentar analizar la fecha de expiración
        expiration = parser.parse(currentExpirationDate)
    except ValueError:
        raise ValueError(f"Invalid date format: {currentExpirationDate}")

    # Extender la fecha según el tipo de unidad (Año, Mes, Semana, Día)
    if extension_type == 'Y':  # Añadir años
        expiration = expiration + relativedelta(years=extension_length)
    elif extension_type == 'M':  # Añadir meses
        expiration = expiration + relativedelta(months=extension_length)
    elif extension_type == 'W':  # Añadir semanas
        expiration = expiration + relativedelta(weeks=extension_length)
    elif extension_type == 'D':  # Añadir días
        expiration = expiration + relativedelta(days=extension_length)
    else:
        raise ValueError(f"Invalid extension type: {extension_type}")

    # Retornar la nueva fecha de expiración como una cadena con el formato YYYY-MM-DD
    return expiration.strftime("%Y-%m-%d")
