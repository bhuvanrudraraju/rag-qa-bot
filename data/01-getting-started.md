# NimbusNote — Getting Started

NimbusNote is a lightweight note-syncing service used internally for this exercise. It is fictional — do not look for a real product by this name.

## Creating a workspace

Every user starts by creating a workspace. A workspace is identified by a lowercase slug (letters, numbers, and hyphens only) and can hold up to 50 notebooks on the Free plan, or unlimited notebooks on the Pro plan.

To create a workspace, send a `POST /workspaces` request with a `name` field. The server responds with a `workspace_id` that you'll use in every subsequent request.

## Creating your first note

Notes belong to notebooks, and notebooks belong to workspaces. A brand-new workspace automatically gets one notebook called "Inbox". You can create a note directly inside Inbox with `POST /notebooks/{id}/notes`.

Notes support Markdown formatting. Images are not supported in the Free plan; Pro plan workspaces can attach up to 20MB of images per note.

## Sync behavior

NimbusNote syncs every 15 seconds while the app is in the foreground, and every 5 minutes in the background. If two devices edit the same note within that sync window, NimbusNote keeps both versions as separate note revisions rather than silently merging them — the user is asked to pick which version to keep the next time they open the note.

## Offline mode

All notes are available offline once they've synced at least once. Notes created while offline are queued and sync automatically once the connection returns. There is no limit to how long a note can stay queued offline.
