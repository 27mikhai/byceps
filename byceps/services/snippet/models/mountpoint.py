"""
byceps.services.snippet.models.mountpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from flask import url_for
from werkzeug.routing import BuildError

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...site.transfer.models import SiteID

from ..transfer.models import SnippetID

from .snippet import Snippet


class Mountpoint(db.Model):
    """The exposition of a snippet at a certain URL path of a site."""
    __tablename__ = 'snippet_mountpoints'
    __table_args__ = (
        db.UniqueConstraint('site_id', 'endpoint_suffix'),
        db.UniqueConstraint('site_id', 'url_path'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    site_id = db.Column(db.UnicodeText, db.ForeignKey('sites.id'), index=True, nullable=False)
    endpoint_suffix = db.Column(db.UnicodeText, nullable=False)
    url_path = db.Column(db.UnicodeText, nullable=False)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)

    def __init__(self, site_id: SiteID, endpoint_suffix: str, url_path: str,
                 snippet_id: SnippetID) -> None:
        self.site_id = site_id
        self.endpoint_suffix = endpoint_suffix
        self.url_path = url_path
        self.snippet_id = snippet_id

    def generate_url(self) -> Optional[str]:
        try:
            return url_for('snippet.{}'.format(self.endpoint_suffix))
        except BuildError:
            return None

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('site_id') \
            .add_with_lookup('endpoint_suffix') \
            .add_with_lookup('url_path') \
            .add_with_lookup('snippet') \
            .build()
