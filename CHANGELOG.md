# Changelog

## [1.0.1] - 2025-10-24

### Fixed
- Critical bug in underperformer identification logic (changed OR to AND)
- Now correctly identifies articles with both low views AND low engagement

### Added
- API request timeout handling
- Better error messages for invalid API keys and network issues
- Null and empty value checks throughout codebase
- Division-by-zero safety checks

### Credits
- Thanks to Pascal CESCATO (@pcescato) for identifying the underperformer logic bug

## [1.0.0] - 2025-10-22

### Initial Release
- Full analytics dashboard for DEV.to articles
- Tag performance analysis
- Growth trend tracking
- Underperformer detection
- Export to JSON/CSV
