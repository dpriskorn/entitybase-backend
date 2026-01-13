# WMF RecentChange Schemas

This directory contains JSON schemas for Wikimedia MediaWiki RecentChange events.

## Schema Versions

- `latest/`: Symlink to current latest version

## Updating Schemas

Schemas are manually maintained. To update:

go to external/schemas-event-primary and run `git pull`

## Usage

These schemas are used for validating incoming RecentChange events from the Wikimedia Event Platform.