from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.group()
def translate():
    """
    Translation and localization commands.
    """
    pass

import os

def extract():
    if os.system('pybabel extract -F babel.cfg -k _l -o text.pot .'):
        raise RuntimeError('Extract command failed.')

@translate.command()
def update():
    """
    Update all languages.
    """

    extract()
    if os.system('pybabel update -i text.pot -d webapp/translations'):
        raise RuntimeError('Update command failed.')
    os.remove('text.pot')

@translate.command()
def compile_lang():
    """
    Compile all languages.
    """
    if os.system('pybabel compile -d webapp/translations'):
        raise RuntimeError('Compile command failed.')

import click

@translate.command()
@click.argument('lang')
def init(lang):
    """
    Initialize a new language.
    """
    extract()
    if os.system(f'pybabel init -i text.pot -d webapp/translations -l {lang}'):
        raise RuntimeError('Init command failed.')
    os.remove('text.pot')