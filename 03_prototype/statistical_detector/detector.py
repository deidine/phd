"""
Statistical Authorization Anomaly Detector (SAAD)
Contribution 2 of PhD Thesis

Author: Deidine Cheigeur
Date: 2026

Description:
    Detects DDoS attacks and lateral movement probes by monitoring
    Ory Keto authorization request logs using:
    1. Shannon entropy (Nychis et al., 2008) — detects DDoS concentration
    2. CUSUM (Blazek et al., 2001)          — detects slow-ramp attacks

    NO MACHINE LEARNING. Pure statistical methods.

References:
    - Chandola et al. (2009) ACM Surveys: https://doi.org/10.1145/1541880.1541882
    - Nychis et al. (2008) IMC: https://doi.org/10.1145/1452520.1452539
    - Blazek et al. (2001) IEEE: https://doi.org/10.1109/IWIAS.2001.935077
    - Ory Keto: https://www.ory.sh/docs/keto/

Requirements:
    pip install numpy scipy pandas
"""

import math
import time
import logging
import collections
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SAAD] %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────

WINDOW_SECONDS      = 10     # sliding window for entropy computation
BASELINE_SECONDS    = 600    # 10 minutes of normal traffic to establish baseline
ENTROPY_DROP_THRESH = 0.40   # 40% entropy drop triggers alert (Nychis et al.)
CUSUM_K_FACTOR      = 0.5    # CUSUM allowance = 0.5 × expected shift (Blazek et al.)
CUSUM_H_SIGMA       = 5.0    # CUSUM alert threshold: 5σ above baseline
LOG_PATH            = "/var/log/keto/access.log"


# ── Data Structures ───────────────────────────────────────────────

@dataclass
class Alert:
    timestamp: float
    alert_type: str       # "ENTROPY_DROP" or "CUSUM_SPIKE"
    service: str
    value: float
    threshold: float
    message: str


@dataclass
class CUSUMState:
    """CUSUM state for a single service-pair stream."""
    baseline_mean: float = 0.0
    baseline_std: float  = 1.0
    cusum: float         = 0.0
    k: float             = 0.0       # allowance (set after baseline)
    h: float             = 0.0       # threshold (set after baseline)
    baseline_samples: List[float] = field(default_factory=list)
    baseline_ready: bool = False


# ── Shannon Entropy ────────────────────────────────────────────────

