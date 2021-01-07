# Changelog

Chronological changes to scikick are summarized below.

## 0.2.0 - TBD

### New Features

- Added experimental support for `.ipynb`
- Website menus are processed to be more human readable (#1) 
- Individual page log files stored in report/logs
- Allow for global rmarkdown/pandoc yaml in scikick.yml
- Dump full logs after snakemake error
- Include the default homepage in sk status

### Changes

- Remove custom CSS for rmarkdown::html_document
- Snakemake requirement bumped to >= 5.9 due to use of custom logger
- New sk status message (detect unknown execution reasons)
- Fix issue #2 for sk add -d usage
- More checks for scikick.yml state (e.g. sk version in use)
- Minor changes to footer/homepage content (include scikick.yml)
- Reduce outputs in sk init and other
- New sk init template

## 0.1.2 - September 9th 2020

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
