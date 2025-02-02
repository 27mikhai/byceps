"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

import pytest

from byceps.events.snippet import SnippetCreated
from byceps.services.snippet.dbmodels.snippet import (
    SnippetVersion as DbSnippetVersion,
)
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.services.user.transfer.models import User

from tests.helpers import generate_token, log_in_user


@pytest.fixture(scope='package')
def snippet_admin(make_admin):
    permission_ids = {
        'admin.access',
        'snippet.create',
        'snippet.update',
        'snippet.delete',
        'snippet.view',
        'snippet.view_history',
        'snippet_mountpoint.create',
        'snippet_mountpoint.delete',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def snippet_admin_client(make_client, admin_app, snippet_admin):
    return make_client(admin_app, user_id=snippet_admin.id)


@pytest.fixture(scope='package')
def global_scope():
    return Scope('global', 'global')


@pytest.fixture
def make_document(global_scope: Scope, snippet_admin: User):
    def _wrapper(
        name: Optional[str] = None, title: str = 'Title', body: str = 'Body'
    ) -> tuple[DbSnippetVersion, SnippetCreated]:
        if name is None:
            name = generate_token()

        version, event = snippet_service.create_document(
            global_scope, name, snippet_admin.id, title, body
        )
        return version, event

    return _wrapper


@pytest.fixture
def make_fragment(global_scope: Scope, snippet_admin: User):
    def _wrapper(
        name: Optional[str] = None, body: str = 'Body'
    ) -> tuple[DbSnippetVersion, SnippetCreated]:
        if name is None:
            name = generate_token()

        version, event = snippet_service.create_fragment(
            global_scope, name, snippet_admin.id, body
        )
        return version, event

    return _wrapper
