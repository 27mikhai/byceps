"""
byceps.blueprints.admin.tourney.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


TourneyCategoryPermission = create_permission_enum('tourney_category', [
    'create',
    'update',
    'view',
])
