# Security policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could enable code execution,
digest bypass, path escape, credential exposure, or unsafe host access. Use the
repository's private security-advisory reporting channel. Include the affected
schema version, a minimal recipe, impact, and any proposed mitigation.

## Trust model

A valid recipe is not necessarily a trustworthy recipe. Schema validation
proves structure and enforces baseline safety properties; maintainers and users
must still review publisher identity, download ownership, licences, requested
capabilities, and application behavior.

Wineforge implementations should additionally:

- verify source bytes against SHA-256 before use;
- reject redirects that downgrade HTTPS;
- treat archive extraction and Windows paths as untrusted input;
- apply steps transactionally in a disposable or backed-up prefix;
- never interpolate recipe values into a shell;
- require explicit user approval for declared host or network access;
- avoid exposing the host root, home directory, devices, or Unix sockets;
- record the recipe and engine digests in an installation receipt.

The schema intentionally cannot request raw host paths, devices, arbitrary
commands, or unbounded filesystem access.

