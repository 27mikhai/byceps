"""
byceps.blueprints.snippet_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...services.site import service as site_service
from ...services.snippet import service as snippet_service
from ...services.snippet.transfer.models import Scope
from ...services.text_diff import service as text_diff_service
from ...util.datetime.format import format_datetime_short
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.iterables import pairwise
from ...util.framework.templating import templated
from ...util.views import redirect_to, respond_no_content

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..snippet import signals
from ..snippet.templating import get_snippet_context

from .authorization import SnippetMountpointPermission, SnippetPermission
from .forms import DocumentCreateForm, DocumentUpdateForm, \
    FragmentCreateForm, FragmentUpdateForm, MountpointCreateForm

blueprint = create_blueprint('snippet_admin', __name__)


permission_registry.register_enum(SnippetMountpointPermission)
permission_registry.register_enum(SnippetPermission)


@blueprint.route('/for_scope/<scope_type>/<scope_name>')
@permission_required(SnippetPermission.view)
@templated
def index_for_scope(scope_type, scope_name):
    """List snippets for that scope."""
    scope = Scope(scope_type, scope_name)

    snippets = snippet_service \
        .get_snippets_for_scope_with_current_versions(scope)

    mountpoints = snippet_service.get_mountpoints_for_scope(scope)

    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'snippets': snippets,
        'mountpoints': mountpoints,
        'site': site,
    }


@blueprint.route('/versions/<uuid:snippet_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def view_version(snippet_version_id):
    """Show the snippet with the given id."""
    version = _find_version(snippet_version_id)

    try:
        snippet_context = get_snippet_context(version)

        context = {
            'version': version,
            'snippet_title': snippet_context['title'],
            'snippet_head': snippet_context['head'],
            'snippet_body': snippet_context['body'],
            'error_occurred': False,
        }
    except Exception as e:
        context = {
            'version': version,
            'error_occurred': True,
            'error_message': str(e),
        }

    context['site'] = _find_site_for_scope(version.snippet.scope)

    return context


@blueprint.route('/snippets/<uuid:snippet_id>/history')
@permission_required(SnippetPermission.view_history)
@templated
def history(snippet_id):
    snippet = _find_snippet_by_id(snippet_id)

    versions = snippet.get_versions()
    versions_pairwise = list(pairwise(versions + [None]))

    site = _find_site_for_scope(snippet.scope)

    return {
        'snippet': snippet,
        'versions_pairwise': versions_pairwise,
        'site': site,
    }


# -------------------------------------------------------------------- #
# document


@blueprint.route('/for_scope/<scope_type>/<scope_name>/documents/create')
@permission_required(SnippetPermission.create)
@templated
def create_document_form(scope_type, scope_name):
    """Show form to create a document."""
    scope = Scope(scope_type, scope_name)

    form = DocumentCreateForm()

    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'site': site,
    }


@blueprint.route('/for_scope/<scope_type>/<scope_name>/documents', methods=['POST'])
@permission_required(SnippetPermission.create)
def create_document(scope_type, scope_name):
    """Create a document."""
    scope = Scope(scope_type, scope_name)

    form = DocumentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version = snippet_service.create_document(scope, name, creator.id, title,
                                              body, head=head,
                                              image_url_path=image_url_path)

    flash_success('Das Dokument "{}" wurde angelegt.', version.snippet.name)
    signals.snippet_created.send(None, snippet_version_id=version.id)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/documents/<uuid:snippet_id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_document_form(snippet_id):
    """Show form to update a document."""
    snippet = _find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    form = DocumentUpdateForm(
        obj=current_version,
        name=snippet.name)

    site = _find_site_for_scope(snippet.scope)

    return {
        'form': form,
        'snippet': snippet,
        'site': site,
    }


@blueprint.route('/documents/<uuid:snippet_id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_document(snippet_id):
    """Update a document."""
    form = DocumentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.current_user
    title = form.title.data.strip()
    head = form.head.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    version = snippet_service.update_document(snippet, creator.id, title, body,
                                              head=head,
                                              image_url_path=image_url_path)

    flash_success('Das Dokument "{}" wurde aktualisiert.', version.snippet.name)
    signals.snippet_updated.send(None, snippet_version_id=version.id)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/documents/<uuid:from_version_id>/compare_to/<uuid:to_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def compare_documents(from_version_id, to_version_id):
    """Show the difference between two document versions."""
    from_version = _find_version(from_version_id)
    to_version = _find_version(to_version_id)

    if from_version.snippet_id != to_version.snippet_id:
        abort(400, 'The versions do not belong to the same snippet.')

    html_diff_title = _create_html_diff(from_version, to_version, 'title')
    html_diff_head = _create_html_diff(from_version, to_version, 'head')
    html_diff_body = _create_html_diff(from_version, to_version, 'body')
    html_diff_image_url_path = _create_html_diff(from_version, to_version,
                                                 'image_url_path')

    site = _find_site_for_scope(from_version.snippet.scope)

    return {
        'diff_title': html_diff_title,
        'diff_head': html_diff_head,
        'diff_body': html_diff_body,
        'diff_image_url_path': html_diff_image_url_path,
        'site': site,
    }


# -------------------------------------------------------------------- #
# fragment


@blueprint.route('/for_scope/<scope_type>/<scope_name>/fragments/create')
@permission_required(SnippetPermission.create)
@templated
def create_fragment_form(scope_type, scope_name):
    """Show form to create a fragment."""
    scope = Scope(scope_type, scope_name)

    form = FragmentCreateForm()

    site = _find_site_for_scope(scope)

    return {
        'scope': scope,
        'form': form,
        'site': site,
    }


@blueprint.route('/for_scope/<scope_type>/<scope_name>/fragments', methods=['POST'])
@permission_required(SnippetPermission.create)
def create_fragment(scope_type, scope_name):
    """Create a fragment."""
    scope = Scope(scope_type, scope_name)

    form = FragmentCreateForm(request.form)

    name = form.name.data.strip().lower()
    creator = g.current_user
    body = form.body.data.strip()

    version = snippet_service.create_fragment(scope, name, creator.id, body)

    flash_success('Das Fragment "{}" wurde angelegt.', version.snippet.name)
    signals.snippet_created.send(None, snippet_version_id=version.id)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/fragments/<uuid:snippet_id>/update')
@permission_required(SnippetPermission.update)
@templated
def update_fragment_form(snippet_id):
    """Show form to update a fragment."""
    snippet = _find_snippet_by_id(snippet_id)
    current_version = snippet.current_version

    form = FragmentUpdateForm(
        obj=current_version,
        name=snippet.name)

    site = _find_site_for_scope(snippet.scope)

    return {
        'form': form,
        'snippet': snippet,
        'site': site,
    }


@blueprint.route('/fragments/<uuid:snippet_id>', methods=['POST'])
@permission_required(SnippetPermission.update)
def update_fragment(snippet_id):
    """Update a fragment."""
    form = FragmentUpdateForm(request.form)

    snippet = _find_snippet_by_id(snippet_id)

    creator = g.current_user
    body = form.body.data.strip()

    version = snippet_service.update_fragment(snippet, creator.id, body)

    flash_success('Das Fragment "{}" wurde aktualisiert.', version.snippet.name)
    signals.snippet_updated.send(None, snippet_version_id=version.id)

    return redirect_to('.view_version', snippet_version_id=version.id)


@blueprint.route('/fragments/<uuid:from_version_id>/compare_to/<uuid:to_version_id>')
@permission_required(SnippetPermission.view_history)
@templated
def compare_fragments(from_version_id, to_version_id):
    """Show the difference between two fragment versions."""
    from_version = _find_version(from_version_id)
    to_version = _find_version(to_version_id)

    if from_version.snippet_id != to_version.snippet_id:
        abort(400, 'The versions do not belong to the same snippet.')

    html_diff_body = _create_html_diff(from_version, to_version, 'body')

    site = _find_site_for_scope(from_version.snippet.scope)

    return {
        'diff_body': html_diff_body,
        'site': site,
    }


# -------------------------------------------------------------------- #
# mountpoint


@blueprint.route('/snippets/<uuid:snippet_id>/mountpoints/create')
@permission_required(SnippetMountpointPermission.create)
@templated
def create_mountpoint_form(snippet_id):
    """Show form to create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    form = MountpointCreateForm()

    site = _find_site_for_scope(snippet.scope)

    return {
        'snippet': snippet,
        'form': form,
        'site': site,
    }


