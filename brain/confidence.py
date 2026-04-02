"""
Khufra Trading System - Confidence Scoring Engine
Multi-factor composite scoring (0-100) for trade decisions.
V2 Spec Section 5.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


class TradeAction:
    NO_TRADE = "no_trade"
    WATCHLIST = "watchlist"
    TRADE_CONSERVATIVE = "trade_conservative"
    TRADE_STANDARD = "trade_standard"
    TRADE_HIGH_CONVICTION = "trade_high_conviction"


@dataclass
class ConfidenceResult:
    """Result of confidence scoring."""
    total_score: int
    action: str
    position_risk_pct: float  # effective risk % of equity
    breakdown: dict = field(default_factory=dict)

    @property
    def should_trade(self) -> bool:
        return self.action in (
            TradeAction.TRADE_CONSERVATIVE,
            TradeAction.TRADE_STANDARD,
            TradeAction.TRADE_HIGH_CONVICTION,
        )


class ConfidenceEngine:
    """
    Multi-factor confidence scorer.
    Each signal factor contributes points to a composite 0-100 score.
    Only trades above threshold are executed.
    """

    def __init__(self, config):
        self.config = config
        self.weights = config.confidence.weights
        self.min_score = config.confidence.min_score_to_trade
        self.min_score_watch = config.confidence.min_score_watch_zone
        self.base_risk = config.risk.base_risk_pct

    def score(
        self,
        regime_aligned: bool,
        regime_clear: bool,
        behavioral_pattern: Optional[str] = None,
        behavioral_strength: float = 0.0,
        whale_confirmed: Optional[bool] = None,
        order_book_support: float = 0.0,
        funding_favorable: float = 0.0,
        volume_confirmed: bool = False,
        is_watch_zone: bool = False,
        regime: str = None,
    ) -> ConfidenceResult:
        """
        Calculate composite confidence score.

        Args:
            regime_aligned: Strategy matches current regime
            regime_clear: Regime is clearly identified (not transition)
            behavioral_pattern: Detected pattern name or None
            behavioral_strength: 0-1 strength of behavioral pattern
            whale_confirmed: True/False/None (None = no data, use neutral)
            order_book_support: 0-1 how much order book supports the trade
            funding_favorable: 0-1 how favorable the funding rate is
            volume_confirmed: Whether volume supports the move
            is_watch_zone: Whether we're in a watch-only kill zone
            regime: Current regime string for position sizing

        Returns:
            ConfidenceResult with score, action, and position size
        """
        breakdown = {}

        # Factor 1: Regime Alignment (max 20)
        max_regime = self.weights.regime_alignment
        if regime_aligned:
            breakdown['regime'] = max_regime if regime_clear else max_regime // 2
        else:
            breakdown['regime'] = 0

        # Factor 2: Behavioral Pattern (max 25)
        max_behavioral = self.weights.behavioral_pattern
        if behavioral_pattern:
            if behavioral_strength >= 0.7:
                breakdown['behavioral'] = max_behavioral  # Textbook pattern
            elif behavioral_strength >= 0.4:
                breakdown['behavioral'] = int(max_behavioral * 0.6)  # Partial pattern
            else:
                breakdown['behavioral'] = int(max_behavioral * 0.3)
        else:
            breakdown['behavioral'] = 0

        # Factor 3: Whale/On-Chain (max 20)
        max_whale = self.weights.whale_onchain
        if whale_confirmed is True:
            breakdown['whale'] = max_whale
        elif whale_confirmed is False:
            breakdown['whale'] = 0  # Whale data contradicts
        else:
            # No whale data available — use neutral score
            breakdown['whale'] = max_whale // 2

        # Factor 4: Order Book Support (max 15)
        max_ob = self.weights.order_book
        breakdown['order_book'] = int(max_ob * min(1.0, order_book_support))

        # Factor 5: Funding Rate (max 10)
        max_fr = self.weights.funding_rate
        breakdown['funding_rate'] = int(max_fr * min(1.0, funding_favorable))

        # Factor 6: Volume Confirmation (max 10)
        max_vol = self.weights.volume
        breakdown['volume'] = max_vol if volume_confirmed else 0

        # Calculate total
        total = sum(breakdown.values())
        total = min(100, max(0, total))

        # Determine action and position size
        effective_min = self.min_score_watch if is_watch_zone else self.min_score

        if total < 50:
            action = TradeAction.NO_TRADE
            risk_pct = 0.0
        elif total < effective_min:
            action = TradeAction.WATCHLIST
            risk_pct = 0.0
        elif total < 75:
            action = TradeAction.TRADE_CONSERVATIVE
            risk_pct = self._calculate_position_risk(total, regime, "conservative")
        elif total < 85:
            action = TradeAction.TRADE_STANDARD
            risk_pct = self._calculate_position_risk(total, regime, "standard")
        else:
            action = TradeAction.TRADE_HIGH_CONVICTION
            risk_pct = self._calculate_position_risk(total, regime, "high_conviction")

        result = ConfidenceResult(
            total_score=total,
            action=action,
            position_risk_pct=risk_pct,
            breakdown=breakdown,
        )

        logger.info(
            f"CONFIDENCE: {total}/100 -> {action} | "
            f"Risk: {risk_pct:.2%} | {breakdown}"
        )

        return result

    def _calculate_position_risk(
        self, score: int, regime: str, tier: str
    ) -> float:
        """
        Calculate effective position risk %.
        position_risk = base_risk * confidence_multiplier * regime_multiplier
        """
        confidence_mult = self.config.risk.confidence_multipliers.get(tier, 1.0)
        regime_mult = self.config.risk.regime_multipliers.get(regime or 'transition', 0.5)

        effective_risk = self.base_risk * confidence_mult * regime_mult

        # Never exceed max risk
        max_risk = self.config.risk.max_risk_pct
        return min(effective_risk, max_risk)
