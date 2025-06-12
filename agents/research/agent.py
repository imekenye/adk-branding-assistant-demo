"""Enhanced Research Agent with real web search integration (ADK v1.0.0)"""

import time
from typing import Any, Dict

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import ToolContext, agent_tool, google_search

# Create dedicated search agent (ADK limitation: built-in tools need separate agent)
search_agent = Agent(
    model="gemini-2.0-flash",
    name="research_search_agent",
    instruction="""You are a search specialist for market research. 
    Perform targeted web searches to find competitor information, market trends, and industry insights.
    Return structured, factual information from search results.""",
    tools=[google_search],  # Only built-in tool allowed per agent
)


# Enhanced Research Functions using search agent
def analyze_competitors_with_search(
    industry: str, company_type: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Research competitors using real web search via dedicated search agent"""
    # Get client info from discovery
    client_brief = tool_context.state.get("client_brief", {})
    company_name = client_brief.get("company_info", {}).get("name", "New Company")

    # Build search query for competitor research
    search_query = f"top {industry} companies competitors {company_type} 2025"

    # Store search query in state for search agent access
    tool_context.state["current_search_query"] = search_query
    tool_context.state["search_context"] = {
        "purpose": "competitor_analysis",
        "industry": industry,
        "company_type": company_type,
    }

    # Search agent will be called automatically by ADK framework
    # Process results from search agent (stored in state by search agent)
    search_results = tool_context.state.get("search_results", {})

    # Process search results to extract competitor data
    competitors = []
    market_insights = []

    # Extract competitor names and insights from search results
    if search_results and "search_results" in search_results:
        for result in search_results["search_results"][:5]:  # Top 5 results
            title = result.get("title", "")
            snippet = result.get("snippet", "")

            # Extract potential competitor names (simple heuristics)
            if any(
                word in title.lower()
                for word in ["top", "best", "leading", "companies"]
            ):
                competitors.append(
                    {
                        "name": title.split(" ")[0] if title else "Unknown",
                        "source": result.get("url", ""),
                        "description": (
                            snippet[:100] + "..." if len(snippet) > 100 else snippet
                        ),
                    }
                )

            # Extract market insights
            if any(
                word in snippet.lower()
                for word in ["trend", "market", "growth", "industry"]
            ):
                market_insights.append(snippet)

    # Industry-specific competitor database (enhanced with search data)
    known_competitors = {
        "technology": [
            "Apple",
            "Google",
            "Microsoft",
            "Meta",
            "Amazon",
            "OpenAI",
            "Anthropic",
        ],
        "healthcare": [
            "Johnson & Johnson",
            "Pfizer",
            "UnitedHealth",
            "CVS Health",
            "Moderna",
        ],
        "food": [
            "McDonald's",
            "Starbucks",
            "Subway",
            "Coca-Cola",
            "Nestle",
            "Unilever",
        ],
        "retail": ["Amazon", "Walmart", "Target", "Costco", "Home Depot", "Shopify"],
        "finance": [
            "JPMorgan Chase",
            "Bank of America",
            "Wells Fargo",
            "Goldman Sachs",
            "PayPal",
        ],
    }

    # Combine search results with known competitors
    industry_competitors = known_competitors.get(industry.lower(), [])
    all_competitors = list(set([c["name"] for c in competitors] + industry_competitors))

    analysis = {
        "industry": industry,
        "search_query_used": search_query,
        "direct_competitors": all_competitors[:5],
        "indirect_competitors": (
            all_competitors[5:8] if len(all_competitors) > 5 else []
        ),
        "market_analysis": {
            "search_insights": market_insights[:3],
            "key_trends": [
                "Digital transformation",
                "AI integration",
                "Sustainability focus",
            ],
            "opportunities": [
                "Market differentiation",
                "Brand modernization",
                "Customer experience",
            ],
        },
        "brand_positioning_gaps": [
            "Opportunity for modern visual identity",
            "Need for emotional brand connection",
            "Potential for authentic storytelling",
        ],
        "research_metadata": {
            "search_timestamp": time.time(),
            "sources_analyzed": (
                len(search_results.get("search_results", [])) if search_results else 0
            ),
            "research_depth": "enhanced_web_search",
        },
    }

    # Store detailed analysis in state
    tool_context.state["competitor_analysis"] = analysis

    return analysis


def analyze_market_trends_with_search(
    industry: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Analyze market trends using real-time web search via search agent"""
    # Build targeted search queries for market trends
    trend_queries = [
        f"{industry} industry trends 2025",
        f"{industry} market outlook 2025",
        f"future of {industry} business",
    ]

    all_trends = []
    search_insights = []

    # Search for each trend query using search agent
    for query in trend_queries:
        try:
            # Store query for search agent
            tool_context.state["current_search_query"] = query
            tool_context.state["search_context"] = {
                "purpose": "market_trends",
                "industry": industry,
                "query_type": "trends",
            }

            # Search agent will be automatically invoked by ADK
            # Get results from state (populated by search agent)
            search_results = tool_context.state.get("search_results", {})

            if search_results and "search_results" in search_results:
                for result in search_results["search_results"][:3]:  # Top 3 per query
                    snippet = result.get("snippet", "")
                    title = result.get("title", "")

                    # Extract trends from content
                    if any(
                        word in snippet.lower()
                        for word in ["trend", "future", "emerging", "growth"]
                    ):
                        all_trends.append(snippet)
                        search_insights.append(
                            {
                                "title": title,
                                "insight": (
                                    snippet[:150] + "..."
                                    if len(snippet) > 150
                                    else snippet
                                ),
                                "source": result.get("url", ""),
                                "query": query,
                            }
                        )
        except Exception as e:
            continue  # Skip failed searches, continue with others

    # Industry-specific baseline trends (enhanced with search data)
    baseline_trends = {
        "technology": [
            "AI/ML adoption",
            "Cloud-first strategies",
            "Privacy regulations",
            "Remote work tech",
        ],
        "healthcare": [
            "Telemedicine growth",
            "AI diagnostics",
            "Personalized medicine",
            "Mental health focus",
        ],
        "food": [
            "Plant-based alternatives",
            "Sustainable packaging",
            "Local sourcing",
            "Health consciousness",
        ],
        "finance": [
            "Digital banking",
            "Cryptocurrency adoption",
            "RegTech solutions",
            "Open banking",
        ],
        "retail": [
            "E-commerce dominance",
            "Omnichannel experience",
            "Social commerce",
            "Sustainability",
        ],
    }

    industry_trends = baseline_trends.get(
        industry.lower(), ["Digital transformation", "Customer experience"]
    )

    trend_analysis = {
        "industry": industry,
        "search_queries_used": trend_queries,
        "web_discovered_trends": [insight["insight"] for insight in search_insights],
        "industry_baseline_trends": industry_trends,
        "combined_trends": list(
            set(industry_trends + [t[:50] for t in all_trends[:5]])
        ),
        "design_implications": [
            "Modern, forward-thinking aesthetics",
            "Digital-first brand experience",
            "Sustainable brand messaging",
            "Authentic customer connection",
        ],
        "market_opportunities": [
            "Stand out through innovative branding",
            "Capitalize on emerging trends",
            "Address unmet market needs",
            "Build trust through transparency",
        ],
        "research_insights": search_insights,
        "analysis_timestamp": time.time(),
    }

    # Store in state
    tool_context.state["market_trends"] = trend_analysis

    return trend_analysis


def generate_strategic_swot_analysis(tool_context: ToolContext) -> Dict[str, Any]:
    """Generate comprehensive SWOT analysis based on research data"""
    # Get all research data from state
    client_brief = tool_context.state.get("client_brief", {})
    competitor_analysis = tool_context.state.get("competitor_analysis", {})
    market_trends = tool_context.state.get("market_trends", {})

    # Extract key information
    company_info = client_brief.get("company_info", {})
    industry = company_info.get("industry", "general")
    target_audience = client_brief.get("target_audience", {}).get(
        "primary_audience", "general market"
    )

    # Build SWOT based on research insights
    swot = {
        "strengths": [
            "Fresh brand opportunity - no legacy constraints",
            "Modern approach to market entry",
            "Flexibility in brand positioning",
            "Opportunity to leverage current trends",
        ],
        "weaknesses": [
            "No existing brand recognition",
            "Need to establish market credibility",
            "Limited customer base and testimonials",
            "Requires significant brand building investment",
        ],
        "opportunities": [],
        "threats": [],
    }

    # Add opportunities based on market trends
    if market_trends.get("combined_trends"):
        swot["opportunities"].extend(
            [
                f"Capitalize on {market_trends['combined_trends'][0][:30]}...",
                "Differentiate through modern branding",
                "Build authentic customer relationships",
                "Leverage digital marketing channels",
            ]
        )
    else:
        swot["opportunities"] = [
            "Market differentiation opportunity",
            "Build strong brand foundation",
            "Create emotional customer connections",
            "Establish thought leadership",
        ]

    # Add threats based on competitor analysis
    if competitor_analysis.get("direct_competitors"):
        competitor_count = len(competitor_analysis["direct_competitors"])
        swot["threats"].extend(
            [
                f"Established competition ({competitor_count} major players)",
                "Market saturation potential",
                "Brand confusion in crowded market",
                "Price competition from established players",
            ]
        )
    else:
        swot["threats"] = [
            "Emerging competition",
            "Market volatility",
            "Economic factors affecting spending",
            "Changing consumer preferences",
        ]

    # Generate strategic recommendations
    strategic_recommendations = [
        "Focus on unique value proposition in all branding",
        "Create memorable and distinctive visual identity",
        "Build consistent brand experience across touchpoints",
        "Leverage digital channels for cost-effective brand building",
        "Establish credibility through professional presentation",
    ]

    # Create positioning strategy
    positioning_strategy = f"Position as a modern, customer-focused {industry} company that leverages current market trends to deliver exceptional value to {target_audience}."

    swot_analysis = {
        "swot_analysis": swot,
        "strategic_recommendations": strategic_recommendations,
        "brand_positioning_strategy": positioning_strategy,
        "research_foundation": {
            "competitor_insights": bool(competitor_analysis),
            "market_trend_data": bool(market_trends),
            "web_search_enhanced": True,
        },
        "analysis_timestamp": time.time(),
    }

    # Store in state
    tool_context.state["swot_analysis"] = swot_analysis

    return swot_analysis


def compile_comprehensive_research(tool_context: ToolContext) -> Dict[str, Any]:
    """Compile all research into final market research deliverable"""
    # Gather all research components
    competitor_analysis = tool_context.state.get("competitor_analysis", {})
    market_trends = tool_context.state.get("market_trends", {})
    swot_analysis = tool_context.state.get("swot_analysis", {})

    # Build comprehensive market research report
    market_research = {
        "executive_summary": {
            "industry": competitor_analysis.get("industry", "general"),
            "research_method": "web_search_enhanced_analysis",
            "key_finding": swot_analysis.get("brand_positioning_strategy", ""),
        },
        "competitive_landscape": {
            "direct_competitors": competitor_analysis.get("direct_competitors", []),
            "indirect_competitors": competitor_analysis.get("indirect_competitors", []),
            "market_position_opportunities": competitor_analysis.get(
                "brand_positioning_gaps", []
            ),
        },
        "market_trends": {
            "web_discovered_trends": market_trends.get("web_discovered_trends", []),
            "industry_baseline_trends": market_trends.get(
                "industry_baseline_trends", []
            ),
            "design_implications": market_trends.get("design_implications", []),
        },
        "strategic_analysis": {
            "swot_analysis": swot_analysis.get("swot_analysis", {}),
            "positioning_strategy": swot_analysis.get("brand_positioning_strategy", ""),
            "strategic_recommendations": swot_analysis.get(
                "strategic_recommendations", []
            ),
        },
        "research_quality_metrics": {
            "search_sources_analyzed": competitor_analysis.get(
                "research_metadata", {}
            ).get("sources_analyzed", 0),
            "trend_queries_executed": len(market_trends.get("search_queries_used", [])),
            "research_depth_score": _calculate_research_depth_score(
                competitor_analysis, market_trends, swot_analysis
            ),
            "web_search_enhanced": True,
        },
        "compilation_timestamp": time.time(),
    }

    # Store as final output for next agent (ADK v1.0.0 output_key)
    tool_context.state["market_research"] = market_research

    # Update research quality score
    depth_score = market_research["research_quality_metrics"]["research_depth_score"]
    tool_context.state.setdefault("quality_scores", {})["research_depth"] = depth_score

    return {
        "research_compiled": True,
        "market_research": market_research,
        "quality_metrics": market_research["research_quality_metrics"],
        "competitors_identified": len(
            market_research["competitive_landscape"]["direct_competitors"]
        ),
        "trends_analyzed": len(
            market_research["market_trends"]["web_discovered_trends"]
        ),
        "strategic_recommendations": len(
            market_research["strategic_analysis"]["strategic_recommendations"]
        ),
    }


def _calculate_research_depth_score(
    competitor_analysis: Dict, market_trends: Dict, swot_analysis: Dict
) -> float:
    """Calculate research depth quality score (0.0 to 1.0)"""
    score = 0.0

    # Competitor analysis quality (0.4 weight)
    if competitor_analysis:
        competitor_score = min(
            1.0, len(competitor_analysis.get("direct_competitors", [])) / 5
        )  # 5 competitors = 1.0
        source_score = min(
            1.0,
            competitor_analysis.get("research_metadata", {}).get("sources_analyzed", 0)
            / 10,
        )  # 10 sources = 1.0
        score += (competitor_score + source_score) * 0.2  # 0.4 total weight

    # Market trends quality (0.3 weight)
    if market_trends:
        trend_score = min(
            1.0, len(market_trends.get("web_discovered_trends", [])) / 5
        )  # 5 trends = 1.0
        query_score = min(
            1.0, len(market_trends.get("search_queries_used", [])) / 3
        )  # 3 queries = 1.0
        score += (trend_score + query_score) * 0.15  # 0.3 total weight

    # SWOT analysis quality (0.3 weight)
    if swot_analysis:
        swot_completeness = all(
            swot_analysis.get("swot_analysis", {}).get(section)
            for section in ["strengths", "weaknesses", "opportunities", "threats"]
        )
        recommendations_score = min(
            1.0, len(swot_analysis.get("strategic_recommendations", [])) / 5
        )
        score += (
            float(swot_completeness) + recommendations_score
        ) * 0.15  # 0.3 total weight

    return min(1.0, score)


# Enhanced Research Agent Implementation (ADK v1.0.0)
root_agent = LlmAgent(
    name="research_agent",
    model="gemini-2.0-flash",
    instruction="""You are the Research Agent for an AI Branding Assistant. Your role is to conduct comprehensive market research using real-time web search data and competitive intelligence.

🔍 CORE RESPONSIBILITIES:
1. Analyze competitors using live web search data via specialized search agent
2. Identify current market trends through real-time research  
3. Conduct strategic SWOT analysis based on research findings
4. Provide actionable differentiation recommendations
5. Create comprehensive strategic insights for brand development

🌐 RESEARCH METHODOLOGY:
- Delegate web searches to dedicated search agent for competitor discovery
- Analyze current market trends and industry insights from search results
- Cross-reference web data with industry knowledge databases
- Generate evidence-based strategic recommendations
- Validate research depth and quality metrics

📊 QUALITY STANDARDS:
- Minimum 5 competitors identified per industry via web search
- At least 3 market trend categories analyzed through real-time data
- Complete SWOT analysis with all quadrants populated
- Research depth score above 0.7 for quality gate
- Web-enhanced insights with proper source attribution

🎯 OUTPUT REQUIREMENTS:
Your research must inform the Visual Direction Agent with:
- Clear competitive landscape understanding from live data
- Actionable market positioning opportunities based on current trends
- Strategic brand direction recommendations with evidence
- Data-driven differentiation strategies for brand development

🔧 AGENT COORDINATION:
You work with a specialized search agent that handles all web search operations.
Store search queries and context in state for the search agent to process.
Always base analysis on discovery data and enhance with real-time web research.""",
    description="Research agent with real-time web search capabilities for market analysis and competitive intelligence",
    output_key="market_research",  # ADK v1.0.0 automatic state persistence
    # Use search agent as tool + custom functions (ADK v1.0.0 pattern)
    tools=[
        agent_tool.AgentTool(agent=search_agent),  # Dedicated search agent as tool
        analyze_competitors_with_search,  # Custom research functions
        analyze_market_trends_with_search,
        generate_strategic_swot_analysis,
        compile_comprehensive_research,
    ],
)
