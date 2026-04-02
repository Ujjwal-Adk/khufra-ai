"""
Khufra Trading System - AI Advisor (Optional)
Claude AI as an optional confirmation/analysis layer.
Can be toggled on/off via config.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIAdvisor:
    """
    Optional Claude AI confirmation layer.
    When enabled, asks Claude to review high-confidence trades
    before execution as an additional sanity check.
    """

    def __init__(self, config):
        self.config = config
        self.enabled = config.ai_advisor.enabled
        self.client = None

    async def start(self):
        """Initialize Anthropic client if enabled."""
        if not self.enabled:
            logger.info("AI Advisor: disabled")
            return

        if not self.config.secrets.anthropic_api_key:
            logger.warning("AI Advisor: enabled but no API key — disabling")
            self.enabled = False
            return

        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.secrets.anthropic_api_key
            )
            logger.info(f"AI Advisor initialized (model: {self.config.ai_advisor.model})")
        except ImportError:
            logger.warning("anthropic package not installed — AI Advisor disabled")
            self.enabled = False

    async def review_trade(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        regime: str,
        confidence_score: int,
        score_breakdown: dict,
        behavioral_pattern: str = "",
        market_context: str = "",
    ) -> dict:
        """
        Ask Claude to review a potential trade.
        Returns: {'approved': bool, 'reasoning': str, 'adjustments': dict}
        """
        if not self.enabled or not self.client:
            return {'approved': True, 'reasoning': 'AI advisor disabled', 'adjustments': {}}

        if confidence_score < self.config.ai_advisor.confirm_above_score:
            return {'approved': True, 'reasoning': 'Below AI review threshold', 'adjustments': {}}

        prompt = (
            f"You are Khufra, a crypto trading system advisor. Review this trade:\n\n"
            f"Direction: {direction.upper()}\n"
            f"Entry: ${entry_price:.2f}\n"
            f"Stop Loss: ${stop_loss:.2f}\n"
            f"Take Profit: ${take_profit:.2f}\n"
            f"Risk/Reward: {abs(take_profit - entry_price) / abs(entry_price - stop_loss):.2f}\n"
            f"Regime: {regime}\n"
            f"Confidence: {confidence_score}/100\n"
            f"Score Breakdown: {score_breakdown}\n"
            f"Behavioral Pattern: {behavioral_pattern or 'None'}\n"
            f"Context: {market_context or 'N/A'}\n\n"
            f"Respond with JSON: {{\"approved\": true/false, \"reasoning\": \"...\", "
            f"\"risk_concerns\": [\"...\"], \"adjustments\": {{\"stop_loss\": null, \"take_profit\": null}}}}"
        )

        try:
            response = await self.client.messages.create(
                model=self.config.ai_advisor.model,
                max_tokens=self.config.ai_advisor.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            logger.info(f"AI Advisor response: {text[:200]}")

            import json
            try:
                result = json.loads(text)
                return {
                    'approved': result.get('approved', True),
                    'reasoning': result.get('reasoning', ''),
                    'adjustments': result.get('adjustments', {}),
                }
            except json.JSONDecodeError:
                return {'approved': True, 'reasoning': 'Failed to parse AI response', 'adjustments': {}}

        except Exception as e:
            logger.error(f"AI Advisor error: {e}")
            return {'approved': True, 'reasoning': f'AI error: {e}', 'adjustments': {}}
