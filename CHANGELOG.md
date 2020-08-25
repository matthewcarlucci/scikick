# Changelog

Chronological changes to scikick are summarized below.

## Unreleased - August 25th 2020

### New Features

- Allow for convenient single page runs with `sk run my.Rmd` usage
- Single page status usage as `sk status my.Rmd`
- Add `--copy-deps` to `sk add` for duplicating file dependencies
- Index page is now defined by user with `sk add <path to index file>` 
instead of auto-detected

### Changes

- sk status fixes
- Tested and fixed renv compatibility
- Better indications of snakemake errors during `sk run`
- Default index page is appended to any added index page
- Requirement of git2r version >= 0.27.1
- Fix git warnings and other outputs
- Add checks for scikick.yml format
- Other bug fixes

## 0.1.1

- Initial release
