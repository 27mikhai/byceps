#!/usr/bin/env python

"""Create a new terms of service version.

However, do not set the new version as the current version for the brand.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.consent import subject_service as consent_subject_service
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import SnippetVersionID
from byceps.services.terms import version_service as terms_version_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_brand


def validate_snippet_version_id(ctx, param, value) -> SnippetVersionID:
    snippet_version = snippet_service.find_snippet_version(value)

    if not snippet_version:
        raise click.BadParameter('Unknown snippet_version ID "{}".'.format(value))

    return snippet_version.id


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('title')
@click.argument('snippet_version_id', callback=validate_snippet_version_id)
@click.argument('consent_subject_name_suffix')
def execute(brand, title, snippet_version_id, consent_subject_name_suffix):
    consent_subject_name = '{}_terms-of-service_{}'.format(
        brand.id, consent_subject_name_suffix)

    consent_subject_title = 'AGB {} / {}'.format(brand.title, title)

    consent_subject = consent_subject_service.create_subject(
        consent_subject_name, consent_subject_title, 'terms_of_service')

    terms_version_service \
        .create_version(brand.id, title, snippet_version_id, consent_subject.id)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
