import os
import distutils.file_util as file_util
import distutils.dir_util as dir_util
import subprocess

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()


def copy_files_scaffolds(filename, new_filename, output_dir):
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
    dest_dir = os.path.join(os.path.dirname(__file__), 'atramhasis', 'scaffolds', output_dir, new_filename + '_tmpl')
    file_util.copy_file(source_dir, dest_dir, update=True)


def copy_static_scaffold(output_dir):
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'atramhasis', 'static'))
    dest_dir = os.path.join(os.path.dirname(__file__), 'atramhasis', 'scaffolds', output_dir, '+package+', 'static')
    dir_util.copy_tree(os.path.join(source_dir, 'css'), os.path.join(dest_dir, 'css'), update=True)
    dir_util.copy_tree(os.path.join(source_dir, 'img'), os.path.join(dest_dir, 'img'), update=True)
    dir_util.copy_tree(os.path.join(source_dir, 'js'), os.path.join(dest_dir, 'js'), update=True)
    dir_util.copy_tree(os.path.join(source_dir, 'scss', 'atramhasis'), os.path.join(dest_dir, 'scss', 'atramhasis'),
                       update=True)
    dir_util.mkpath(os.path.join(dest_dir, 'admin'))
    file_util.copy_file(
        os.path.join(source_dir, 'admin', '.bowerrc'),
        os.path.join(dest_dir, 'admin', '.bowerrc'),
        update=True
    )
    file_util.copy_file(
        os.path.join(source_dir, 'admin', 'bower.json'),
        os.path.join(dest_dir, 'admin', 'bower.json'),
        update=True
    )
    file_util.copy_file(
        os.path.join(source_dir, 'admin', 'Gruntfile.js'),
        os.path.join(dest_dir, 'admin', 'Gruntfile.js'),
        update=True
    )
    file_util.copy_file(
        os.path.join(source_dir, 'admin', 'package.json'),
        os.path.join(dest_dir, 'admin', 'package.json'),
        update=True
    )


def dojo_build():
    print('-' * 50)
    print('==> check npm dependencies')
    libs = str(subprocess.check_output(["npm", "list", "-g", "bower", "grunt-cli"]))
    if 'bower' in libs:
        bower = True
        print('bower OK')
    else:
        bower = False
        print('bower KO, use \'npm install -g bower\' to install')
    if 'grunt-cli' in libs:
        gruntcli = True
        print('grunt-cli OK')
    else:
        gruntcli = False
        print('grunt-cli KO, use \'npm install -g grunt-cli\' to install')
    if bower and gruntcli:
        print('==> running grunt build')
        subprocess.call(["grunt", "-v", "build"], cwd="atramhasis/static/admin")
    print('-' * 50)


class PrepareScaffold(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        dojo_build()
        copy_files_scaffolds("requirements.txt", "atramhasis-requirements.txt", "atramhasis_demo")
        copy_files_scaffolds("requirements-dev.txt", "atramhasis-requirements-dev.txt", "atramhasis_demo")
        copy_files_scaffolds("requirements.txt", "atramhasis-requirements.txt", "atramhasis_scaffold")
        copy_files_scaffolds("requirements-dev.txt", "atramhasis-requirements-dev.txt", "atramhasis_scaffold")
        copy_static_scaffold("atramhasis_scaffold")
        copy_static_scaffold("atramhasis_demo")


requires = [
    'pyramid',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'skosprovider',
    'skosprovider_sqlalchemy',
    'skosprovider_rdf',
    'skosprovider_getty',
    'skosprovider_heritagedata',
    'pyramid_skosprovider',
    'language_tags',
    'pyramid_jinja2',
    'alembic',
    'babel',
    'colander',
    'requests',
    'dogpile.cache',
    'six',
    'pyramid_rewrite'
]

setup(name='atramhasis',
      version='0.6.5',
      description='A web based editor for thesauri adhering to the SKOS specification.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ],
      author='Flanders Heritage Agency',
      author_email='ict@onroerenderfgoed.be',
      url='http://atramhasis.readthedocs.org',
      keywords='web wsgi pyramid SKOS thesaurus vocabulary',
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='atramhasis',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = atramhasis:main
      [console_scripts]
      initialize_atramhasis_db = atramhasis.scripts.initializedb:main
      import_file = atramhasis.scripts.import_file:main
      dump_rdf = atramhasis.scripts.dump_rdf:main
      generate_ldf_config = atramhasis.scripts.generate_ldf_config:main
      [pyramid.scaffold]
        atramhasis_scaffold=atramhasis.scaffolds:AtramhasisTemplate
        atramhasis_demo=atramhasis.scaffolds:AtramhasisDemoTemplate
      """,
      cmdclass={
          'prepare': PrepareScaffold
      }
      )
