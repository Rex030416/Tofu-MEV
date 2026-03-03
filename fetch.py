"""
Fetch Arbitrum swap data from Dune Analytics API with incremental saving.
"""

import os
import time
import requests
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────
API_KEY  = "iTRTbjTgkDJJ0RPVYulNW15fRkm25MU0"
QUERY_ID = 6773275
OUTPUT   = "arb_swaps_jan2026.csv"
BATCH    = 10_000          # rows per API call
SAVE_EVERY = 5             # flush to disk every N batches (50k rows)

# ── Helpers ─────────────────────────────────────────────────────────

def save_rows(rows, path, append=False):
    """Write rows to CSV. If append=True, skip header to avoid duplicates."""
    df = pd.DataFrame(rows)
    if "tx_index" in df.columns:
        df = df.sort_values(["block_number", "tx_index", "evt_index"]).reset_index(drop=True)
    if append and os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)
    return len(df)


def print_summary(path):
    """Print basic stats from the saved CSV."""
    df = pd.read_csv(path)
    print(f"\nSaved {len(df)} rows to {path}")
    print(f"Range:   {df['block_time'].min()} ~ {df['block_time'].max()}")
    print(f"Blocks:  {df['block_number'].nunique()} | Senders: {df['sender'].nunique()}")

# ── Main fetch loop ────────────────────────────────────────────────

headers = {"X-Dune-API-Key": API_KEY}
rows = []
offset = 0
total_saved = 0
batches_since_save = 0

try:
    while True:
        url = (f"https://api.dune.com/api/v1/query/{QUERY_ID}/results"
               f"?limit={BATCH}&offset={offset}")
        resp = requests.get(url, headers=headers)

        # Stop if credits are used up
        if resp.status_code == 402:
            print(f"Credits exhausted. Saving {len(rows)} buffered rows...")
            break

        # Back off on rate limit
        if resp.status_code == 429:
            print("Rate limited, waiting 30s...")
            time.sleep(30)
            continue

        resp.raise_for_status()
        batch = resp.json()["result"]["rows"]

        # No more data available
        if not batch:
            break

        rows.extend(batch)
        offset += BATCH
        batches_since_save += 1
        print(f"Fetched {total_saved + len(rows)} rows (buffer: {len(rows)})...")

        # Periodically flush buffer to disk to limit memory usage
        if batches_since_save >= SAVE_EVERY:
            n = save_rows(rows, OUTPUT, append=(total_saved > 0))
            total_saved += n
            print(f"  -> Flushed {n} rows to disk (total: {total_saved})")
            rows.clear()
            batches_since_save = 0

        time.sleep(1)

except KeyboardInterrupt:
    print(f"\nInterrupted! Saving {len(rows)} buffered rows...")
except Exception as e:
    print(f"Error: {e}. Saving {len(rows)} buffered rows...")
finally:
    # Always flush remaining buffer to disk before exit
    if rows:
        n = save_rows(rows, OUTPUT, append=(total_saved > 0))
        total_saved += n

    if total_saved:
        print_summary(OUTPUT)
    else:
        print("No data fetched.")
