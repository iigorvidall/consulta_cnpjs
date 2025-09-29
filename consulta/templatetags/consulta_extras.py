from django import template

register = template.Library()


@register.filter
def email_or_dash(value: str) -> str:
    """Return a safe email string or 'Sem e-mail' when missing/invalid.

    Handles cases where the backend may have accidentally stored template fragments
    like "{% else %}" as plain text by stripping such substrings.
    """
    if not value:
        return 'Sem e-mail'
    s = str(value).strip()
    # Guard against stray template delimiters accidentally persisted
    if '{% else %}' in s or '{% if' in s:
        # Try to keep the email portion if present, else fall back
        # Very simple heuristic: split at template markers
        parts = [p.strip() for p in s.replace('{% else %}', '|').split('|') if p.strip()]
        for p in parts:
            if '@' in p and ' ' not in p:
                return p
        return 'Sem e-mail'
    if s == '-' or s.lower() in ('sem e-mail', 'sem email'):
        return 'Sem e-mail'
    return s
