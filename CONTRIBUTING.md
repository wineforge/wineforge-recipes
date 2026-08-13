# Contributing

Contributions must remain declarative, reviewable, and reproducible.

1. Add or update a recipe in `recipes/v1/`.
2. Pin every download by SHA-256. Never use a moving URL without a digest.
3. Request only the runtime capabilities the application actually needs.
4. Include at least one meaningful postcondition.
5. Run the validator and unit tests documented in the README.
6. Explain the source and licence of any real-world metadata in the pull
   request. Do not submit credentials, licence keys, personal paths, private
   download links, or material you cannot publish.

Schema evolution is additive within a major version. A breaking semantic or
validation change requires a new `schema/vN/` directory and migration notes.
Once released, an old major schema remains available.

The action vocabulary should stay small. Proposals for new actions must explain
why existing typed actions cannot express the operation and what validation,
rollback, and security boundaries apply. Arbitrary command execution will not
be added as a convenience feature.

