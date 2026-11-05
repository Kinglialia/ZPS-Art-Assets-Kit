# Library configuration

Use the library explicitly named by the user or the current project configuration. Look for `art-library.json` at the supplied project root when one is available. Do not search unrelated projects or default to a previous owner's library. If both sources conflict, resolve which is current before writing. Reading an accessible supplied snapshot can proceed while the write target remains undecided.

Optional configuration (store it in the project, not in the installed skill):

```json
{
  "schema_version": 1,
  "canonical_source": "local",
  "local_root": "./reference-library",
  "drive_folder_url": null
}
```

`canonical_source` is `local` or `drive`; set `drive_folder_url` when Drive is canonical. `local_root` is relative to the config file, or an explicit absolute user path. These fields locate data; they do not authorize synchronization or grant access. Do not create or modify project config unless requested. A user-provided location is sufficient without this file.

For Drive, inspect the available connector and current listing for the index and library JSON. Saved IDs/receipts do not prove current access or freshness. For a local snapshot, read its start/index document, verify its manifest if present, then open the relevant cards and images. Respect the actual package layout rather than assuming a fixed parent directory. Record snapshot/version and the canonical destination for updates.

If no library is configured, ask for its location only when library access is needed. Other art tasks can continue. Keep library data versions separate from skill versions; do not replace newer cloud data with an older local snapshot.

## Snapshot supplied with the v0.5.x package

The extracted installer includes `resources/library-v0.2.0/reference-library/` (version 0.2.0). It is not copied into installed skills. Keep the extracted resources at a stable location and supply that absolute path in the task or project art-library.json. Its parent MANIFEST.json verifies the original snapshot. The nested older manager and stored Drive URLs are historical source data, not active skill instructions or current cloud authorization. Use the current installed manager guidance.

Read 01-INDEX.txt, then selected cards/images. Do not load all library.json, KNOWLEDGE or images into context. Stored review statuses are historical; inspect images needed for present findings. No cloud refresh or synchronization has been performed by packaging.
