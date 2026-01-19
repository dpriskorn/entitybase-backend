# Repository Classes Overview

This document describes the repository classes that handle data access to Vitess.

## Architecture Notes

- **Connection Management**: All repositories receive a `connection_manager` for database access
- **Transaction Safety**: Methods should be called within connection contexts
- **Error Handling**: Repositories raise exceptions for database errors
- **Performance**: Methods are optimized for common query patterns
- **Data Integrity**: Foreign key relationships are maintained at the application level

