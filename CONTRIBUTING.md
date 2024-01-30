# Contributing

Contributions to `logot` are always welcome! 🤗


## Questions and feedback 🤔

Please [open an issue](https://github.com/etianen/logot/issues) for any questions, feedback or feature requests. Asking questions can help improve the [project docs](https://logot.readthedocs.io), and we're always happy to discuss new features!


## Bugs 🐛

Please [open an issue](https://github.com/etianen/logot/issues) to report a bug. Try to be as detailed as possible, and always include:

- The Python version you're using.
- The `logot` version you're using.
- Steps to reproduce.

Please report vulnerabilities privately via [GitHub Security](https://github.com/etianen/logot/security). Security issues will be fixed as soon as possible. 💪


## New features and changes 🏗️

For non-trivial features and changes, please [open an issue](https://github.com/etianen/logot/issues) first to discuss the work! This will make it easier to understand and (hopefully) accept your contribution.


### Developing 🤓

`logot` is developed using [Poetry](https://python-poetry.org/), an excellent Python packaging and dependency management tool. Make sure Poetry is [installed and up-to-date](https://python-poetry.org/docs/#installation) before developing `logot`!

1. Fork the `logot` [GitHub project](https://github.com/etianen/logot).

2. Clone the repository locally:

   ``` bash
   git clone git@github.com:your-username/logot.git
   cd logot
   ```

3. Install dependencies and activate your project:

   ``` bash
   poetry install
   poetry shell
   ```

4. Create a new branch:

   ``` bash
   git checkout -b awesome-thing
   ```

5. Implement your changes! Don't worry about keeping a clean commit history, as your PR will be squashed when merged into `logot`! 😅

6. Add tests and documentation. Please see our [build and test workflow](https://github.com/etianen/logot/blob/main/.github/workflows/build.yml) for all required lints and checks, including:
   - Linting with [Ruff](https://docs.astral.sh/ruff/linter/)
   - Formatting with [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
   - Type-checking with [mypy](https://mypy.readthedocs.io/)
   - Testing with [pytest](https://docs.pytest.org/)

8. Commit and push your changes:

   ``` bash
   git add .
   git commit -m 'Added awesome thing'
   git push origin awesome-thing
   ```

9. Open a [pull request](https://github.com/etianen/logot/pulls) to submit your changes to `logot`. Please include a good title and description, since this will become the permanent commit message when merged into `logot`! 🚀