@blueprint.route('/snippets/<uuid:snippet_id>/mountpoints', methods=['POST'])
@permission_required(SnippetMountpointPermission.create)
def create_mountpoint(snippet_id):
    """Create a mountpoint."""
    snippet = _find_snippet_by_id(snippet_id)

    form = MountpointCreateForm(request.form)

    endpoint_suffix = form.endpoint_suffix.data.strip()
    url_path = form.url_path.data.strip()
    if not url_path.startswith('/'):
        abort(400, 'URL path must start with a slash.')

    mountpoint = snippet_service.create_mountpoint(endpoint_suffix, url_path,
                                                   snippet)

    flash_success('Der Mountpoint für "{}" wurde angelegt.',
                  mountpoint.url_path)
    return redirect_to('.index_for_scope',
                       scope_type=snippet.scope.type_,
                       scope_name=snippet.scope.name)


@blueprint.route('/mountpoints/<uuid:mountpoint_id>', methods=['DELETE'])
@permission_required(SnippetMountpointPermission.delete)
@respond_no_content
def delete_mountpoint(mountpoint_id):
    """Delete a mountpoint."""
    mountpoint = snippet_service.find_mountpoint(mountpoint_id)

    if mountpoint is None:
        abort(404)

    url_path = mountpoint.url_path

    snippet_service.delete_mountpoint(mountpoint)

    flash_success('Der Mountpoint für "{}" wurde entfernt.', url_path)


# -------------------------------------------------------------------- #
# helpers


def _find_snippet_by_id(snippet_id):
    snippet = snippet_service.find_snippet(snippet_id)

    if snippet is None:
        abort(404)

    return snippet


def _find_version(version_id):
    version = snippet_service.find_snippet_version(version_id)

    if version is None:
        abort(404)

    return version


def _create_html_diff(from_version, to_version, attribute_name):
    """Create an HTML diff between the named attribute's value of each
    of the two versions.
    """
    from_description = format_datetime_short(from_version.created_at)
    to_description = format_datetime_short(to_version.created_at)

    from_text = getattr(from_version, attribute_name)
    to_text = getattr(to_version, attribute_name)

    return text_diff_service.create_html_diff(from_text, to_text,
                                              from_description, to_description)


def _find_site_for_scope(scope):
    if scope.type_ != 'site':
        return None

    return site_service.find_site(scope.name)
