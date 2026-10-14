# Ready for a test drive — 2026-10-14

## Scopuli

Open **gedit-** from the application menu or run
`~/Applications/gedit-/run-prototype`. The current window is titled **gedit-**.
If an older **gedit- — Prototype** window remains, save/close it manually; it
runs the earlier version and was not forcibly closed.

Separate launcher:
`~/.local/share/applications/com.greenfinch628.gedit.qtprototype.desktop`.
No existing gedit launcher or file-type default was changed.

## Miller

Open **~/Applications/medit-next.app** for the updated Mac review build:

```sh
open ~/Applications/medit-next.app
```

Original **medit-.app** remains unchanged. Review identity is
`com.greenfinch628.medit.review`, with independent preferences and recovery in
`~/Library/Application Support/medit-next-review/`. It starts without production
documents; open the files/folders you want to test.

Edited authoritative source: `~/XcodeProjects/medit-/medit-/`.
Optimized review build: `~/XcodeProjects/medit-/build/review-next/`.

## Try in both

1. Compare smaller typography, shorter tabs and larger sidebar text.
2. Open Preferences → Fonts / Editing / Appearance / Spelling.
3. Right-click a tab, pick a color, close/reopen and confirm it persists. Dark
   colors should retain readable titles and controls.
4. Change Tab Width and Spaces at the bottom. Try Tab in ordinary text and an
   Alt-drag / Option-drag rectangle. Preferences set new-document defaults.
5. Open .sh/.txt/.md; check syntax colors and toggle spelling.
6. Pin/reorder tabs, search/replace and use Open/Save dropdowns.
7. Type unsaved text, close without saving, reopen: it should return without
   having been saved to the original file.
8. Explicitly close a tab and restore its recovery copy. Fedora: Ctrl+Shift+T /
   Open → Restore Closed Tab…. Mac: application menu → Restore Closed Tab.
9. Switch/close folders and open another window. Check remembered documents,
   sidebar state and independent loose-document sessions.

## Validation and preservation

- Fedora: 11 core check groups, 14 next-step groups and a separate second-launch
  check. Covers real block-editing input, encoding/save failures, external
  changes, recovery failures/crashes, workspace/tree restoration, pinning,
  replace undo and read-only Git scanning.
- Miller: optimized review build succeeds; all 130 self-tests pass, including
  tab-width/spaces/color and spelling checks.
- Each app's own interface capture was inspected. Native decorations, dialogs,
  scrollbar styles and font rendering still reflect the operating system.
- Legacy Fedora launcher/binary/.gitignore hashes are unchanged; its working
  tree remains clean. Legacy runtime was not launched.
- Installed production medit binary hash remains
  `134476e8e370cbe16dc3b2a396c500d1080450b2b7514049cc8df2f8699035d9`.
- Source backups exist under each project's build folder.
- An interrupted Mac layout test added three fixture paths to Recent Items.
  Only those three were removed; all seven pre-existing entries were retained.
  Further tests ran under the separate review identity.

The original new-project .gitignore refinements were retained. Legacy and production medit recovery data
were neither migrated nor shared with the new/review editors.

## Practical differences

GTK's Open dialog cannot choose files and directories together, so Fedora has
Workspace…. Native find/font dialogs differ between Qt and AppKit. Spelling
dictionaries and ambiguous eight-bit encoding detection may differ. Different
syntax engines can produce different token colors.

Recovery is debounced: it cannot guarantee the last fraction of a second before
a power failure. Failed recovery prevents an orderly close.

Pause further sustained work if remaining usage reaches 9%; check both usage
windows and do not consume reset credits automatically.

Syntax and spelling refinements: Editing has Enable syntax highlighting, with
one fixed scheme, with Xcode Default Light colors for Bash. Left-click an underlined misspelling for suggestions
and × Ignore. Ignore is document-local and recovered with that document.
Personal dictionary learning remains a future explicit Add to Dictionary action.

Welcome follow-up: pinned on startup; unpinning or disabling Show Welcome on startup dismisses it and suppresses session restoration. Unsaved Welcome edits are archived. Added dedicated Fedora checks and five Mac checks. Both supplied Welcome examples now begin with “A familiar place to write, designed to be pleasant to use.” Unchanged personal copies migrate; edited copies stay intact.

Tab Rename: named files move within their current folder without saving pending edits; untitled documents save as UTF-8 in the sidebar root, or use Save As when no folder is open. Existing paths and open destination tabs are refused. Other open windows, stored session/closed-tab references, recent files and sidebar Git state follow the rename. Fedora rename and cross-window checks pass; the Mac review build passes 130 checks.

Bash colors now follow Xcode Default (Light), read from the installed Xcode theme on Miller: comments #5d6c79, keywords #9b2393, strings #c41a16, numbers #1c00cf, variables #326d74, command substitutions #6c36a9. Fonts and non-Bash highlighting remain unchanged. Qt checks verify token colors, plain-text preservation and disabling syntax.

Sidebar file menu: Rename handles closed and open files; Delete confirms and moves the file to Trash. Open copies retain their text as unsaved documents, and stored recovery references detach from the deleted path. Cancel and Trash failure preserve the file. Folder actions are excluded. New checks use isolated fixtures rather than the user’s Trash.
