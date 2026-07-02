# ponytail: filtro personalizado para formatear moneda de Paraguay (Guaraníes) de forma robusta
from django import template

register = template.Library()

@register.filter
def gs_format(value):
    if value is None:
        return "Gs. 0"
    try:
        val = float(value)
        is_negative = val < 0
        val_abs = abs(val)
        # Formatear con separadores de miles con punto y sin decimales
        formatted = f"{int(round(val_abs)):,}".replace(",", ".")
        prefix = "-" if is_negative else ""
        return f"{prefix}Gs. {formatted}"
    except (ValueError, TypeError):
        return value
