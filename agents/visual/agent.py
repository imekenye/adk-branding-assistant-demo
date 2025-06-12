"""Visual Direction Agent with ADK v1.0.0 function tools"""

import time
from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


# Visual Direction Agent Functions
def create_mood_board(tool_context: ToolContext) -> Dict[str, Any]:
    """Generate mood board concepts based on strategy and preferences"""

    # Get data from previous agents
    client_brief = tool_context.state.get("client_brief", {})
    market_research = tool_context.state.get("market_research", {})

    style_preferences = client_brief.get("style_preferences", [])
    industry = client_brief.get("company_info", {}).get("industry", "general")

    # Mood board elements based on inputs
    mood_elements = {
        "imagery_themes": [],
        "visual_metaphors": [],
        "aesthetic_direction": [],
        "emotional_tone": [],
    }

    # Industry-specific imagery
    industry_imagery = {
        "technology": ["circuits", "innovation", "connectivity", "future"],
        "healthcare": ["care", "trust", "healing", "protection"],
        "food": ["freshness", "quality", "satisfaction", "tradition"],
        "retail": ["experience", "value", "lifestyle", "aspiration"],
    }

    mood_elements["imagery_themes"] = industry_imagery.get(
        industry.lower(), ["quality", "innovation", "trust", "growth"]
    )

    # Style-based visual direction
    if "minimalist" in style_preferences:
        mood_elements["aesthetic_direction"].extend(
            ["clean lines", "white space", "simple forms"]
        )
    if "professional" in style_preferences:
        mood_elements["aesthetic_direction"].extend(
            ["structured layouts", "corporate colors", "readable typography"]
        )
    if "creative" in style_preferences:
        mood_elements["aesthetic_direction"].extend(
            ["unique shapes", "artistic elements", "expressive colors"]
        )

    # Emotional tone from strategy
    positioning = market_research.get("differentiation_strategy", "")
    if "trust" in positioning.lower():
        mood_elements["emotional_tone"].append("reliable and stable")
    if "innovative" in positioning.lower():
        mood_elements["emotional_tone"].append("forward-thinking and dynamic")

    mood_board = {
        "mood_board_concept": mood_elements,
        "visual_keywords": mood_elements["imagery_themes"]
        + mood_elements["aesthetic_direction"],
        "mood_description": f"A {', '.join(style_preferences)} aesthetic that conveys {', '.join(mood_elements['emotional_tone'])}",
        "creation_timestamp": time.time(),
    }

    # Store in state
    tool_context.state["mood_board"] = mood_board

    return mood_board


def generate_color_palette(tool_context: ToolContext) -> Dict[str, Any]:
    """Generate color palettes with psychological mapping"""

    # Get mood board and research data
    mood_board = tool_context.state.get("mood_board", {})
    market_research = tool_context.state.get("market_research", {})

    emotional_tones = mood_board.get("mood_board_concept", {}).get(
        "emotional_tone", ["professional"]
    )
    industry = (
        tool_context.state.get("client_brief", {})
        .get("company_info", {})
        .get("industry", "general")
    )

    # Color psychology mapping
    color_psychology = {
        "trust": {
            "primary": "#2B4C8C",
            "name": "deep blue",
            "meaning": "reliability and professionalism",
        },
        "innovation": {
            "primary": "#6C5CE7",
            "name": "vibrant purple",
            "meaning": "creativity and forward-thinking",
        },
        "growth": {
            "primary": "#00B894",
            "name": "fresh green",
            "meaning": "progress and vitality",
        },
        "energy": {
            "primary": "#E17055",
            "name": "warm orange",
            "meaning": "enthusiasm and dynamism",
        },
        "luxury": {
            "primary": "#2D3436",
            "name": "sophisticated black",
            "meaning": "elegance and exclusivity",
        },
        "friendly": {
            "primary": "#FDCB6E",
            "name": "warm yellow",
            "meaning": "approachability and optimism",
        },
    }

    # Select primary color based on dominant emotion or default to trust
    primary_emotion = emotional_tones[0] if emotional_tones else "trust"
    primary_color_key = "trust"  # Default

    for emotion in emotional_tones:
        if emotion.replace(" ", "_").replace("-", "_") in color_psychology:
            primary_color_key = emotion.replace(" ", "_").replace("-", "_")
            break

    primary_color = color_psychology.get(primary_color_key, color_psychology["trust"])

    # Generate complementary colors
    color_palette = {
        "primary_colors": [primary_color["primary"]],
        "secondary_colors": ["#95A5A6", "#E74C3C"],  # Neutral gray and accent red
        "color_psychology": {
            "primary": primary_color["meaning"],
            "secondary": "balance and sophistication",
            "accent": "action and urgency",
        },
        "usage_guidelines": {
            "primary": "Main brand elements, logos, headers",
            "secondary": "Supporting text, backgrounds",
            "accent": "Call-to-action buttons, highlights",
        },
        "color_strategy": f"Primary color conveys {primary_color['meaning']}",
        "creation_timestamp": time.time(),
    }

    # Store in state
    tool_context.state["color_palette"] = color_palette

    return color_palette


