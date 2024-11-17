# src/core/integrations/openai/financial_analysis_client.py

import json
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import sentry_sdk
from core.utils.logger import get_logger
from pydantic import ValidationError

from .base_client import OpenAIBaseClient
from .types import Assistant, OpenAIError, StreamEvent

logger = get_logger(__name__)


class FinancialAnalysisClient(OpenAIBaseClient):
    """Specialized client for financial analysis using OpenAI APIs."""

    async def create_financial_assistant(
        self,
        name: str,
        specialization: str = "general",
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Assistant:
        """
        Create a specialized financial analysis assistant.

        Args:
            name (str): Name of the assistant.
            specialization (str): Type of financial analysis (e.g., 'technical', 'fundamental').
            tools (Optional[List[Dict[str, Any]]]): Additional tools beyond default financial tools.

        Returns:
            Assistant: The created financial assistant object.
        """
        default_tools = [
            {"type": "code_interpreter"},  # For financial calculations
            {"type": "file_search"},  # For market data analysis
        ]
        if tools:
            default_tools.extend(tools)

        instructions = f"""You are a specialized financial analyst focusing on {specialization} analysis.
Provide detailed, data-driven insights while maintaining compliance with financial regulations.
Always consider:
1. Risk assessment and management
2. Market conditions and trends
3. Historical data patterns
4. Economic indicators
5. Regulatory compliance

When making recommendations:
- Clearly state assumptions
- Provide confidence levels
- Include relevant disclaimers
- Cite data sources
"""

        try:
            assistant = await self.create_assistant(
                name=name,
                instructions=instructions,
                tools=default_tools,
                metadata={"specialization": specialization},
            )
            self.logger.info(
                f"[{assistant.id}] Created financial assistant: {assistant.name}"
            )
            return assistant
        except OpenAIError as oe:
            self.logger.error(f"Failed to create financial assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during financial assistant creation: {e}"
            )
            sentry_sdk.capture_exception(e)
            raise OpenAIError(f"Unexpected error: {e}") from e

    async def analyze_market_data(
        self,
        market_data: Dict[str, Any],
        analysis_type: str,
        stream: bool = False,
        cancel_event: Optional[asyncio.Event] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[StreamEvent]]:
        """
        Analyze market data with streaming support.

        Args:
            market_data (Dict[str, Any]): Dictionary containing market data.
            analysis_type (str): Type of analysis required.
            stream (bool): Whether to stream the analysis.
            cancel_event (Optional[asyncio.Event]): Event to signal cancellation of streaming.

        Returns:
            Union[Dict[str, Any], AsyncIterator[StreamEvent]]: Analysis result or stream of events.
        """
        messages = [
            {
                "role": "system",
                "content": "You are a quantitative financial analyst. Analyze the provided market data and provide insights.",
            },
            {
                "role": "user",
                "content": f"""Perform a {analysis_type} analysis on the following market data:
{json.dumps(market_data, indent=2)}

Focus on:
1. Key trends and patterns
2. Risk indicators
3. Actionable insights
4. Market opportunities
""",
            },
        ]

        response_format = {"type": "json_object"} if not stream else None

        try:
            response = await self.create_chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused analysis
                stream=stream,
                max_tokens=(
                    self.config.streaming.max_chunk_size
                    if self.config.streaming
                    else None
                ),
                cancel_event=cancel_event,
            )
            if not stream:
                self.logger.info("Market data analysis completed")
            else:
                self.logger.info("Started streaming market data analysis")
            return response
        except OpenAIError as oe:
            self.logger.error(f"Failed to analyze market data: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during market data analysis: {e}")
            sentry_sdk.capture_exception(e)
            raise OpenAIError(f"Unexpected error: {e}") from e

    async def generate_trading_strategy(
        self,
        market_conditions: Dict[str, Any],
        risk_profile: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a trading strategy based on market conditions and risk profile.

        Args:
            market_conditions (Dict[str, Any]): Current market conditions.
            risk_profile (str): Risk tolerance level.
            constraints (Optional[Dict[str, Any]]): Trading constraints and requirements.

        Returns:
            Dict[str, Any]: Generated trading strategy.
        """
        messages = [
            {
                "role": "system",
                "content": """You are a trading strategy expert. Generate detailed, practical trading
strategies based on market conditions while adhering to risk management principles.""",
            },
            {
                "role": "user",
                "content": f"""Generate a trading strategy with the following parameters:
Risk Profile: {risk_profile}
Market Conditions: {json.dumps(market_conditions, indent=2)}
Constraints: {json.dumps(constraints, indent=2) if constraints else 'None'}

Include:
1. Entry and exit criteria
2. Position sizing recommendations
3. Risk management rules
4. Performance monitoring metrics
""",
            },
        ]

        payload = {
            "model": self.config.default_model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 500,
        }

        try:
            response = await self._make_request(
                "POST", "chat/completions", data=payload
            )
            strategy = (
                response.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            self.logger.info("Trading strategy generated")
            return {"strategy": strategy}
        except ValidationError as ve:
            self.logger.error(f"Trading strategy validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(f"Trading strategy validation failed: {ve}") from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to generate trading strategy: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during trading strategy generation: {e}"
            )
            sentry_sdk.capture_exception(e)
            raise OpenAIError(f"Unexpected error: {e}") from e

    async def analyze_financial_document(
        self, file_id: str, analysis_focus: List[str]
    ) -> Assistant:
        """
        Analyze uploaded financial documents (reports, statements, etc.).

        Args:
            file_id (str): ID of the uploaded document.
            analysis_focus (List[str]): List of aspects to focus on.

        Returns:
            Assistant: Assistant configured to analyze the financial document.
        """
        payload = {
            "name": "Financial Document Analyst",
            "instructions": f"""Analyze the provided financial document focusing on: {', '.join(analysis_focus)}.
Provide detailed insights and highlight key findings.""",
            "model": self.config.default_model,
            "tools": [{"type": "file_search"}],
            "metadata": {"focus": analysis_focus},
            "file_ids": [file_id],
        }

        try:
            response = await self._make_request("POST", "assistants", data=payload)
            assistant = Assistant(**response)
            self.logger.info(
                f"[{assistant.id}] Created financial document assistant: {assistant.name}"
            )
            return assistant
        except ValidationError as ve:
            self.logger.error(f"Financial document assistant validation error: {ve}")
            sentry_sdk.capture_exception(ve)
            raise OpenAIError(
                f"Financial document assistant data validation failed: {ve}"
            ) from ve
        except OpenAIError as oe:
            self.logger.error(f"Failed to create financial document assistant: {oe}")
            sentry_sdk.capture_exception(oe)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error during financial document assistant creation: {e}"
            )
            sentry_sdk.capture_exception(e)
            raise OpenAIError(f"Unexpected error: {e}") from e

    # Additional financial analysis methods can be implemented similarly.
