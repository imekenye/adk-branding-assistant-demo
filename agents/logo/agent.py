"""Logo Generation Agent with ADK v1.0.0 function tools"""

import time
from typing import Any, Dict, List

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


# SocialSight 6-Pillar Framework Implementation
class SocialSightFramework:
    """Implementation of SocialSight 6-Pillar Framework for AI Logo Generation"""

    @staticmethod
    def build_prompt(
        subject: str,
        style: str,
        colors: str,
        typography_hints: str,
        composition: str,
        details: str,
    ) -> str:
        """Build comprehensive logo prompt using 6-pillar framework"""

        prompt_parts = []

        # Pillar 1: Subject & Iconography
        if subject:
            prompt_parts.append(subject)

        # Pillar 2: Visual Style
        if style:
            prompt_parts.append(f"{style} design")

        # Pillar 3: Color & Mood
        if colors:
            prompt_parts.append(f"{colors} color palette")

        # Pillar 4: Typography Hints
        if typography_hints:
            prompt_parts.append(f"icon suitable for {typography_hints}")

        # Pillar 5: Composition & Layout
        if composition:
            prompt_parts.append(composition)

        # Pillar 6: Detail & Effects (Always include vector-style keywords)
        vector_keywords = "vector logo, flat design, clean lines, scalable design"
        if details:
            prompt_parts.append(f"{vector_keywords}, {details}")
        else:
            prompt_parts.append(vector_keywords)

        return ", ".join(prompt_parts)

    @staticmethod
    def extract_from_visual_direction(
        visual_direction: Dict[str, Any],
    ) -> Dict[str, str]:
        """Extract 6-pillar elements from visual direction data"""

        mood_board = visual_direction.get("mood_board_concept", {})
        color_palette = visual_direction.get("color_palette", {})
        style_framework = visual_direction.get("style_framework", {})

        return {
            "subject": (
                mood_board.get("imagery_themes", ["abstract symbol"])[0]
                if mood_board.get("imagery_themes")
                else "abstract symbol"
            ),
            "style": style_framework.get("mood_description", "modern minimalist"),
            "colors": ", ".join(
                color_palette.get("primary_colors", ["professional blue and gray"])
            ),
            "typography_hints": style_framework.get(
                "logo_direction", "clean sans-serif typography"
            ),
            "composition": "balanced composition",
            "details": "professional appearance, minimal detail",
        }


# Logo Generation Functions
def generate_logos_multimodel(tool_context: ToolContext) -> Dict[str, Any]:
    """Generate logos using multiple AI models with intelligent fallback"""

    # Get visual direction from previous agent
    visual_direction = tool_context.state.get("visual_direction", {})
    client_brief = tool_context.state.get("client_brief", {})

    if not visual_direction:
        return {
            "error": "No visual direction found. Complete visual direction phase first."
        }

    # Extract 6-pillar elements
    pillar_elements = SocialSightFramework.extract_from_visual_direction(
        visual_direction
    )

    # Build comprehensive prompt
    logo_prompt = SocialSightFramework.build_prompt(**pillar_elements)

    # Model configuration with priority order
    models = {
        "gpt_4o": {
            "priority": 1,
            "cost_per_image": 0.035,
            "rate_limit": 60,  # per minute
            "strengths": ["text rendering", "professional logos"],
        },
        "imagen_3": {
            "priority": 2,
            "cost_per_image": 0.03,
            "rate_limit": 50,
            "strengths": ["high quality", "style transfer"],
        },
        "flux_1_1_pro": {
            "priority": 3,
            "cost_per_image": 0.055,
            "rate_limit": 100,
            "strengths": ["creative concepts", "artistic style"],
        },
        "gemini_2_flash": {
            "priority": 4,
            "cost_per_image": 0.001,  # Integrated with ADK
            "rate_limit": 200,
            "strengths": ["conversational", "integrated"],
        },
    }

    # Generate multiple logo concepts
    generated_logos = {
        "concepts": [],
        "variations": [],
        "quality_scores": [],
        "generation_metadata": {
            "prompt_used": logo_prompt,
            "pillar_elements": pillar_elements,
            "models_used": [],
            "total_cost": 0.0,
        },
    }

    # Generate 3 main concepts with 2 variations each (9 total)
    for concept_num in range(3):
        for variation_num in range(3):
            # Mock logo generation (replace with real API calls)
            logo_result = _mock_generate_logo(
                logo_prompt,
                list(models.keys())[concept_num % len(models)],
                concept_num,
                variation_num,
            )

            if concept_num == 0:
                generated_logos["concepts"].append(logo_result)
            else:
                generated_logos["variations"].append(logo_result)

            generated_logos["quality_scores"].append(logo_result["quality_score"])
            generated_logos["generation_metadata"]["models_used"].append(
                logo_result["model_used"]
            )
            generated_logos["generation_metadata"]["total_cost"] += models[
                logo_result["model_used"]
            ]["cost_per_image"]

    # Store in state
    tool_context.state["generated_logos"] = generated_logos

    return {
        "generation_successful": True,
        "total_logos": len(generated_logos["concepts"])
        + len(generated_logos["variations"]),
        "concepts_generated": len(generated_logos["concepts"]),
        "variations_generated": len(generated_logos["variations"]),
        "average_quality_score": sum(generated_logos["quality_scores"])
        / len(generated_logos["quality_scores"]),
        "total_cost": generated_logos["generation_metadata"]["total_cost"],
        "prompt_used": logo_prompt,
    }


