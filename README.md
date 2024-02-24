# Log-based testing 🪵

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Build](https://github.com/etianen/logot/actions/workflows/build.yml/badge.svg)](https://github.com/etianen/logot/actions/workflows/build.yml)
[![Codecov](https://codecov.io/gh/etianen/logot/graph/badge.svg?token=J5K0LOOSTZ)](https://codecov.io/gh/etianen/logot)
[![Docs](https://readthedocs.org/projects/logot/badge/)](https://logot.readthedocs.io)
[![PyPI version](https://img.shields.io/pypi/v/logot.svg)](https://pypi.org/project/logot/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/logot.svg)](https://pypi.org/project/logot/)

`logot` makes it easy to test whether your code is logging correctly:

```python
from logot import Logot, logged

def test_something(logot: Logot) -> None:
    do_something()
    logot.assert_logged(logged.info("Something was done"))
```

`logot` integrates with popular testing frameworks (e.g. [`pytest`](https://logot.readthedocs.io/latest/using-pytest.html), [`unittest`](https://logot.readthedocs.io/latest/using-unittest.html)). It supports many 3rd-party [asynchronous](https://logot.readthedocs.io/latest/integrations/index.html#asynchronous-frameworks) and [logging](https://logot.readthedocs.io/latest/integrations/index.html#logging-frameworks) frameworks, and can be extended to support many more. 💪

## Documentation 📖

Full documentation is published on [Read the Docs](https://logot.readthedocs.io). Learn more about `logot` with the following guides:

- [Log message matching](https://logot.readthedocs.io/latest/log-message-matching.html)
- [Log pattern matching](https://logot.readthedocs.io/latest/log-pattern-matching.html)
- [Log capturing](https://logot.readthedocs.io/latest/log-capturing.html)
- [Using with `pytest`](https://logot.readthedocs.io/latest/using-pytest.html)
- [Using with `unittest`](https://logot.readthedocs.io/latest/using-unittest.html)
- [Installing](https://logot.readthedocs.io/latest/installing.html)


## Bugs / feedback 🐛

Issue tracking is hosted on [GitHub](https://github.com/etianen/logot/issues).


## Changelog 🏗️

Release notes are published on [GitHub](https://github.com/etianen/logot/releases).


## License ⚖️

`logot` is published as open-source software under the [MIT license](https://github.com/etianen/logot/blob/main/LICENSE).
