from django.db.models import CharField
from django.db.models.functions import Cast


def bounded_page_size(request, default, maximum=100):
    """Return a safe page size from a request, falling back to the view default."""
    try:
        return min(max(int(request.GET.get("page_size", default)), 1), maximum)
    except (TypeError, ValueError):
        return default


def apply_ordering(queryset, requested, allowed_fields):
    """Apply only explicitly supported ordering fields with a stable tie-breaker."""
    if requested and any(requested in {field, f"-{field}"} for field in allowed_fields):
        return queryset.order_by(requested, "pk")
    return queryset


def filter_partial_id(queryset, search_term):
    """Search numeric primary keys as text without backend-specific lookups."""
    return queryset.annotate(_searchable_id=Cast("pk", output_field=CharField())).filter(
        _searchable_id__icontains=search_term
    )
