"""Discovery Agent with ADK v1.0.0 function tools"""

import mimetypes
import time
from pathlib import Path
from typing import Any, Dict, List

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from PIL import Image


# Modern Function Tools
def upload_and_process_file(
    file_path: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Real file upload processing with PIL image analysis"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        # Enhanced file categorization
        file_ext = file_path.suffix.lower()
        mime_type = mimetypes.guess_type(str(file_path))[0]

        category_map = {
            (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"): "reference_image",
            (".svg", ".ai", ".eps"): "existing_logo",
            (".pdf",): "document",
            (".doc", ".docx", ".txt", ".md"): "text_document",
            (".sketch", ".fig", ".xd"): "design_file",
        }

        category = "other"
        for extensions, cat in category_map.items():
            if file_ext in extensions:
                category = cat
                break

        # Basic image analysis for reference images
        image_analysis = {}
        if category == "reference_image":
            try:
                with Image.open(file_path) as img:
                    # Get image properties
                    width, height = img.size
                    image_analysis = {
                        "dimensions": {"width": width, "height": height},
                        "aspect_ratio": round(width / height, 2),
                        "orientation": (
                            "landscape"
                            if width > height
                            else "portrait" if height > width else "square"
                        ),
                        "format": img.format,
                        "mode": img.mode,
                    }

                    # Color analysis for RGB images
                    if img.mode in ("RGB", "RGBA"):
                        img_rgb = img.convert("RGB")
                        # Get dominant colors (simplified)
                        colors = img_rgb.getcolors(maxcolors=256 * 256 * 256)
                        if colors:
                            # Get top 3 colors by frequency
                            top_colors = sorted(
                                colors, key=lambda x: x[0], reverse=True
                            )[:3]
                            image_analysis["dominant_colors"] = [
                                f"#{r:02x}{g:02x}{b:02x}"
                                for count, (r, g, b) in top_colors
                            ]

                            # Determine color temperature
                            avg_color = [
                                sum(comp) / len(top_colors)
                                for comp in zip(*[color for _, color in top_colors])
                            ]
                            r, g, b = avg_color
                            image_analysis["color_temperature"] = (
                                "warm" if r > b else "cool" if b > r else "neutral"
                            )

            except Exception as e:
                image_analysis["error"] = f"Image analysis failed: {str(e)}"

        # Create comprehensive file metadata
        file_info = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": file_ext,
            "mime_type": mime_type,
            "category": category,
            "upload_timestamp": time.time(),
            "image_analysis": image_analysis,
            "project_id": tool_context.state.get("project_id"),
        }

        # Store in session state
        tool_context.state.setdefault("uploaded_files", []).append(file_info)

        return {
            "success": True,
            "file_info": file_info,
            "total_files": len(tool_context.state["uploaded_files"]),
            "category": category,
            "has_image_analysis": bool(image_analysis),
        }

    except Exception as e:
        return {"success": False, "error": f"File processing failed: {str(e)}"}


def generate_industry_questionnaire(
    industry: str, tool_context: ToolContext, company_size: str = "startup"
) -> Dict[str, Any]:
    """Dynamic questionnaire generation based on industry and company size"""

    # Enhanced base questions with priority scoring
    base_questions = [
        {
            "question": "What is your company name and core business?",
            "priority": "high",
            "type": "text",
        },
        {
            "question": "Who is your primary target audience?",
            "priority": "high",
            "type": "text",
        },
        {
            "question": "What are your company's core values and mission?",
            "priority": "high",
            "type": "text",
        },
        {
            "question": "How do you want customers to feel about your brand?",
            "priority": "high",
            "type": "emotion",
        },
        {
            "question": "What differentiates you from competitors?",
            "priority": "high",
            "type": "positioning",
        },
    ]

    # Industry-specific questions with enhanced targeting
    industry_questions = {
        "technology": [
            {
                "question": "What type of technology solution do you provide?",
                "priority": "high",
                "type": "product",
            },
            {
                "question": "Is your audience B2B, B2C, or both?",
                "priority": "medium",
                "type": "targeting",
            },
            {
                "question": "Do you prefer modern/futuristic or approachable styling?",
                "priority": "medium",
                "type": "style",
            },
            {
                "question": "How technical is your target audience?",
                "priority": "medium",
                "type": "audience",
            },
        ],
        "healthcare": [
            {
                "question": "What healthcare services or products do you offer?",
                "priority": "high",
                "type": "product",
            },
            {
                "question": "Do you work directly with patients or other businesses?",
                "priority": "high",
                "type": "targeting",
            },
            {
                "question": "How important is conveying trust and professionalism?",
                "priority": "high",
                "type": "tone",
            },
            {
                "question": "Are there regulatory requirements for your branding?",
                "priority": "medium",
                "type": "compliance",
            },
        ],
        "food": [
            {
                "question": "What type of food/cuisine do you specialize in?",
                "priority": "high",
                "type": "product",
            },
            {
                "question": "Is your brand premium, casual, or fast-casual?",
                "priority": "high",
                "type": "positioning",
            },
            {
                "question": "Do you emphasize tradition, innovation, or health?",
                "priority": "medium",
                "type": "values",
            },
            {
                "question": "What's your restaurant/product format?",
                "priority": "medium",
                "type": "format",
            },
        ],
        "retail": [
            {
                "question": "What products or services do you sell?",
                "priority": "high",
                "type": "product",
            },
            {
                "question": "What's your target customer demographic?",
                "priority": "high",
                "type": "audience",
            },
            {
                "question": "Are you positioning as premium, value, or luxury?",
                "priority": "high",
                "type": "positioning",
            },
            {
                "question": "Do you sell online, in-store, or both?",
                "priority": "medium",
                "type": "channel",
            },
        ],
        "finance": [
            {
                "question": "What financial services do you provide?",
                "priority": "high",
                "type": "product",
            },
            {
                "question": "Who is your target customer (individuals, businesses, both)?",
                "priority": "high",
                "type": "targeting",
            },
            {
                "question": "How do you want to be perceived (trustworthy, innovative, accessible)?",
                "priority": "high",
                "type": "perception",
            },
            {
                "question": "Are there compliance requirements for your branding?",
                "priority": "medium",
                "type": "compliance",
            },
        ],
    }

    # Company size adjustments
    size_adjustments = {
        "startup": [
            "What's your primary growth goal for the next year?",
            "What's your budget range for brand development?",
        ],
        "small_business": [
            "How established is your current customer base?",
            "Are you looking to expand to new markets?",
        ],
        "enterprise": [
            "How does this rebrand fit into broader corporate strategy?",
            "Who are the key stakeholders in brand decisions?",
        ],
    }

    # Compile questionnaire
    questions = base_questions.copy()
    questions.extend(industry_questions.get(industry.lower(), []))

    if company_size.lower() in size_adjustments:
        size_questions = [
            {"question": q, "priority": "low", "type": "business"}
            for q in size_adjustments[company_size.lower()]
        ]
        questions.extend(size_questions)

    questionnaire = {
        "industry": industry,
        "company_size": company_size,
        "questions": questions,
        "total_questions": len(questions),
        "high_priority_count": len(
            [q for q in questions if q.get("priority") == "high"]
        ),
        "estimated_time": f"{len(questions) * 1.5:.0f} minutes",
        "completion_score": 0.0,
        "generated_timestamp": time.time(),
    }

    # Store in session state
    tool_context.state["discovery_questionnaire"] = questionnaire

    return questionnaire


def analyze_style_preferences(
    style_inputs: List[str],
    tool_context: ToolContext,
    reference_images: List[str] = None,
) -> Dict[str, Any]:
    """Enhanced style preference analysis with reference image integration"""

    # Enhanced style categories with emotional mapping
    style_categories = {
        "minimalist": {
            "keywords": [
                "clean",
                "simple",
                "modern",
                "uncluttered",
                "minimal",
                "sleek",
            ],
            "emotions": ["calm", "focused", "professional"],
            "colors": ["whites", "grays", "monochrome"],
            "typography": ["sans-serif", "geometric"],
        },
        "vintage": {
            "keywords": [
                "retro",
                "classic",
                "traditional",
                "aged",
                "nostalgic",
                "heritage",
            ],
            "emotions": ["nostalgic", "authentic", "timeless"],
            "colors": ["earth tones", "muted", "sepia"],
            "typography": ["serif", "script", "decorative"],
        },
        "playful": {
            "keywords": [
                "fun",
                "colorful",
                "friendly",
                "approachable",
                "whimsical",
                "energetic",
            ],
            "emotions": ["joyful", "energetic", "friendly"],
            "colors": ["bright", "vibrant", "rainbow"],
            "typography": ["rounded", "hand-drawn", "casual"],
        },
        "professional": {
            "keywords": [
                "corporate",
                "serious",
                "trustworthy",
                "formal",
                "established",
                "reliable",
            ],
            "emotions": ["confident", "trustworthy", "stable"],
            "colors": ["blues", "grays", "conservative"],
            "typography": ["serif", "clean sans-serif"],
        },
        "creative": {
            "keywords": [
                "artistic",
                "unique",
                "innovative",
                "expressive",
                "bold",
                "experimental",
            ],
            "emotions": ["inspiring", "innovative", "bold"],
            "colors": ["bold", "unexpected", "artistic"],
            "typography": ["custom", "display", "experimental"],
        },
        "luxury": {
            "keywords": [
                "premium",
                "elegant",
                "sophisticated",
                "exclusive",
                "refined",
                "upscale",
            ],
            "emotions": ["prestigious", "exclusive", "refined"],
            "colors": ["black", "gold", "deep colors"],
            "typography": ["elegant serif", "refined sans-serif"],
        },
    }

    # Analyze text inputs
    identified_styles = []
    confidence_scores = {}

    for style_input in style_inputs:
        input_lower = style_input.lower()
        for style, attributes in style_categories.items():
            # Calculate confidence based on keyword matches
            matches = sum(
                1 for keyword in attributes["keywords"] if keyword in input_lower
            )
            confidence = matches / len(attributes["keywords"])

            if confidence > 0:
                identified_styles.append(style)
                confidence_scores[style] = confidence_scores.get(style, 0) + confidence

    # Analyze reference images if provided
    image_style_insights = {}
    if reference_images:
        uploaded_files = tool_context.state.get("uploaded_files", [])
        for file_info in uploaded_files:
            if file_info["category"] == "reference_image" and file_info.get(
                "image_analysis"
            ):
                analysis = file_info["image_analysis"]

                # Simple style inference from image properties
                insights = []
                if analysis.get("color_temperature") == "cool":
                    insights.append("professional")
                elif analysis.get("color_temperature") == "warm":
                    insights.append("friendly")

                if len(analysis.get("dominant_colors", [])) <= 2:
                    insights.append("minimalist")
                elif len(analysis.get("dominant_colors", [])) >= 4:
                    insights.append("vibrant")

                image_style_insights[file_info["file_name"]] = insights

    # Compile analysis results
    final_styles = list(set(identified_styles))
    sorted_styles = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)

    style_analysis = {
        "input_preferences": style_inputs,
        "identified_styles": final_styles,
        "confidence_ranking": sorted_styles,
        "primary_style": sorted_styles[0][0] if sorted_styles else "modern",
        "secondary_styles": [style for style, _ in sorted_styles[1:3]],
        "image_insights": image_style_insights,
        "style_attributes": {
            style: style_categories[style]
            for style in final_styles
            if style in style_categories
        },
        "analysis_timestamp": time.time(),
    }

    # Store in session state
    tool_context.state["style_analysis"] = style_analysis

    return style_analysis


