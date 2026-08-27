# NimbusNote — Troubleshooting

## "My note didn't sync"

First check the sync indicator in the top-right corner of the app. A grey cloud icon means the note is queued but hasn't synced yet — this is normal if you're offline. A red cloud icon means sync failed after retrying, and usually means your session has expired; sign out and back in to fix it.

If the icon is green but changes still aren't showing on your other device, it's almost always because the other device is more than 5 minutes stale in the background — bring the app to the foreground on that device to force an immediate sync.

## "I see two versions of the same note"

This happens when the same note was edited on two devices within the same sync window (see the Getting Started guide for how sync timing works). NimbusNote does not auto-merge conflicting edits. Open the note and use the "Compare versions" button to manually pick which version to keep, or keep both as separate notes.

## "I can't upload an image"

Image attachments are a Pro and Team plan feature only. If you're on the Free plan, uploading an image will show an upgrade prompt instead of an error. If you're on Pro or Team and still can't upload, check that the image is under the 20MB limit — larger files fail silently in the current app version, which is a known issue on the roadmap to fix.

## "My workspace says it's over its notebook limit"

This happens only on the Free plan (50 notebook cap) after a downgrade from Pro or Team. You won't lose any notebooks, but you won't be able to create new ones until you're back under the limit or you upgrade again.

## Account recovery

If you're locked out, use the "Forgot password" link on the sign-in page. Password reset emails expire after 1 hour. There is currently no SMS-based recovery option.