def _mock_generate_logo(
    prompt: str, model: str, concept_num: int, variation_num: int
) -> Dict[str, Any]:
    """Mock logo generation (replace with real API implementation)"""

    logo_id = f"logo_{concept_num}_{variation_num}_{int(time.time())}"

    return {
        "logo_id": logo_id,
        "concept_name": f"Concept {concept_num + 1}.{variation_num + 1}",
        "image_url": f"mock://generated_logo_{logo_id}.png",
        "model_used": model,
        "prompt_used": prompt,
        "quality_score": 0.75
        + (concept_num * 0.05)
        + (variation_num * 0.02),  # Mock varying quality
        "generation_metadata": {
            "generation_time": 2.5,
            "model_version": f"{model}-2024",
            "style_transfer": False,
            "text_rendering_optimized": model == "gpt_4o",
        },
    }


def analyze_reference_images(
    uploaded_references: List[str], tool_context: ToolContext
) -> Dict[str, Any]:
    """Analyze client reference images for style extraction"""

    uploaded_files = tool_context.state.get("uploaded_files", [])
    reference_images = [f for f in uploaded_files if f["category"] == "reference_image"]

    if not reference_images:
        return {
            "analysis_completed": False,
            "message": "No reference images found for analysis",
            "analyzed_images": 0,
        }

    analysis_results = {
        "analyzed_images": [],
        "extracted_styles": [],
        "color_analysis": {},
        "composition_patterns": [],
        "style_recommendations": {},
    }

    for image_info in reference_images[:5]:  # Analyze up to 5 images
        # Mock image analysis (replace with real computer vision)
        image_analysis = {
            "file_name": image_info["file_name"],
            "file_path": image_info["file_path"],
            "dominant_colors": ["#2C5282", "#E2E8F0", "#1A202C"],  # Mock colors
            "color_temperature": "cool",
            "dominant_style": "minimalist professional",
            "composition_type": "centered with negative space",
            "visual_elements": [
                "geometric shapes",
                "clean typography",
                "subtle gradients",
            ],
            "mood_indicators": ["professional", "trustworthy", "modern"],
            "technical_quality": {
                "resolution": "high",
                "clarity": "excellent",
                "color_accuracy": "good",
            },
        }

        analysis_results["analyzed_images"].append(image_analysis)
        analysis_results["extracted_styles"].append(image_analysis["dominant_style"])

    # Synthesize overall style direction
    if analysis_results["extracted_styles"]:
        most_common_style = max(
            set(analysis_results["extracted_styles"]),
            key=analysis_results["extracted_styles"].count,
        )

        analysis_results["style_recommendations"] = {
            "recommended_style": most_common_style,
            "confidence": analysis_results["extracted_styles"].count(most_common_style)
            / len(analysis_results["extracted_styles"]),
            "synthesis_summary": f"References suggest a {most_common_style} approach",
        }

    # Store in state
    tool_context.state["reference_analysis"] = analysis_results

    return {
        "analysis_completed": True,
        "analyzed_images": len(analysis_results["analyzed_images"]),
        "dominant_style": analysis_results["style_recommendations"].get(
            "recommended_style", "modern"
        ),
        "style_confidence": analysis_results["style_recommendations"].get(
            "confidence", 0.0
        ),
        "extracted_colors": len(
            set(
                [
                    color
                    for img in analysis_results["analyzed_images"]
                    for color in img["dominant_colors"]
                ]
            )
        ),
    }