def compile_comprehensive_brief(tool_context: ToolContext) -> Dict[str, Any]:
    """Compile comprehensive client brief with validation and completeness scoring"""

    # Gather all discovery data
    uploaded_files = tool_context.state.get("uploaded_files", [])
    questionnaire = tool_context.state.get("discovery_questionnaire", {})
    style_analysis = tool_context.state.get("style_analysis", {})

    # Categorize uploaded files
    file_categories = {}
    for file in uploaded_files:
        category = file["category"]
        file_categories.setdefault(category, []).append(file)

    # Extract image insights
    image_insights = {}
    for file in file_categories.get("reference_image", []):
        if file.get("image_analysis"):
            insights = file["image_analysis"]
            image_insights[file["file_name"]] = {
                "colors": insights.get("dominant_colors", []),
                "temperature": insights.get("color_temperature", "neutral"),
                "orientation": insights.get("orientation", "unknown"),
            }

    # Build comprehensive client brief
    client_brief = {
        "company_info": {
            "industry": questionnaire.get("industry", "general"),
            "company_size": questionnaire.get("company_size", "startup"),
            "questionnaire_completion": questionnaire.get("completion_score", 0.0),
        },
        "target_audience": {
            "primary_audience": "to be defined from questionnaire responses",
            "audience_type": "b2b_and_b2c",  # Would be extracted from actual responses
            "demographics": "to be refined",
        },
        "style_preferences": {
            "primary_style": style_analysis.get("primary_style", "modern"),
            "secondary_styles": style_analysis.get("secondary_styles", []),
            "confidence_scores": style_analysis.get("confidence_ranking", []),
            "style_attributes": style_analysis.get("style_attributes", {}),
        },
        "visual_references": {
            "uploaded_images": len(file_categories.get("reference_image", [])),
            "existing_logos": len(file_categories.get("existing_logo", [])),
            "documents": len(file_categories.get("document", [])),
            "image_insights": image_insights,
        },
        "industry_requirements": {
            "industry": questionnaire.get("industry", "general"),
            "compliance_considerations": [],  # Would be populated based on industry
            "industry_specific_needs": [],
        },
        "brief_metadata": {
            "compilation_timestamp": time.time(),
            "completeness_score": _calculate_completeness_score(
                questionnaire, style_analysis, uploaded_files
            ),
            "total_files": len(uploaded_files),
            "ready_for_research": True,  # Will be calculated based on completeness
        },
    }

    # Validate brief quality
    validation_results = _validate_brief_quality(client_brief)
    client_brief["validation"] = validation_results

    # Store as output for next agent
    tool_context.state["client_brief"] = client_brief

    return {
        "brief_compiled": True,
        "client_brief": client_brief,
        "completeness_score": client_brief["brief_metadata"]["completeness_score"],
        "validation_passed": validation_results["overall_quality"] >= 0.8,
        "recommendations": validation_results.get("recommendations", []),
    }


