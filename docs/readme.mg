# HOW TO USE

##

    pip install sphinx-rtd_theme

    pip install sphinx-autoapi



## First Time in Repo

Choose split!

    mkdir docs
    cd docs
    sphinx-quickstart
    
Modify conf.py and index.rst to equal to these

### conf.py start at -- Options for HTML output -------------------------------------------------

Edit toAdd var and autoApiDirs
```
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
```

### index.rst start under ===

```
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   autoapi/index
````


## build docu

    sphinx-build -b html source build


## On GitHub

1. Actions Tab

2. Search Static HTML

3. Click configure

4. set path to 'docs/build'

5. commit changes

6. Go to Settings Tab

7. go to Pages

8. under build and Deploy select Source GitHub Actions