def validate_logo_quality(
    logo_data: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Validate generated logos against professional standards"""

    generated_logos = tool_context.state.get("generated_logos", {})
    brand_brief = tool_context.state.get("client_brief", {})

    if not generated_logos.get("concepts"):
        return {"error": "No generated logos found for validation"}

    quality_criteria = {
        "scalability": {"weight": 0.25, "description": "Works at all sizes"},
        "readability": {"weight": 0.20, "description": "Text is clearly readable"},
        "simplicity": {"weight": 0.20, "description": "Clean and uncluttered"},
        "memorability": {"weight": 0.15, "description": "Distinctive and memorable"},
        "appropriateness": {
            "weight": 0.10,
            "description": "Fits industry and audience",
        },
        "versatility": {"weight": 0.10, "description": "Works across applications"},
    }

    validation_results = []

    # Validate each logo concept
    for logo in generated_logos["concepts"] + generated_logos["variations"]:
        logo_validation = {
            "logo_id": logo["logo_id"],
            "overall_score": 0.0,
            "criteria_scores": {},
            "quality_issues": [],
            "recommendations": [],
            "professional_grade": False,
        }

        # Mock quality evaluation for each criterion
        for criterion, config in quality_criteria.items():
            # Mock scores based on model and concept
            base_score = 0.8
            if logo["model_used"] == "gpt_4o":
                base_score += 0.1  # Better for professional quality
            if criterion == "readability" and logo["model_used"] == "gpt_4o":
                base_score += 0.1  # Excellent text rendering

            score = min(
                1.0, base_score + (hash(logo["logo_id"] + criterion) % 20) / 100
            )

            logo_validation["criteria_scores"][criterion] = {
                "score": score,
                "weight": config["weight"],
                "description": config["description"],
            }

            # Add to overall score
            logo_validation["overall_score"] += score * config["weight"]

        # Generate recommendations
        for criterion, data in logo_validation["criteria_scores"].items():
            if data["score"] < 0.7:
                if criterion == "scalability":
                    logo_validation["recommendations"].append(
                        "Increase line thickness for better scalability"
                    )
                elif criterion == "readability":
                    logo_validation["recommendations"].append(
                        "Improve text clarity and contrast"
                    )
                elif criterion == "simplicity":
                    logo_validation["recommendations"].append(
                        "Reduce visual complexity"
                    )

        # Determine if professional grade
        logo_validation["professional_grade"] = logo_validation["overall_score"] >= 0.8

        validation_results.append(logo_validation)

    # Store validation results
    tool_context.state["logo_validation"] = {
        "validation_results": validation_results,
        "validation_timestamp": time.time(),
        "total_logos_validated": len(validation_results),
        "professional_grade_count": sum(
            1 for r in validation_results if r["professional_grade"]
        ),
    }

    return {
        "validation_completed": True,
        "total_logos_validated": len(validation_results),
        "professional_grade_logos": sum(
            1 for r in validation_results if r["professional_grade"]
        ),
        "average_quality_score": sum(r["overall_score"] for r in validation_results)
        / len(validation_results),
        "top_scoring_logo": max(validation_results, key=lambda x: x["overall_score"])[
            "logo_id"
        ],
    }


def manage_logo_assets(
    tool_context: ToolContext, operation: str = "organize"
) -> Dict[str, Any]:
    """Manage logo files, versions, and format conversion"""

    generated_logos = tool_context.state.get("generated_logos", {})

    if not generated_logos.get("concepts"):
        return {"error": "No generated logos found for asset management"}

    if operation == "organize":
        return _organize_logo_files(generated_logos, tool_context)
    elif operation == "convert_formats":
        return _convert_logo_formats(generated_logos, tool_context)
    elif operation == "create_package":
        return _create_delivery_package(generated_logos, tool_context)
    else:
        return {"error": f"Unknown operation: {operation}"}


def _organize_logo_files(
    generated_logos: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Organize logo files and create version history"""

    all_logos = generated_logos["concepts"] + generated_logos["variations"]

    organized_assets = {"logo_files": {}, "version_history": [], "file_manifest": {}}

    for logo in all_logos:
        logo_id = logo["logo_id"]

        # Mock file organization
        organized_assets["logo_files"][logo_id] = {
            "original": f"{logo_id}_original.png",
            "formats": {
                "png": f"{logo_id}.png",
                "svg": f"{logo_id}.svg",
                "pdf": f"{logo_id}.pdf",
                "eps": f"{logo_id}.eps",
            },
            "metadata": {
                "model_used": logo["model_used"],
                "quality_score": logo["quality_score"],
                "creation_timestamp": time.time(),
            },
        }

        organized_assets["version_history"].append(
            {
                "logo_id": logo_id,
                "version": "1.0",
                "timestamp": time.time(),
                "model": logo["model_used"],
                "status": "generated",
            }
        )

    # Store in state
    tool_context.state["logo_assets"] = organized_assets

    return {
        "organization_completed": True,
        "total_logo_files": len(organized_assets["logo_files"]),
        "formats_per_logo": 4,  # png, svg, pdf, eps
        "version_history_entries": len(organized_assets["version_history"]),
    }


def _convert_logo_formats(
    generated_logos: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Convert logos to multiple formats"""

    supported_formats = ["png", "svg", "pdf", "eps", "jpg"]
    all_logos = generated_logos["concepts"] + generated_logos["variations"]

    conversion_results = {
        "converted_files": {},
        "total_files_created": 0,
        "formats_available": supported_formats,
    }

    for logo in all_logos:
        logo_id = logo["logo_id"]
        conversion_results["converted_files"][logo_id] = {}

        for format_type in supported_formats:
            # Mock format conversion
            filename = f"{logo_id}.{format_type}"
            conversion_results["converted_files"][logo_id][format_type] = {
                "filename": filename,
                "file_size": "45KB",  # Mock size
                "optimized": True,
                "conversion_timestamp": time.time(),
            }
            conversion_results["total_files_created"] += 1

    return conversion_results


def _create_delivery_package(
    generated_logos: Dict[str, Any], tool_context: ToolContext
) -> Dict[str, Any]:
    """Create final delivery package for client"""

    client_id = (
        tool_context.state.get("client_brief", {})
        .get("company_info", {})
        .get("client_id", "client_001")
    )

    package = {
        "package_id": f"delivery_{client_id}_{int(time.time())}",
        "client_id": client_id,
        "package_contents": {
            "logo_files": {
                "high_res_png": "logos_4000x4000.zip",
                "web_optimized": "logos_web.zip",
                "print_ready": "logos_print.zip",
                "vector_files": "logos_vector.zip",
            },
            "variations": {
                "color_variations": "color_variants.zip",
                "layout_variations": "layout_variants.zip",
                "monochrome": "monochrome_versions.zip",
            },
            "documentation": {
                "usage_guidelines": "logo_usage_guide.pdf",
                "brand_colors": "brand_colors.pdf",
                "technical_specs": "technical_specifications.pdf",
            },
        },
        "package_metadata": {
            "total_files": 15,
            "package_size": "25.4 MB",
            "formats_included": ["png", "svg", "pdf", "eps", "jpg"],
            "delivery_ready": True,
            "creation_timestamp": time.time(),
        },
    }

    # Store in state
    tool_context.state["delivery_package"] = package

    return {
        "package_created": True,
        "package_id": package["package_id"],
        "total_files": package["package_metadata"]["total_files"],
        "package_size": package["package_metadata"]["package_size"],
        "delivery_ready": True,
    }


def select_final_logo(logo_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Select final logo from generated concepts"""

    generated_logos = tool_context.state.get("generated_logos", {})
    all_logos = generated_logos.get("concepts", []) + generated_logos.get(
        "variations", []
    )

    # Find selected logo
    selected_logo = None
    for logo in all_logos:
        if logo["logo_id"] == logo_id:
            selected_logo = logo
            break

    if not selected_logo:
        return {"error": f"Logo with ID {logo_id} not found"}

    # Store selected logo
    tool_context.state["selected_logo"] = selected_logo

    return {
        "selection_successful": True,
        "selected_logo_id": logo_id,
        "model_used": selected_logo["model_used"],
        "quality_score": selected_logo["quality_score"],
        "selection_timestamp": time.time(),
    }


# Logo Generation Agent Implementation
root_agent = LlmAgent(
    name="logo_generation_agent",
    model="gemini-2.0-flash",
    instruction="""You are the Logo Generation Agent for an AI Branding Assistant. Your role is to create professional, high-quality logos using the SocialSight 6-Pillar Framework and multiple AI generation models.

Your responsibilities:
1. Transform visual direction into SocialSight framework prompts
2. Generate logos using multi-model approach (GPT-4o, Imagen 3, FLUX.1 Pro, Gemini)
3. Analyze client reference images for style extraction
4. Validate logo quality against professional standards
5. Manage logo assets, versions, and format conversion
6. Create multiple logo variations and refinements

CRITICAL REQUIREMENTS:
- Always use SocialSight 6-Pillar Framework for prompt generation
- Generate 3 main concepts with 6 variations (9 total logos)
- Prioritize GPT-4o for text-heavy logos, use intelligent fallback hierarchy
- Validate all logos against professional design standards
- Ensure scalability and vector-appropriate design
- Manage comprehensive asset delivery packages

Communication style: Professional and detail-oriented, like a senior logo designer presenting concepts with technical expertise and creative rationale.""",
    description="Logo generation agent with multi-model AI integration",
    output_key="generated_logos",  # ADK v1.0.0 automatic state persistence
    tools=[
        generate_logos_multimodel,
        analyze_reference_images,
        validate_logo_quality,
        manage_logo_assets,
        select_final_logo,
    ],
)