def _calculate_completeness_score(
    questionnaire: Dict, style_analysis: Dict, uploaded_files: List
) -> float:
    """Calculate completeness score for the discovery phase"""
    score_components = {
        "questionnaire": 0.4,  # 40% weight
        "style_analysis": 0.3,  # 30% weight
        "file_uploads": 0.3,  # 30% weight
    }

    total_score = 0.0

    # Questionnaire score
    if questionnaire:
        high_priority = questionnaire.get("high_priority_count", 0)
        total_questions = questionnaire.get("total_questions", 1)
        questionnaire_score = min(high_priority / max(total_questions * 0.6, 1), 1.0)
        total_score += questionnaire_score * score_components["questionnaire"]

    # Style analysis score
    if style_analysis:
        has_primary = 1.0 if style_analysis.get("primary_style") else 0.0
        has_confidence = 1.0 if style_analysis.get("confidence_ranking") else 0.0
        style_score = (has_primary + has_confidence) / 2
        total_score += style_score * score_components["style_analysis"]

    # File uploads score
    if uploaded_files:
        has_references = any(f["category"] == "reference_image" for f in uploaded_files)
        file_variety = len(set(f["category"] for f in uploaded_files))
        file_score = (0.7 if has_references else 0.3) + (min(file_variety / 3, 1) * 0.3)
        total_score += min(file_score, 1.0) * score_components["file_uploads"]

    return round(total_score, 2)


