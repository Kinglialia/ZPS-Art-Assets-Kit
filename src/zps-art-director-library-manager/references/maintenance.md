# Maintain library.json schema 2

Canonical source: library.json. The cards, INDEX, KNOWLEDGE, and gallery (if released) are built from it. maintain.py builds the TXT files. The gallery has its own build tool, and it is not updated by the same command by default. The maintain.py file in the library package checks and rebuilds the TXT files with Python 3.11+. It makes no network calls. If Python is not available, you can do an equivalent procedure with another tool in the environment.

Entry: id, name, category, example, source_url, checked_at (YYYY-MM-DD), version (positive integer), status (INDEX_ONLY/DRAFT/READY), card, source_summary, observed, ad_inference, validation_suggestion, limitations, rights, visual_review, games, media. The fields image/image_sha256/image_source_url point to the first image of media. card_drive_url keeps the link to the cloud record.

Media: file (relative path in the package), source_url, game, credit, official_url (null if the source does not provide it), sha256, width, height, visual_review; drive_url and drive_id after sync. Record reviewed only when you really opened the image. An image that was checked for decode/hash but not viewed must be recorded separately. In a review record, state the file/hash or image version, the date, and the scope viewed, when known. You can write it in an existing description field. Do not change the schema on your own. When you replace an image or change the representative image, check observed, ad_inference, and the conclusions that depend on the image again. Keep the history and mark the parts that need review. Do not inherit a review from a previous image. Do not treat a record from a previous person or session as a new observation.

## General preparation

Identify the write target and the approved scope according to the project rules. Distinguish the local working copy from the canonical library. A request to edit the local copy does not authorize publishing to Drive. Check which maintenance tools are really in the package. The skill repo does not include maintain.py, build_gallery.py, or images. If they are missing, do only the equivalent checks that you can do, and report the parts you did not do.

Keep the old ID and source. Raise the version when the content changes. Normalize URLs to find duplicate candidates. Keep query strings that have meaning. Check identity before you merge. Do not treat a changed URL as a new reference by default. Create a DRAFT when data is missing. Preserve image bytes, credits, and history. Do not replace an image with another game to fill a gap.

## Update the local copy

1. Record the initial version/hash of the relevant data. Keep the pre-edit copy in the history/backup location that the task scope defines. Do not rely on chat as history.
2. Edit the working copy. Do QA on: ID/URL, required fields, paths, image decode/size/hash, image matches media[0], credits, and links. Check snapshot coverage only if it is in scope. The image review status must reflect the real evidence.
3. Check the local baseline again before you replace files. If another change exists, reconcile. Rebuild the affected readable outputs: cards, INDEX, KNOWLEDGE, and gallery if there is one. Compare them against the same release/version. Update the manifest if the package has a manifest and a declared file changed. Keep the old baseline in the history.
4. Read the output files again. Report "updated locally", the location, the QA, and the missing parts. If you saved only to a temporary workspace, state clearly that it is not stored durably. Do not treat Drive as synced. Return the result to the storage location that the user specified, within the permitted scope.

## Sync Drive when assigned

1. Read the current cloud version/metadata before you prepare to write, and keep it as a baseline. An old receipt does not replace this step. Store the old version in the defined history. Keep the old ZIP for a major release.
2. Prepare the working copy and do QA by the local steps. Before upload, check the cloud baseline again. Reconcile when another edit exists. Update the old file by ID to keep the link. Upload a new file when needed. Do not change sharing.
3. Upload images first. Record the returned ID/URL in the data and in the receipt. Rebuild the cards and the readable outputs that depend on the new links, then upload the cards, library, INDEX, KNOWLEDGE, gallery (if released), QA, and the receipt. A checkpoint must state clearly what is saved and what is pending. Check the target before you retry after a timeout.
4. Read back the count, IDs, bytes, and checksum if the tool supports it. Compare the canonical data with the readable outputs of the same version. Report only what you verified. If interrupted, state which copy is new, which copy is still old, and the recovery step. Do not claim an atomic transaction.

Command: python3 maintain.py --coverage checks the saved snapshot and rebuilds the TXT files. This is not a read-only command. Adding --cloud only requires a valid cloud URL in the local data. It does not call Drive. It does not verify that the file exists, the access permission, or the remote content. Report the local check, the snapshot comparison, and the live Drive readback separately, with the time each was done. When the website changes, update the snapshot from a real observed source. Do not edit the snapshot only to make a test pass.

To add a reference from another source: use a new namespace + a stable slug, a real source URL, and the same schema. No skill edit is needed. Raising the version is the responsibility of the maintenance step. The validator does not prove that the content deserves a version increase. Do not run automatically because a file appears in the Inbox.

An image check by script needs Pillow (requirements.txt in the ZIP). The validator decodes images and compares size/hash. Decoding does not replace a visual review. If Python/Pillow is not available, use a tool that can do an equivalent check, and record exactly which checks were run.

Check the connector/API capability that is really available in the session: read metadata, checksum, and write conditions if supported. Do not infer that a connector has all the capabilities of the Drive API. The Drive-side version and the library entry/release version have different meanings. Use the cloud metadata as the baseline for remote changes. It does not replace the content version. If the tool supports conditional write, use the condition that you read to detect conflicts, and reconcile when the condition fails. Reading back the version before writing only reduces the race condition. It does not remove it completely. If there is no conditional write, only one person/agent maintains the library at a time. If you find a concurrent edit, stop writing the old copy and reconcile. Do not claim a transaction or absolute race protection.

## Refresh the website when assigned

Compare new/changed/removed entries against the snapshot. Check each style and image separately, including gallery/lazy loading. Remove duplicates by content/identity. Do not remove a different image only because it comes from the same game. Record the source of errors and the resolution. Keep the history of entries that were removed from the website. Do not delete saved data on your own. Report the local result, the snapshot comparison, and the live Drive verification separately.
