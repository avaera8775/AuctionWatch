# AuctionWatch

A standalone desktop app for browsing **FFXI items** and their **live Auction House
history** — search any item, read its description, and pull recent sales, current
listings, and price ranges from any world's search server. **The game does not
need to be running.**

It's a personal, self-hosted "FFXIAH" that talks to the same search servers the
game and community sites use.

**Project home:** https://github.com/BalladOfWorms/AuctionWatch

---

## Running it

**If you have the built `AuctionWatch.exe`:** just double-click it. Nothing to
install — the item database is baked in.

**If you're running the script (`AuctionWatch.py`):** you need Python 3 (the
standard Windows installer includes everything — `tkinter` ships with it, no
`pip install` required). Keep `ffxi_items.json` in the same folder, then:

```
python AuctionWatch.py
```

---

## Using it

- **Search** — type part of an item name; results list on the left. Sorted so the
  closest / shortest matches surface first.
- **Right-click** a result → opens that item's **BG-wiki** page in your browser.
- **Click** a result → the right pane shows its name, id, category, stack size,
  and description, then loads its Auction House data.

**Auction data (right pane):**
- **Sold history** — the most recent sales (date/time, price, seller → buyer).
  The server returns up to 10 singles and 10 stacks per item; that's a hard
  limit on its end, same as in-game and FFXIAH.
- **All / Singles / Stacks** buttons — filter the table; the price summary
  (low / med / high) follows the filter so single and stack prices never blend.
- **On sale now** — how many singles and stacks are currently listed.
- **Sortable columns** — click any header (Sold, Price, Seller, Buyer) to sort;
  click again to reverse.

**Worlds:**
- Pick your **World** from the dropdown. With an item open, switching worlds
  re-pulls it live on that server, so you can compare prices across worlds.
- **All 16 worlds** ship with their search-server address already filled in.
- **Address / Save / Detect** — if a world's address is missing or ever stops
  working (Square Enix occasionally renumbers them), fix it here:
  - **Detect** (game running, logged into that world): do one in-game `/search`
    or open the AH, then click **Detect** — it reads that world's search-server
    IP straight from your PC's network connections and fills the Address box.
  - **Save** writes it to `%APPDATA%\AuctionWatch\servers.json`, so it persists
    and overrides the built-in default for you.

---


## Notes & contributing

All 16 live worlds are included and occupy `124.150.154.61`–`124.150.154.76`.
Square Enix occasionally renumbers a world's search server; if one ever stops
returning results, use **Detect** on that world and **Save** to fix it locally.
If you confirm a changed address, an issue or PR at
https://github.com/BalladOfWorms/AuctionWatch keeps the shipped defaults current
for everyone.