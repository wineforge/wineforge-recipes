# Installation execution contract

TOML is a serialization format; it does not install software by itself. A
Wineforge implementation turns a validated recipe into an installation plan
and executes only the actions defined by the schema.

For a `run-installer` action, an implementation must:

1. download the referenced source over HTTPS without permitting a downgrade;
2. verify the complete file against its pinned SHA-256 digest;
3. create or open the recipe's private Wine prefix under required isolation;
4. stage the verified source in a launcher-owned directory inside that prefix
   and address it with a Windows path;
5. invoke an `exe` source directly, or invoke an `msi` source through
   `msiexec /i`;
6. pass each declared argument as a distinct process argument without a shell;
7. wait for completion and accept only a declared `successExitCodes` value;
8. run every declared postcondition; and
9. record the recipe, source, engine, result, and postcondition digests in an
   installation receipt.

Failure at any stage fails the installation. Implementations should build a
new prefix transactionally and retain or restore the previous working prefix
instead of continuing with partial state.

## Comparison with Chocolatey

Chocolatey packages normally contain NuGet metadata plus a
`chocolateyInstall.ps1` script. Its `Install-ChocolateyPackage` helper accepts
installer type, download URLs, checksums, silent arguments, and valid exit
codes. Chocolatey's PowerShell model is flexible enough to run arbitrary
package code.

Wineforge deliberately models the common safe subset as data:

| Chocolatey concept | Wineforge recipe |
| --- | --- |
| package URL and checksum | `[[sources]]` with HTTPS and SHA-256 |
| `fileType` | `installerType` |
| `silentArgs` | `arguments` array |
| `validExitCodes` | `successExitCodes` array |
| package script verification | typed `[[verify]]` postconditions |
| arbitrary PowerShell | intentionally unsupported |

Installer-specific silent switches still have to come from the application's
publisher. For example, Notepad++ documents case-sensitive `/S`; MSI packages
usually use arguments such as `/qn` and `/norestart`.

The public catalog validates these plans today. Runtime execution belongs in
the Wineforge CLI and is the next integration layer; accepting a recipe must
never imply evaluating TOML as code.
