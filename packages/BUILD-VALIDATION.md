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
