import datetime
import distutils.dir_util
import os
from textwrap import dedent

from alembic.config import Config
from pyramid.scaffolds import PyramidTemplate
from pyramid.scaffolds import Template


def copy_dir_to_scaffold(output_dir, package, dir):
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', dir))
    dest_dir = os.path.join(output_dir, package, dir)
    distutils.dir_util.copy_tree(source_dir, dest_dir)


class AtramhasisTemplate(PyramidTemplate):
    _template_dir = 'atramhasis_scaffold'
    summary = 'Create an Atramhasis implementation'

    def pre(self, command, output_dir, vars):
        from alembic import command
        from alembic.script import ScriptDirectory
        root = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
        alembic_config = Config(os.path.join(root, 'alembic.ini'))
        alembic_config.set_main_option(
            'script_location', os.path.join(root, 'atramhasis', 'alembic')
        )
        scripts = ScriptDirectory.from_config(alembic_config)
        vars['last_revision'] = scripts.get_revisions("head")[0].revision
        vars['today'] = datetime.datetime.now().isoformat()
        super().pre(command, output_dir, vars)

    def post(self, command, output_dir, vars):  # pragma: no cover
        """ Overrides :meth:`pyramid.scaffolds.template.Template.post`"""

        copy_dir_to_scaffold(output_dir, vars['package'], 'locale')

        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Documentation: http://atramhasis.readthedocs.io

            Welcome to Atramhasis.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)


class AtramhasisDemoTemplate(PyramidTemplate):
    _template_dir = 'atramhasis_demo'
    summary = 'Create an Atramhasis demo'

    def post(self, command, output_dir, vars):  # pragma: no cover
        """ Overrides :meth:`pyramid.scaffolds.template.Template.post`"""

        copy_dir_to_scaffold(output_dir, vars['package'], 'locale')

        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Documentation: http://atramhasis.readthedocs.io
            Demo instructions: http://atramhasis.readthedocs.io/en/latest/demo.html

            Welcome to Atramhasis Demo.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)
        return Template.post(self, command, output_dir, vars)
