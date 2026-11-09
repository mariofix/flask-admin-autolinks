# flask-admin-autolinks

Automatic hyperlinks for relationship columns in Flask-Admin's SQLAlchemy list views.

By default, a relationship column renders as plain text (`str()` of the related object). With this mixin, each related object becomes a link to its own edit (or details) page in the admin.

## Features

- Opt-in per view. No effect unless `column_relationship_links` is set.
- Resolves the target view from the registered views by model. No endpoint naming convention required.
- Respects the target view's `can_edit`, `can_view_details` and `is_accessible()`. Falls back to plain text.
- Eager-loads link targets through the view's `_auto_joins`, so the list page does not issue N+1 queries.
- Explicit `column_formatters` entries always win.
- Output is escaped.

## Installation

```bash
uv add flask-admin-autolinks
# or
pip install flask-admin-autolinks
```

Requires Flask-Admin with SQLAlchemy support (`flask-admin[sqlalchemy]`). Supported versions are declared in `pyproject.toml`.

## Usage

Place `AutoLinksMixin` before `ModelView` in the bases:

```python
from flask_admin.contrib.sqla import ModelView
from flask_admin_autolinks import AutoLinksMixin


class OrderView(AutoLinksMixin, ModelView):
    column_list = ("id", "customer", "items")
    column_relationship_links = True
```

For project-wide use, define a shared base once:

```python
class BaseView(AutoLinksMixin, ModelView):
    column_relationship_links = True
```

Only relationship columns listed in `column_list` are linked.

## Configuration

`column_relationship_links` accepts:

| Value | Behavior |
| --- | --- |
| `False` (default) | Disabled. |
| `True` | Link every relationship column in `column_list` to the registered view for the related model. |
| `dict[str, str]` | Same as `True`, with per-column overrides mapping a relationship name to a view endpoint. |

```python
class OrderView(AutoLinksMixin, ModelView):
    column_list = ("id", "customer", "items")
    column_relationship_links = {"customer": "client"}  # "client" is the target view's endpoint
```

An empty dict is falsy and leaves the feature disabled.

## Behavior

For each related object, the link target is chosen in this order:

1. Target view has `can_edit` and is accessible: link to `edit_view`.
2. Otherwise, target view has `can_view_details` and is accessible: link to `details_view`.
3. Otherwise: escaped plain text.

If no view is registered for the related model (or the override endpoint is not found), the cell renders as plain text. The list page is never broken by a missing target.

Collections render as comma-separated links. `None` renders as an empty cell.

A column that already has an entry in `column_formatters` is left untouched and is not eager-loaded by this package.

## To Do

- SQLAlchemy backend only (`flask_admin.contrib.sqla`), add others.

## License

See `LICENSE` for MIT License.

## IA

Documentation done with Claude.
