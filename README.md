# Are L1 MEV Heuristics Trustworthy on L2 Rollups?

**A Post-EIP-4844 Evaluation with Plausibility Filters**

> Tofu Mining: Kaixin Du (kdu9), Qinan Sun (qsun31), Oliver Yuan (xyuan38)

## Motivation

Existing MEV (Maximal Extractable Value) detection tools were designed for Ethereum L1, where miners/validators control transaction ordering via a public mempool. On Layer-2 rollups like Arbitrum, a centralized sequencer determines ordering and there is no public mempool — yet researchers continue applying L1 heuristics unchanged. This leads to **massive false positives**, particularly for sandwich attack detection, because "coincidental ordering" often mimics sandwich patterns.

Furthermore, **EIP-4844** (March 2024) introduced blob transactions that fundamentally changed L2 fee economics, making pre-4844 datasets and tools outdated.

## Problem

- L1 sandwich heuristics produce high false-positive rates on L2 due to coincidental ordering.
- Existing studies either diagnose the problem without proposing solutions (Gogol et al.) or train models on biased labels (Chen et al.).
- No prior work provides a reusable filtering methodology for post-EIP-4844 L2 data.

## Goal

Systematically evaluate the reliability of existing MEV detection heuristics on Layer-2 rollups in the post-EIP-4844 period. Rather than replacing current tools, we design **independent plausibility filters** that layer on top of existing detectors to eliminate false positives.

## Methodology

1. **Baseline**: Apply standard L1 MEV heuristics (sandwich, arbitrage, liquidation) to Arbitrum swap data.
2. **Plausibility Filters**: Design independent filters to flag and remove false positives — e.g., profit feasibility checks, sender behavior analysis, timing constraints.
3. **Evaluation**: Quantitative comparison of detection accuracy before and after filtering.

## Project Structure

```
ETH_Data/
├── fetch.py                  # Dune Analytics data fetcher (incremental saving)
├── eth_2026.1.1.csv          # Raw Arbitrum swap data (Jan 2026)
├── Project proposal.pdf      # Full project proposal
└── README.md
```

## Data

Swap-level data is fetched from [Dune Analytics](https://dune.com/) covering **Arbitrum DEX swaps** in January 2026 (post-EIP-4844).

| Field | Description |
|-------|-------------|
| `block_number` | Arbitrum block number |
| `block_time` | Block timestamp (UTC) |
| `tx_hash` | Transaction hash |
| `tx_index` / `evt_index` | Ordering within block |
| `sender` | Transaction sender |
| `pool` | DEX pool address |
| `token_bought_*` | Bought token address, amount, symbol |
| `token_sold_*` | Sold token address, amount, symbol |
| `amount_usd` | Swap value in USD |

## Usage

```bash
# Install dependencies
pip install requests pandas

# Fetch data from Dune (requires API key)
python fetch.py
```

The fetcher supports incremental saving — data is flushed to disk periodically and on any interruption (Ctrl+C, credit exhaustion, errors).

## References

1. P. Daian et al., "Flash Boys 2.0: Frontrunning in Decentralized Exchanges, Miner Extractable Value, and Consensus Instability," *IEEE S&P*, 2020.
2. K. Qin, L. Zhou, and A. Gervais, "Quantifying Blockchain Extractable Value: How dark is the forest?" *IEEE S&P*, 2022.
3. K. Gogol et al., "How to Serve Your Sandwich? MEV Attacks in Private L2 Mempools," *arXiv:2601.19570*, Jan. 2026.
4. C. F. Torres et al., "Rolling in the Shadows: Analyzing the Extraction of MEV Across Layer-2 Rollups," *ACM CCS*, 2024.
5. Y. Chen et al., "Mecon: A GNN-based Framework for MEV Detection," 2025.
6. B. Yang et al., "SoK: MEV Countermeasures — Theory and Practice," *CCS Workshop*, 2024.
7. A. Solmaz et al., "When Priority Fails: Optimistic MEV on Layer 2," *Nethermind Research*, 2025.
