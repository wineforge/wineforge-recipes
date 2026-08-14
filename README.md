# Wineforge Recipes

Wineforge Recipes is the neutral, versioned format for describing reproducible
Windows application setup under Wineforge. Human-authored recipes are TOML;
the JSON Schema remains a machine-readable validation artifact. This repository
contains neutral fictional examples and pinned public recipes for open-source
applications. It intentionally contains no user-specific or proprietary
application configuration.

Recipes are data, not programs. Version 1 supports verified downloads and a
small set of typed installation operations. A pinned Chocolatey `.nupkg` can
also be used as declarative input, but package PowerShell is never executed.
It deliberately has no arbitrary shell, PowerShell, batch-file, or host-path
action.

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

## Automatic installation

Recipes can describe unattended installation through typed `[[install]]`
steps. A `run-installer` step selects a verified source, declares `exe` or
`msi`, supplies silent arguments as an array, and lists accepted exit codes.
When a vendor distributes its installer inside a ZIP, `archiveMember` names the
exact executable to extract from the verified archive; other members are not
extracted.
The `copy-file` action can seed a verified application default beneath
`%APPDATA%` without hard-coding Wine's private Windows username.
The `chocolatey-package` action pins a `.nupkg` and asks Wineforge to translate
the supported static `Install-ChocolateyPackage` fields into the same native
installer plan. Both the package and its vendor download are SHA-256 verified.
TOML itself does not execute anything, and the catalog validator does not run
installers. The required runtime behavior and comparison with Chocolatey are
documented in [docs/installation-execution.md](docs/installation-execution.md).

The Notepad++, 7-Zip, and Google Chrome recipes are real, pinned fixtures. The
Chrome recipe exercises the download-at-install-time Chocolatey model. Their
declared source bytes are checked by a scheduled and manually dispatchable workflow.
This verifies download integrity without running third-party Windows code in
ordinary pull-request jobs. End-to-end installation belongs in an isolated,
disposable Wine prefix using the Wineforge runtime.

## Repository policy

Real recipes must reference public publisher material, use verifiable licensing
metadata, and pin immutable installer bytes. Private recipes can use the same
schema without being contributed.
