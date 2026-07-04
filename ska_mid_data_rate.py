"""
Estimate the typical data rate of the SKA-Mid telescope under its current
(SKA1) baseline design.

Two rates are modelled, corresponding to two points in the SKA-Mid data path:

  1. Digitised ("raw voltage") rate -- from the 197 dishes to the
     Correlator/Beamformer (CBF).
  2. Visibility (correlator output) rate -- from the CBF to the Science
     Data Processor (SDP).

Design numbers used below come from public SKAO material:
  - SKA1 System Baseline Design, SKA-TEL-SKO-0000002
  - Braun et al. 2019, "Anticipated Performance of the SKA1", arXiv:1912.12699
  - SKAO Telescope Specifications: skao.int/en/science-users/118
  - 133 SKA dishes @ ~100 Gb/s + 64 MeerKAT dishes @ ~40 Gb/s digitiser
    output (~15.8 Tb/s combined raw ingest); correlator dump (integration)
    time of 0.14 s; 65 536 max frequency channels; 19 306 baselines.

Run this file directly to print a summary table of the results.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Band:
    name: str
    f_low_hz: float
    f_high_hz: float

    @property
    def bandwidth_hz(self) -> float:
        return self.f_high_hz - self.f_low_hz


# SKA-Mid observing bands (0.35-15.4 GHz), per SKAO telescope specifications.
BANDS = [
    Band("Band 1", 0.35e9, 1.05e9),
    Band("Band 2", 0.95e9, 1.76e9),
    Band("Band 5a", 4.6e9, 8.5e9),
    Band("Band 5b", 8.3e9, 15.4e9),
]

# Array composition.
N_SKA_DISHES = 133
N_MEERKAT_DISHES = 64
N_DISHES_TOTAL = N_SKA_DISHES + N_MEERKAT_DISHES  # 197

# Per-dish digitiser output, as published for the current design.
SKA_DISH_RATE_BPS = 100e9       # ~100 Gb/s per SKA1 dish
MEERKAT_DISH_RATE_BPS = 40e9    # ~40 Gb/s per MeerKAT dish

# Correlator/visibility parameters.
N_POL_PRODUCTS = 4       # XX, XY, YX, YY
BYTES_PER_VIS = 8         # 32-bit real + 32-bit imaginary
DUMP_TIME_S = 0.14        # correlator integration ("dump") time
N_CHANNELS_MAX = 65536    # max spectral channels for imaging mode


def raw_ingest_rate_bps() -> float:
    """Total digitised data rate from all dishes into the CBF."""
    return (N_SKA_DISHES * SKA_DISH_RATE_BPS
            + N_MEERKAT_DISHES * MEERKAT_DISH_RATE_BPS)


def n_baselines(n_dishes: int = N_DISHES_TOTAL) -> int:
    return n_dishes * (n_dishes - 1) // 2


def visibility_rate_bps(n_channels: int = N_CHANNELS_MAX,
                         dump_time_s: float = DUMP_TIME_S,
                         n_dishes: int = N_DISHES_TOTAL) -> float:
    """Full-resolution correlator output rate delivered to the SDP."""
    bits_per_dump = (n_baselines(n_dishes) * N_POL_PRODUCTS
                     * n_channels * BYTES_PER_VIS * 8)
    return bits_per_dump / dump_time_s


def to_tbps(bits_per_second: float) -> float:
    return bits_per_second / 1e12


def to_gb_per_s(bits_per_second: float) -> float:
    return bits_per_second / 8 / 1e9


def to_pb_per_year(bits_per_second: float) -> float:
    seconds_per_year = 365.25 * 24 * 3600
    return bits_per_second / 8 * seconds_per_year / 1e15


def main() -> None:
    print("SKA-Mid typical data rate (current SKA1 baseline design)")
    print("=" * 60)
    print(f"Dishes: {N_SKA_DISHES} SKA + {N_MEERKAT_DISHES} MeerKAT "
          f"= {N_DISHES_TOTAL}")
    print(f"Baselines: {n_baselines():,}")
    print()

    raw = raw_ingest_rate_bps()
    print("1. Raw digitised data (dishes -> Correlator/Beamformer)")
    print(f"   {to_tbps(raw):.1f} Tb/s  ({to_gb_per_s(raw):.0f} GB/s)")
    print()

    vis = visibility_rate_bps()
    print("2. Full-resolution visibility data (Correlator -> SDP)")
    print(f"   channels={N_CHANNELS_MAX}, dump time={DUMP_TIME_S} s")
    print(f"   {to_tbps(vis):.1f} Tb/s  ({to_gb_per_s(vis):.0f} GB/s)")
    print(f"   ~{to_pb_per_year(vis):,.0f} PB/year if sustained continuously")
    print()

    print("These figures are consistent with SKAO's published order-of-")
    print("magnitude estimates for the current design: ~15-19 Tb/s raw")
    print("dish ingest, and multi-Tb/s (order 10 Tb/s peak, ~2-3 Tb/s")
    print("typical averaged) visibility throughput into the SDP.")


if __name__ == "__main__":
    main()
