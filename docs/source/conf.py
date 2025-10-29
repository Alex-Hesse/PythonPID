# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PythonPID'
copyright = '2025, Alexader Hesse'
author = 'Alexader Hesse'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
import os
import sys
# The absolute path to your project's root directory
sys.path.insert(0, os.path.abspath('../../'))

# List of extensions to enable
extensions = [
    'autoapi.extension',
    'sphinx_rtd_theme'
]


# The theme to use for HTML and HTML Help pages
html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
autoapi_dirs = ['../../src']

def post_process_html(app, exception):
    print("called 1")
    toAdd ='<base href="/PythonPID/">'
    toSearch = '<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />'
    if exception is None and app.builder.name == 'html':
        with open(os.path.abspath(os.path.join("build", "index.html")), "r+", encoding='utf-8') as f:
            content = f.read()
            newContent = content.replace(toSearch, toSearch+'\n  '+toAdd)
            f.seek(0)
            f.truncate()
            f.write(newContent)
        print("Changed index.html to work with github pages")
        
def  setup(app):
    print("called 0")
    app.connect('build-finished', post_process_html)