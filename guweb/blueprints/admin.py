# -*- coding: utf-8 -*-

__all__ = ()

from quart import Blueprint
from quart import render_template

admin = Blueprint('admin', __name__)

@admin.route('/')
@admin.route('/home')
@admin.route('/dashboard')
async def home():
    """Render the homepage of guweb's admin panel."""
    return await render_template('404.html')
