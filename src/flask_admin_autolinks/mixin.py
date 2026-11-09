"""Hyperlink relationship columns in Flask-Admin SQLAlchemy list views."""

import typing as t

from flask import url_for
from flask_admin.contrib.sqla.tools import is_relationship
from markupsafe import Markup, escape


class AutoLinksMixin:
    """Put before ModelView in the bases. True = auto-detect; dict = per-column endpoint override."""

    column_relationship_links: bool | dict[str, str] = False

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._autolinks = self._scaffold_autolinks()
        if self._autolinks:  # eager-load link targets: no N+1 on the list page
            self._auto_joins = list({*self._auto_joins, *self._autolinks.values()})

    def _scaffold_autolinks(self) -> dict[str, t.Any]:
        if not self.column_relationship_links:
            return {}
        found = {}
        for name, _label in self._list_columns:
            if name in self.column_formatters:  # explicit formatters always win
                continue
            attr = getattr(self.model, name, None)
            if attr is not None and is_relationship(attr):
                found[name] = attr
        return found

    def _target_view(self, name: str, related_cls: type) -> t.Any:
        links = self.column_relationship_links
        endpoint = links.get(name) if isinstance(links, dict) else None
        for view in self.admin._views:
            if endpoint is not None:
                if view.endpoint == endpoint:
                    return view
            elif getattr(view, "model", None) is related_cls:
                return view
        return None

    @staticmethod
    def _href(view: t.Any, target: t.Any) -> str | None:
        if view is None or not view.is_accessible():
            return None
        pk = view.get_pk_value(target)
        if view.can_edit:
            return url_for(f"{view.endpoint}.edit_view", id=pk)
        if view.can_view_details:
            return url_for(f"{view.endpoint}.details_view", id=pk)
        return None

    def get_list_value(self, context: t.Any, model: t.Any, name: str) -> t.Any:
        attr = self._autolinks.get(name)
        if attr is None:
            return super().get_list_value(context, model, name)
        value = getattr(model, name)
        if value is None:
            return ""
        prop = attr.property
        view = self._target_view(name, prop.mapper.class_)
        out = []
        for target in value if prop.uselist else [value]:
            label = escape(str(target))
            href = self._href(view, target)
            out.append(Markup('<a href="{}">{}</a>').format(href, label) if href else label)
        return Markup(", ").join(out)