def shannon_entropy(counts: Dict[str, int]) -> float:
    """
    Compute Shannon entropy of a distribution.
    H(X) = -Σ p(x) log₂ p(x)

    Parameters:
        counts: dict mapping target → request count

    Returns:
        entropy in bits [0, log₂(n)]

    Reference:
        Nychis et al. (2008) IMC: https://doi.org/10.1145/1452520.1452539
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def check_entropy_alert(current_H: float, baseline_H: float,
                        service: str) -> Optional[Alert]:
    """
    Alert if entropy drops by more than ENTROPY_DROP_THRESH × baseline.
    A sharp entropy drop = traffic concentrating on one target = DDoS.
    """
    if baseline_H == 0:
        return None
    drop_ratio = (baseline_H - current_H) / baseline_H
    if drop_ratio > ENTROPY_DROP_THRESH:
        msg = (f"DDoS suspected on {service}: entropy dropped "
               f"{drop_ratio:.1%} below baseline "
               f"(current={current_H:.3f}, baseline={baseline_H:.3f})")
        log.warning(f"ALERT: {msg}")
        return Alert(
            timestamp=time.time(),
            alert_type="ENTROPY_DROP",
            service=service,
            value=current_H,
            threshold=baseline_H * (1 - ENTROPY_DROP_THRESH),
            message=msg
        )
    return None


# ── CUSUM ─────────────────────────────────────────────────────────

def update_cusum(state: CUSUMState, x: float) -> Optional[float]:
    """
    Update CUSUM with new observation x.
    Returns alert value if threshold exceeded, else None.

    S(t) = max(0, S(t-1) + (x - μ₀ - k))
    Alert when S(t) > h

    Reference:
        Blazek et al. (2001): https://doi.org/10.1109/IWIAS.2001.935077
    """
    if not state.baseline_ready:
        state.baseline_samples.append(x)
        if len(state.baseline_samples) >= (BASELINE_SECONDS // WINDOW_SECONDS):
            samples = np.array(state.baseline_samples)
            state.baseline_mean = float(np.mean(samples))
            state.baseline_std  = float(np.std(samples)) or 1.0
            state.k = CUSUM_K_FACTOR * state.baseline_std
            state.h = CUSUM_H_SIGMA  * state.baseline_std
            state.baseline_ready = True
            log.info(f"CUSUM baseline ready: μ={state.baseline_mean:.2f} "
                     f"σ={state.baseline_std:.2f} h={state.h:.2f}")
        return None

    # CUSUM update (one-sided, upward)
    state.cusum = max(0.0, state.cusum + (x - state.baseline_mean - state.k))

    if state.cusum > state.h:
        val = state.cusum
        state.cusum = 0.0   # reset after alert
        return val
    return None


# ── Log Parser ────────────────────────────────────────────────────

def parse_keto_log_line(line: str):
    """
    Parse a single Keto access log line.
    Expected format (JSON-ish):
        timestamp,subject,object,relation,result

    Returns (subject, object) tuple or None on parse error.
    """
    try:
        parts = line.strip().split(",")
        subject = parts[1]
        obj     = parts[2]
        return subject, obj
    except (IndexError, ValueError):
        return None


# ── Main Detector ─────────────────────────────────────────────────

class StatisticalDetector:
    def __init__(self):
        self.window_counts: Dict[str, collections.Counter] = {}   # service → Counter
        self.baseline_entropy: Dict[str, float] = {}
        self.cusum_states: Dict[str, CUSUMState] = {}             # service-pair → state
        self.alerts: List[Alert] = []
        self.window_start = time.time()

    def ingest(self, subject: str, obj: str):
        """Process one Keto authorization request."""
        if obj not in self.window_counts:
            self.window_counts[obj] = collections.Counter()
        self.window_counts[obj][subject] += 1

        pair_key = f"{subject}→{obj}"
        if pair_key not in self.cusum_states:
            self.cusum_states[pair_key] = CUSUMState()

    def tick(self):
        """
        Called every WINDOW_SECONDS. Compute entropy and CUSUM for this window.
        """
        now = time.time()

        for service, counts in self.window_counts.items():
            total_requests = sum(counts.values())
            if total_requests == 0:
                continue

            # ── Entropy check ──────────────────────────────────
            H = shannon_entropy(dict(counts))

            if service not in self.baseline_entropy:
                self.baseline_entropy[service] = H
                log.info(f"Entropy baseline set for {service}: {H:.3f} bits")
            else:
                alert = check_entropy_alert(H, self.baseline_entropy[service], service)
                if alert:
                    self.alerts.append(alert)
                else:
                    # Slowly update baseline (exponential moving average)
                    self.baseline_entropy[service] = (
                        0.95 * self.baseline_entropy[service] + 0.05 * H
                    )

            # ── CUSUM check (per service-pair) ─────────────────
            for subject, count in counts.items():
                rate = count / WINDOW_SECONDS   # requests per second
                pair_key = f"{subject}→{service}"
                state = self.cusum_states.setdefault(pair_key, CUSUMState())
                cusum_val = update_cusum(state, rate)

                if cusum_val is not None:
                    msg = (f"Lateral movement / slow attack suspected: "
                           f"{subject} → {service} "
                           f"request rate anomaly (CUSUM={cusum_val:.2f})")
                    log.warning(f"ALERT: {msg}")
                    self.alerts.append(Alert(
                        timestamp=now,
                        alert_type="CUSUM_SPIKE",
                        service=service,
                        value=cusum_val,
                        threshold=state.h,
                        message=msg
                    ))

        # Reset window counters
        self.window_counts.clear()

    def run(self):
        """Tail the Keto log file and process events in real time."""
        log.info("Statistical Anomaly Detector started (no ML)")
        log.info("Methods: Shannon entropy + CUSUM")
        log.info(f"References:")
        log.info(f"  Chandola (2009): https://doi.org/10.1145/1541880.1541882")
        log.info(f"  Nychis  (2008): https://doi.org/10.1145/1452520.1452539")
        log.info(f"  Blazek  (2001): https://doi.org/10.1109/IWIAS.2001.935077")

        try:
            with open(LOG_PATH, "r") as f:
                f.seek(0, 2)   # seek to end (tail mode)
                last_tick = time.time()

                while True:
                    line = f.readline()
                    if line:
                        parsed = parse_keto_log_line(line)
                        if parsed:
                            subject, obj = parsed
                            self.ingest(subject, obj)

                    now = time.time()
                    if now - last_tick >= WINDOW_SECONDS:
                        self.tick()
                        last_tick = now
                    else:
                        time.sleep(0.05)

        except FileNotFoundError:
            log.error(f"Keto log not found at {LOG_PATH}. Is Keto running?")
            log.error("See: https://www.ory.sh/docs/keto/install")


# ── Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    detector = StatisticalDetector()
    detector.run()
