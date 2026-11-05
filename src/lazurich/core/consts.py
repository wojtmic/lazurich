from importlib.metadata import PackageNotFoundError, version

APP_ID = 'd1801a6c-317e-45b7-adef-08fe47e474f6'
CODENAME = 'beta'

try:
    VERSION = version('lazurich')
except PackageNotFoundError:
    VERSION = '0.0.0+dev'
