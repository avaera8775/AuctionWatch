# Changelog

All notable changes to AuctionWatch are documented here.

## [1.0.2] — 2026-07-03

### Added

- **Equipment details** on the item info line — weapons and armor now show their **slot**, **level** (and item level where applicable), a decoded **Jobs** list, and a **Rare / Ex / Rare-Ex** tag.
- **Right-click a search result** for a menu: **Open on FFXIAH** or **Open on BG-wiki**.
- **Remembers its layout** — window size/position and column widths persist between runs (saved to `%APPDATA%\AuctionWatch\ui.json`).

### Changed

- **Singles / Stacks filter** on the auction history, with the price summary following the selected filter.

## [1.0.1] — 2026-07-03

### Added

- Search-server addresses for the final two worlds, **Odin** and **Asura**. All 16 live worlds now ship pre-filled and work out of the box (they occupy `124.150.154.61`–`124.150.154.76`).

## [1.0.0] — 2026-07-03

### Added

- Initial release — search FFXI items by name (23,503 items with descriptions, categories, and stack sizes), pull live cross-server Auction House data (recent sales, on-sale counts, price ranges), split **Singles / Stacks**, sortable columns, right-click a result to open its BG-wiki page, self-detecting server addresses via **Detect**, and 14 worlds preloaded.