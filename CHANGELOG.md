# Changelog

Chronological changes to scikick are summarized below.

## Unreleased - [release date] 2020

### New Features

- Allow for convenient single page runs with `sk run my.Rmd` usage
- Single page status usage as `sk status my.Rmd`
- Add `--copy-deps` to `sk add` for duplicating file dependencies
- Index page is now defined by user with `sk add <path to index file>` 
instead of auto-detected
- Add git SHA to site git logs

### Changes

- Many sk status adjustments
- More detailed `sk add -d` output
- Better outputs for errors and warnings during `sk run`
- Tested and fixed renv compatibility
- Default index page is appended to any added index page
- Requirement of git2r version >= 0.27.1
- Fix git warnings and other outputs
- Add checks for scikick.yml format
- Other bug fixes

## 0.1.1

- Initial release