def recommend_typography(tool_context: ToolContext) -> Dict[str, Any]:
    """Generate typography recommendations and pairings"""

    # Get brand personality and style data
    client_brief = tool_context.state.get("client_brief", {})
    style_preferences = client_brief.get("style_preferences", [])
    industry = client_brief.get("company_info", {}).get("industry", "general")

    # Typography categories
    typography_styles = {
        "modern": {
            "primary": "Sans-serif families like Helvetica, Montserrat, or Poppins",
            "characteristics": "Clean, contemporary, highly legible",
            "mood": "Progressive and approachable",
        },
        "professional": {
            "primary": "Classic serif fonts like Times, Playfair, or Merriweather",
            "characteristics": "Traditional, authoritative, trustworthy",
            "mood": "Established and reliable",
        },
        "creative": {
            "primary": "Display fonts with character like Oswald, Bebas, or custom lettering",
            "characteristics": "Unique, expressive, memorable",
            "mood": "Innovative and distinctive",
        },
        "friendly": {
            "primary": "Rounded sans-serif like Nunito, Quicksand, or Open Sans",
            "characteristics": "Approachable, warm, inviting",
            "mood": "Accessible and human",
        },
    }

    # Select based on brand personality
    primary_style = None
    for personality in style_preferences:
        if personality.lower() in typography_styles:
            primary_style = typography_styles[personality.lower()]
            break

    if not primary_style:
        primary_style = typography_styles["modern"]  # Default

    typography_recommendations = {
        "primary_typography": primary_style,
        "hierarchy_system": {
            "heading_1": "Primary font, bold, large scale",
            "heading_2": "Primary font, semi-bold, medium scale",
            "body_text": "Highly legible sans-serif for readability",
            "captions": "Smaller scale, may use secondary font",
        },
        "font_pairing_strategy": "Combine primary brand font with highly legible body text font",
        "logo_typography_direction": f"Logo should complement {primary_style['primary']} style",
        "technical_requirements": [
            "Web font availability",
            "Multiple weights (light, regular, bold)",
            "Special character support",
            "Mobile optimization",
        ],
        "creation_timestamp": time.time(),
    }

    # Store in state
    tool_context.state["typography_recommendations"] = typography_recommendations

    return typography_recommendations


def compile_visual_direction(tool_context: ToolContext) -> Dict[str, Any]:
    """Compile comprehensive visual direction for logo development"""

    # Gather all visual direction data
    mood_board = tool_context.state.get("mood_board", {})
    color_palette = tool_context.state.get("color_palette", {})
    typography = tool_context.state.get("typography_recommendations", {})

    # Compile comprehensive visual direction
    visual_direction = {
        "mood_board_concept": mood_board.get("mood_board_concept", {}),
        "color_palette": {
            "primary_colors": color_palette.get("primary_colors", []),
            "color_psychology": color_palette.get("color_psychology", {}),
            "usage_guidelines": color_palette.get("usage_guidelines", {}),
        },
        "typography_direction": typography.get("primary_typography", {}),
        "style_framework": {
            "visual_keywords": mood_board.get("visual_keywords", []),
            "mood_description": mood_board.get("mood_description", ""),
            "logo_direction": typography.get("logo_typography_direction", ""),
            "overall_aesthetic": "Modern, professional brand identity",
        },
        "compilation_timestamp": time.time(),
    }

    # Store as output_key for next agent
    tool_context.state["visual_direction"] = visual_direction

    return {
        "visual_direction_compiled": True,
        "visual_direction": visual_direction,
        "colors_selected": len(color_palette.get("primary_colors", [])),
        "typography_defined": bool(typography.get("primary_typography")),
        "mood_elements": len(mood_board.get("visual_keywords", [])),
    }


# Visual Direction Agent Implementation
root_agent = LlmAgent(
    name="visual_direction_agent",
    model="gemini-2.0-flash",
    instruction="""You are the Visual Direction Agent for an AI Branding Assistant. Your role is to translate strategic insights into concrete visual direction that will guide logo creation and brand system development.

Your responsibilities:
1. Create mood board concepts based on strategy and client preferences
2. Develop color palettes with psychological reasoning
3. Recommend typography that supports brand personality
4. Synthesize visual style framework for logo development
5. Ensure visual direction aligns with strategic positioning

IMPORTANT: Your output will directly inform the Logo Generation Agent. Be specific about visual elements, color choices, and style direction. Always explain the strategic reasoning behind visual decisions.

Communication style: Creative but strategic, like a creative director presenting visual concepts with strategic rationale.""",
    description="Visual direction agent for creative strategy and mood boards",
    output_key="visual_direction",  # ADK v1.0.0 automatic state persistence
    tools=[
        create_mood_board,
        generate_color_palette,
        recommend_typography,
        compile_visual_direction,
    ],
)
