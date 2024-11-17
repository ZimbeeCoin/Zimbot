# tests/assistants/internal/test_factory.py

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from assistants.internal.factory import AssistantFactory
from assistants.internal.manager import AssistantManager
from core.integrations.openai.types import Assistant, Tool


@pytest.fixture
def mock_manager():
    return AsyncMock(spec=AssistantManager)


@pytest.fixture
def factory(mock_manager):
    return AssistantFactory(manager=mock_manager)


@pytest.mark.asyncio
async def test_create_market_analyst(factory, mock_manager):
    # Arrange
    name = "MarketGuru"
    market_type = "equities"
    data_sources = ["Bloomberg", "Reuters"]
    risk_profile = "high"

    expected_tools = [
        Tool(type="code_interpreter"),
        Tool(type="file_search"),
        Tool(
            type="function",
            function={
                "name": "analyze_market_data",
                "description": "Analyzes real-time market data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "timeframe": {"type": "string"},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["symbols", "timeframe"],
                },
            },
        ),
    ]

    mock_assistant = Assistant(
        id="assistant_123",
        name=name,
        instructions=f"""You are a specialized market analyst for {market_type} markets.
Data Sources: {', '.join(data_sources)}
Risk Profile: {risk_profile}

Your responsibilities:
1. Analyze market trends and patterns
2. Identify trading opportunities
3. Assess risks and provide risk management strategies
4. Monitor market indicators
5. Generate actionable insights

Always:
- Consider multiple timeframes
- Validate data sources
- Provide confidence levels
- Include risk disclaimers
""",
        tools=expected_tools,
        metadata={
            "type": "market_analyst",
            "market_type": market_type,
            "risk_profile": risk_profile,
        },
    )

    mock_manager.create_assistant.return_value = asyncio.Future()
    mock_manager.create_assistant.return_value.set_result(mock_assistant)

    # Act
    assistant = await factory.create_market_analyst(
        name=name,
        market_type=market_type,
        data_sources=data_sources,
        risk_profile=risk_profile,
    )

    # Assert
    mock_manager.create_assistant.assert_awaited_once_with(
        name=name,
        instructions=assistant.instructions,
        tools=expected_tools,
        metadata={
            "type": "market_analyst",
            "market_type": market_type,
            "risk_profile": risk_profile,
        },
    )
    assert assistant.id == "assistant_123"
    assert assistant.name == name
    assert assistant.tools == expected_tools
    assert assistant.metadata["type"] == "market_analyst"


# Additional tests for other factory methods...
