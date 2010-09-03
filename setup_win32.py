## setup_win32.py (run me as python setup_win32.py py2exe -O2)
##
## Based on setup_win32.py of Gajim project.

from distutils.core import setup
import py2exe
import glob

opts = {
    'py2exe': {
        # ConfigParser,UserString,roman are needed for docutils
        'includes': ('pango,atk,gobject,cairo,pangocairo,gtk.keysyms,gio,encodings,encodings.*'),
        'dll_excludes': [
            'iconv.dll', 'intl.dll', 'libatk-1.0-0.dll',
            'libgdk_pixbuf-2.0-0.dll', 'libgdk-win32-2.0-0.dll',
            'libglib-2.0-0.dll', 'libgmodule-2.0-0.dll',
            'libgobject-2.0-0.dll', 'libgthread-2.0-0.dll',
            'libgtk-win32-2.0-0.dll', 'libpango-1.0-0.dll',
            'libpangowin32-1.0-0.dll', 'libcairo-2.dll',
            'libpangocairo-1.0-0.dll', 'libpangoft2-1.0-0.dll',
        ],
        'optimize': 2,
    }
}

support_files = [('data/pixmaps', glob.glob('turpial/data/pixmaps/*')), ('data/sounds', glob.glob('turpial/data/sounds/*')), ('data/themes/default', glob.glob('turpial/data/themes/default/*'))]

setup(
    name='Turpial',
    version='1.3.4',
    description='A desktop Twitter client',
    author='Wil Alvarez',
    url='http://turpial.org.ve/',
    download_url='http://turpial.org.ve/downloads/',
    license='GPL',
    windows=[{'script': 'turpial/main.py',
              'icon_resources': [(1, 'turpial.ico')]},
            ],
    options=opts,
    data_files=support_files,
)
