# Initial authoritative reference inventory — 2026-10-14

This records the inspection before implementation. Later source, layout and review-build changes are documented in README.md and REVIEW.md.

## Scopuli

- Host confirmed as `scopuli`; new repository `/home/rczys/Applications/gedit-`
  is on `main`, initially `97d7513`.
- Its pre-existing uncommitted `.gitignore` adds build/dist and Python generated
  output rules. Those lines are preserved; only `.venv/` is added for this work.
- Legacy repository `/home/rczys/Applications/gedit-drafts` is clean at `ce91744`.
  Local expanded source, installed files, README and screenshot were inspected.
- `/home/rczys/.local/bin/gedit` runs the legacy
  `/home/rczys/Applications/gedit-drafts/install/bin/gedit`.
- Legacy runtime was not launched. Its runtime functionality remains unconfirmed.
- No applicable AGENTS.md was found in either application tree or parent home /
  Applications directories. The chat's AGENTS.md requires synced sources to stay
  read-only; they were not changed.

## Miller

- Current source `/Users/rczys/XcodeProjects/medit-` is clean at `72a7e98`.
  Local source takes precedence over either remote; no fetch/reset was needed.
- Read `main.swift`, `Session.swift`, `Workspace.swift`, `BlockTextView.swift`.
- Installed `/Users/rczys/Applications/medit-.app` identifies as
  `com.greenfinch628.medit`, version 0.3 build 4.
- Installed binary SHA-256:
  `134476e8e370cbe16dc3b2a396c500d1080450b2b7514049cc8df2f8699035d9`.
  No matching local build product was available for binary comparison; exact
  installed/source equivalence has not been established.
- Saved interface font is `.AppleSystemUIFont`, saved editor size is 16; no
  saved editor-font or interface-size override was found. Source defaults use
  Menlo at 16 and interface size 17.
- No AGENTS.md was found in the medit tree. Miller source, app and defaults were
  read only; no application was launched or rebuilt there.

## Interface mapping

| Item | Current medit reference | Fedora prototype |
| --- | --- | --- |
| Window | Native controls, 1060×720 initial content, 640×400 minimum | Native controls; same initial/minimum sizes |
| Header | Open/arrow, sidebar, new on left; Save/arrow, menu on right | Same order, 62 px header |
| Open | Open…, Open Recent, New File, New Window, Close File, Close Folder | Same commands; Workspace… added after Open Recent |
| Folder choice | Native Open panel accepts files and directories | Native Open file dialog plus dedicated Workspace directory dialog |
| Save | Save, Save As…, Save All | Same order |
| App menu | Preferences…, Help, About medit- | Preferences…, Help, About gedit- |
| Tabs | 220–360 px, dirty `*`, pin, close, blue underline | Same width range and controls; pin before title in Qt tab strip |
| Sidebar | Starts collapsed, approximately 240 px wide | Starts collapsed; folder browser only |
| Status | Plain Text, Tab Width: 2, Ln/Col, INS | Same order, 38 px footer |
| Palette | header d8, sides e0, active tab e8, inactive/sidebar f8 | Same sRGB values; white editing area |
| Editor | Menlo 16, gutter 54, tabs 2, no wrapping | DejaVu Sans Mono 12 pt (~16 logical pixels), gutter 54, tabs 2, no wrapping |
| Blocks | Option-drag, row typing/paste, short-row space padding, Escape | Alt-drag, same tested operations |

QScintilla's Linux backend hardcodes Control at the initial block-selection
click. The editor maps Alt to that initial native event while leaving the
subsequent native selection and drawing to QScintilla. Standard multiline
QScintilla paste repeats the complete clipboard on each selection; prototype
paste distributes one clipboard row per selected row to match medit.

Dependency selection was checked against Riverbank's official Qt 6 installation
instructions: https://www.riverbankcomputing.com/software/qscintilla/download

This mapping is based on current local source inspection. Visual and hands-on
comparison with the running installed medit application remains a user review
step; full parity is not claimed.
