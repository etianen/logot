# Log-based testing 🪵

[![Build](https://github.com/etianen/logot/actions/workflows/build.yml/badge.svg)](https://github.com/etianen/logot/actions/workflows/build.yml)
[![Docs](https://readthedocs.org/projects/logot/badge/)](https://logot.readthedocs.io)
[![PyPI version](https://img.shields.io/pypi/v/logot.svg)](https://pypi.org/project/logot/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/logot.svg)](https://pypi.org/project/logot/)

`logot` makes it easy to test your application is logging correctly:

``` python
from logot import Logot, logged

def test_my_app(logot: Logot) -> None:
    app.start()
    logot.wait_for(logged.info("App started"))
```


## Documentation 📖

Full documentation is published on [Read the Docs](https://logot.readthedocs.io).


## Bugs / feedback 🐛

Issue tracking is hosted on [GitHub](https://github.com/etianen/logot/issues).


## Changelog 🏗️

Release notes are published on [GitHub](https://github.com/etianen/logot/releases).


## License ⚖️

``logot`` is published as open-source software under the [MIT license](https://github.com/etianen/logot/blob/main/LICENSE).
