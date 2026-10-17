# Package validation — 2026-10-16

Version 0.1.1, package revision 1, includes the Ptyxis-style color chooser
with six shade rows and #e8e8e8 background, plus spelling character hit-testing.

Fedora 44 x86_64: RPM built natively and RPM digest verification passed.
The extracted RPM passed chooser rendering/selection, spelling boundary and
Unicode clicks, editor regression checks, and single-instance startup checks.
The Qt xcb desktop plugin has no missing libraries. The RPM was not installed
system-wide; existing per-user source installations remain in place.

Ubuntu 26.04 amd64: DEB built natively in an Ubuntu container and installed
through apt with its declared dependencies. Chooser rendering/selection,
spelling clicks, editor regression checks and startup checks passed with the
packaged dependencies. The chooser check imported the installed application.
The Qt xcb desktop plugin has no missing libraries. Git was added to the test
container for the Git-related regression checks.

These offscreen checks do not replace interactive desktop acceptance testing.
Packages are unsigned. SHA256SUMS covers the current and baseline artifacts.

---

# Baseline package validation — 2026-10-15

Version 0.1.0, package revision 1. Application source baseline c4256f8.
Fedora 44 x86_64: RPM built, digest verification and dependency/installation
dry run passed. Extracted RPM launched offscreen and produced a preview.
Ubuntu 26.04 amd64: DEB built natively in Ubuntu; apt installed the final
package with declared dependencies; the installed nex-editg command launched
offscreen and produced a preview. Qt xcb desktop plugin has no missing libraries.
Core check_prototype.py editing tests passed using packaged Python libraries
on both Fedora and Ubuntu. No app behavior changes were made for packaging.
These checks do not replace an interactive desktop acceptance test.
