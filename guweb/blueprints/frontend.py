# -*- coding: utf-8 -*-

__all__ = ()

from quart import Blueprint
from quart import render_template

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
@frontend.route('/home')
async def home():
    """Render the homepage."""
    return await render_template('404.html')

@frontend.route('/register')
async def register():
    """Render the registration page."""
    return await render_template('404.html')

@frontend.route('/login')
async def login():
    """Render the login page."""
    return await render_template('404.html')