def _validate_brief_quality(client_brief: Dict) -> Dict[str, Any]:
    """Validate client brief quality and provide recommendations"""
    quality_checks = {
        "has_industry": bool(client_brief["company_info"].get("industry")),
        "has_style_preferences": bool(
            client_brief["style_preferences"].get("primary_style")
        ),
        "has_visual_references": client_brief["visual_references"]["uploaded_images"]
        > 0,
        "has_target_audience": bool(
            client_brief["target_audience"].get("primary_audience")
        ),
        "completeness_threshold": client_brief["brief_metadata"]["completeness_score"]
        >= 0.7,
    }

    passed_checks = sum(quality_checks.values())
    overall_quality = passed_checks / len(quality_checks)

    recommendations = []
    if not quality_checks["has_visual_references"]:
        recommendations.append(
            "Upload reference images to improve visual direction quality"
        )
    if not quality_checks["completeness_threshold"]:
        recommendations.append(
            "Complete more questionnaire items for better research insights"
        )
    if not quality_checks["has_style_preferences"]:
        recommendations.append("Provide more specific style preferences")

    return {
        "quality_checks": quality_checks,
        "overall_quality": overall_quality,
        "recommendations": recommendations,
        "ready_for_next_phase": overall_quality >= 0.8,
    }


# Enhanced Discovery Agent (ADK v1.2.1)
root_agent = LlmAgent(
    name="discovery_agent",
    model="gemini-2.0-flash",
    instruction="""You are the Discovery Agent for the AI Branding Assistant. Your role is to gather comprehensive client information and create detailed briefs for the research team.

🎯 PRIMARY OBJECTIVES:
- Process and analyze client file uploads (images, documents, references)
- Generate dynamic industry-specific questionnaires
- Analyze visual style preferences from text and images
- Compile comprehensive client briefs with quality validation

📁 FILE PROCESSING CAPABILITIES:
- Support for images (JPG, PNG, GIF, WebP), design files (SVG, AI, EPS), documents (PDF, DOC)
- Automated image analysis: dominant colors, color temperature, dimensions, orientation
- Reference categorization: inspiration vs existing assets vs competitive examples
- Visual insights extraction from uploaded references

📋 QUESTIONNAIRE INTELLIGENCE:
- Dynamic questions based on industry (technology, healthcare, food, retail, finance)
- Company size adjustments (startup, small business, enterprise)
- Priority-based questioning (high/medium/low priority items)
- Completion tracking and quality scoring

🎨 STYLE ANALYSIS FEATURES:
- Multi-dimensional style categorization (minimalist, vintage, playful, professional, creative, luxury)
- Confidence scoring based on keyword analysis
- Reference image style inference
- Primary/secondary style identification

✅ QUALITY ASSURANCE:
- Completeness scoring (questionnaire 40%, style 30%, uploads 30%)
- Brief validation with recommendations
- Ready-for-research threshold checking
- Comprehensive metadata tracking

Always be thorough but efficient. Guide clients through uploads and questionnaires systematically. Provide clear progress feedback and next steps.""",
    description="Enhanced discovery agent with real file processing and style analysis",
    output_key="client_brief",  # ADK v1.2.1 automatic state persistence
    # Modern function tools
    tools=[
        upload_and_process_file,
        generate_industry_questionnaire,
        analyze_style_preferences,
        compile_comprehensive_brief,
    ],
)
