# Federated Search Domain-Aware Enhancement

## Overview
Enhanced the federated search system to intelligently route queries to domain-specific sources based on query classification. This ensures that queries about sports, financial markets, music, and other non-academic topics are searched using specialized sources rather than generic scholarly databases.

## Key Features

### 1. Domain Detection System (`DomainDetector`)
- **Purpose**: Classifies queries into appropriate domains (sports, financial, music, academic, technology, entertainment)
- **Method**: Keyword and context indicator matching with confidence scoring
- **Output**: Primary domain, confidence score, matched keywords, and all domain scores

### 2. Domain-Specific Search Agents

#### `SportsDomainAgent`
- **Sources**: ESPN, Sports Illustrated, The Athletic, Bleacher Report, CBS Sports, NBC Sports
- **Use Case**: Sports-related queries (athletes, teams, matches, championships, records)
- **Search Rigor**: Site-specific searches using DuckDuckGo to target specialized sports media

#### `FinancialDomainAgent`
- **Sources**: Bloomberg, Reuters Finance, MarketWatch, Financial Times, WSJ, CNBC, Yahoo Finance
- **Use Case**: Financial and economic queries (stocks, markets, trading, investments, earnings)
- **Search Rigor**: Site-specific searches targeting reputable financial news and analysis sources

#### `MusicDomainAgent`
- **Sources**: Pitchfork, Rolling Stone, AllMusic, Billboard, Stereogum, NPR Music
- **Use Case**: Music-related queries (artists, albums, songs, genres, charts, awards)
- **Search Rigor**: Site-specific searches targeting music journalism and review sources

### 3. Domain-Aware Routing Logic

The `RISEEnhancedSynergisticInquiry` orchestrator now:

1. **Detects Query Domain**: Uses `DomainDetector` to classify incoming queries
2. **Routes Intelligently**:
   - **Academic queries** → Routes to `AcademicKnowledgeAgent` (ArXiv) and general academic sources
   - **Sports queries** → Routes to `SportsDomainAgent` + complementary general agents
   - **Financial queries** → Routes to `FinancialDomainAgent` + complementary general agents
   - **Music queries** → Routes to `MusicDomainAgent` + complementary general agents
   - **General/Low-confidence** → Routes to default academic and general agents
3. **Applies Appropriate Rigor**: Each domain agent searches specialized sources with domain-appropriate depth

## Implementation Details

### Domain Detection Thresholds
- **High Confidence (>0.3)**: Routes to domain-specific agents
- **Low Confidence (<0.3)**: Falls back to academic/general agents
- **Academic Domain**: Always uses academic agents regardless of confidence

### Search Strategy
- **Domain-Specific Agents**: Search 3 top sources per domain for performance
- **Complementary Agents**: Always includes `community` (Reddit) and `visual` (YouTube) for context
- **Max Results**: 8 results per query phase for domain agents, 8 for general agents

### Results Metadata
- Each result includes:
  - `domain`: The detected domain (sports, financial, music, etc.)
  - `source_type`: Specialized media type indicator
  - `source`: Specific source name (e.g., "SportsDomain (ESPN)")
  - Standard fields: `title`, `url`, `snippet`, `search_query`

## Example Query Routing

### Sports Query: "Who would win in a match Mike Tyson in his prime or George Foreman in his prime"
- **Domain Detected**: `sports` (confidence: 0.7)
- **Routing**: `SportsDomainAgent` → Searches ESPN, Sports Illustrated, The Athletic for boxing history and fighter analysis
- **Complementary**: Reddit discussions + YouTube videos for additional context
- **Result**: Specialized sports media analysis of fighter statistics, career records, head-to-head comparisons

### Financial Query: "What is the current price of Bitcoin and what factors influence it?"
- **Domain Detected**: `financial` (confidence: 0.8)
- **Routing**: `FinancialDomainAgent` → Searches Bloomberg, Reuters Finance, MarketWatch for crypto market analysis
- **Complementary**: Reddit discussions + general search for real-time community sentiment
- **Result**: Financial news and analysis from reputable financial media sources

### Academic Query: "Recent research on machine learning optimization algorithms"
- **Domain Detected**: `academic` (confidence: 0.9)
- **Routing**: `AcademicKnowledgeAgent` → Searches ArXiv for peer-reviewed papers
- **Complementary**: General search engines and code repositories for implementation examples
- **Result**: Academic papers from ArXiv and scholarly sources

## Benefits

1. **Improved Relevance**: Non-academic queries receive results from specialized domain sources rather than generic scholarly databases
2. **Appropriate Rigor**: Each domain uses sources with the appropriate level of rigor for that niche (sports journalism, financial news, music criticism)
3. **Better Coverage**: Domain-specific agents ensure comprehensive coverage of specialized knowledge areas
4. **Efficient Routing**: Intelligent domain detection prevents unnecessary searches in irrelevant academic databases

## Files Modified

1. **`Three_PointO_ArchE/federated_search_agents.py`**:
   - Added `DomainDetector` class
   - Added `SportsDomainAgent` class
   - Added `FinancialDomainAgent` class
   - Added `MusicDomainAgent` class

2. **`Three_PointO_ArchE/rise_enhanced_synergistic_inquiry.py`**:
   - Added domain detector initialization
   - Added domain-specific agent initialization
   - Enhanced `_execute_rise_enhanced_phase` with domain-aware routing logic

## Future Enhancements

Potential additions:
- Technology domain agent (TechCrunch, Ars Technica, The Verge, etc.)
- Entertainment domain agent (Variety, The Hollywood Reporter, etc.)
- Health/Medical domain agent (WebMD, Mayo Clinic, PubMed, etc.)
- More sophisticated domain detection using LLM-based classification
- Domain-specific result ranking and relevance scoring

## Testing

To test the enhancement, run queries like:
- Sports: "Compare Mike Tyson vs George Foreman boxing careers"
- Financial: "Bitcoin price forecast 2024"
- Music: "Best jazz albums 2023"
- Academic: "Quantum computing research 2024"

The system will automatically detect the domain and route to appropriate specialized agents.


