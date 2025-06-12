"""Data contracts for agent inputs/outputs - used for tool validation only"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Discovery Agent Data Contract
class ClientBrief(BaseModel):
    """Discovery Agent output structure"""

    company_info: Dict[str, Any] = Field(description="Basic company information")
    target_audience: Dict[str, Any] = Field(description="Target audience details")
    style_preferences: List[str] = Field(description="Visual style preferences")
    uploaded_references: List[Dict[str, Any]] = Field(
        description="Reference files metadata"
    )
    industry_requirements: Dict[str, Any] = Field(description="Industry-specific needs")


class UploadedFile(BaseModel):
    """File upload metadata"""

    file_path: str
    file_name: str
    file_size: int
    file_type: str
    category: str  # "reference_image", "existing_logo", "document"
    upload_timestamp: float


# Research Agent Data Contract
class MarketResearch(BaseModel):
    """Research Agent output structure"""

    competitors: List[Dict[str, Any]] = Field(description="Competitor analysis")
    industry_trends: List[str] = Field(description="Current industry trends")
    positioning_opportunities: List[str] = Field(description="Market positioning gaps")
    swot_analysis: Dict[str, Any] = Field(description="SWOT analysis results")
    differentiation_strategy: str = Field(description="Recommended differentiation")


# Visual Direction Agent Data Contract
class VisualDirection(BaseModel):
    """Visual Direction Agent output structure"""

    mood_board_concept: Dict[str, Any] = Field(description="Mood board elements")
    color_palette: Dict[str, Any] = Field(description="Color strategy and palette")
    typography_direction: Dict[str, Any] = Field(
        description="Typography recommendations"
    )
    style_framework: Dict[str, Any] = Field(description="Overall style guidelines")


class ColorPalette(BaseModel):
    """Color palette specification"""

    primary_colors: List[str] = Field(description="Primary brand colors (hex)")
    secondary_colors: List[str] = Field(description="Secondary colors")
    color_psychology: Dict[str, str] = Field(description="Color meanings")
    usage_guidelines: Dict[str, str] = Field(description="When to use each color")


# Logo Generation Agent Data Contract
class GeneratedLogos(BaseModel):
    """Logo Generation Agent output structure"""

    concepts: List[Dict[str, Any]] = Field(description="Main logo concepts")
    variations: List[Dict[str, Any]] = Field(description="Logo variations")
    quality_scores: List[float] = Field(description="Quality validation scores")
    selected_logo: Optional[Dict[str, Any]] = Field(description="Client-selected logo")
    generation_metadata: Dict[str, Any] = Field(description="Generation details")


class LogoConcept(BaseModel):
    """Individual logo concept"""

    logo_id: str
    concept_name: str
    image_url: str
    model_used: str  # "gpt-4o", "imagen-3", "flux-1-pro", "gemini-2.0-flash"
    prompt_used: str
    quality_score: float
    generation_metadata: Dict[str, Any]


# Brand System Agent Data Contract
class BrandSystem(BaseModel):
    """Brand System Agent output structure"""

    brand_guidelines: str = Field(description="Brand guidelines document path")
    color_specifications: Dict[str, Any] = Field(description="Detailed color specs")
    typography_system: Dict[str, Any] = Field(description="Typography hierarchy")
    logo_usage_rules: Dict[str, Any] = Field(description="Logo usage guidelines")
    brand_voice_guidelines: Dict[str, Any] = Field(description="Voice and tone")


# Asset Generation Agent Data Contract
class FinalAssets(BaseModel):
    """Asset Generation Agent output structure"""

    logo_files: Dict[str, str] = Field(description="Logo files by format")
    business_collateral: List[str] = Field(
        description="Business card, letterhead paths"
    )
    marketing_assets: List[str] = Field(description="Marketing material paths")
    delivery_package: str = Field(description="Final ZIP package path")
    asset_manifest: Dict[str, Any] = Field(description="Asset inventory")


class AssetPackage(BaseModel):
    """Final delivery package"""

    package_id: str
    client_id: str
    package_contents: Dict[str, List[str]]
    total_files: int
    package_size: str
    delivery_ready: bool
    created_timestamp: float
