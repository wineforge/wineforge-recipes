# Wineforge Recipes

Wineforge Recipes is the neutral, versioned format for describing reproducible
Windows application setup under Wineforge. This repository contains the public
schema and fictional examples; it intentionally contains no user-specific or
proprietary application configuration.

Recipes are data, not programs. Version 1 supports verified downloads and a
small set of typed installation operations. It deliberately has no arbitrary
shell, PowerShell, batch-file, or host-path action.

## Validate

Create an isolated environment, install the development dependency, and run:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
```

The validator checks the schema itself, every recipe below `recipes/`, and the
test fixtures. CI performs the same checks.

## Format principles

- `schemaVersion` selects an immutable major schema (`1`).
- Recipe IDs are stable reverse-DNS-style identifiers.
- Every remote input uses HTTPS and a SHA-256 digest.
- Executables and arguments are separate values, never shell strings.
- Runtime host and network access are explicit and default to none.
- Platform-specific engine requirements are declared as variants.
- Postconditions make successful installation observable.
- Unknown properties are rejected so misspelled security fields cannot be
  silently ignored.

The normative definition is [schema/v1/recipe.schema.json](schema/v1/recipe.schema.json).

## Repository policy

Only fictional demonstration recipes belong here until a contributor has the
right to publish all names, URLs, metadata, and installation knowledge in a
real recipe. Private recipes can use the same schema without being contributed.

