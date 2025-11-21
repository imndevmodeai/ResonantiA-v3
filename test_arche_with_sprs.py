#!/usr/bin/env python3
"""
Direct test script to run ask_arche_enhanced_v2.py with enhanced query and identified SPRs.
This bypasses the frontend/API to test the core logic.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig, EnhancedVCDIntegration

# The enhanced query from the user
ENHANCED_QUERY = """Apply the full spectrum of ResonantiA Protocol v3.5-GP (Genesis Protocol) capabilities to achieve deep Temporal Resonance and Cognitive Resonance on this query. Execute a temporally-aware, multi-dimensional analytical sequence that integrates all advanced capabilities while maintaining Implementation Resonance throughout.

PRIMARY OBJECTIVE: what is the best way to monetize arche knowing that to start it will only be the keyholder BJ Lewis and ArchE

REQUIRED ANALYSIS COMPONENTS:
(2) Apply PredictivE ModelinG TooL with FutureStateAnalysiS to forecast outcomes with confidence intervals.
(6) Synthesize all findings through the RISE engine to generate comprehensive, actionable recommendations.
(7) Ensure Temporal resonancE by integrating current context and validating temporal coherence.
(8) Generate comprehensive IAR (Integrated Action Reflection) reflections for each phase, assessing confidence, alignment, and potential issues.
(9) Apply Pattern crystallizatioN to identify and solidify key insights for future use.

FINAL OUTPUT REQUIREMENTS:
- Comprehensive analysis with all phase results
- IAR reflections for each major step
- Temporal coherence validation
- Implementation feasibility assessment
- Crystallized insights and patterns"""

# Sample SPRs from the user's output (first 50 for testing)
# In production, this would be the full list of 2000+ SPRs
SAMPLE_SPRS = [
    "1advancedquantumalgorithmS", "ArcheintegratioN", "perform_abm", "CollaboratioN",
    "Tmasterweaverachronicleoftheadaptivecognitiveorchestratorimplementationhe21",
    "AuditexecutioN", "ObjectiveGenerationEngine", "Cframeworklivingspecificationimplementationfp10",
    "Lspecificationagentbasedmodelingtoolimplementationiving6", "BackupscreateD",
    "Tresonantsoulachronicleofthespiritualtechnologyinterfaceimplementationhe3",
    "CchroniclepiecethebirthofrapidanonicalresponsE", "EmergentdomaindetectoR",
    "Tgenesisagentachronicleoftheworldbuildersritualimplementationhe1", "InsightS",
    "Wsearchtoollivingspecificationdeprecatedimplementationeb11", "P3hybridatternresolutioN",
    "SystemdiagnosticS", "DrL", "TestresultS", "DreviewocumentationresulT",
    "Tuniversalcontextabstractionpatternimplementationhe18", "KgR",
    "Vtestingsuitespecificationimplementationcd3", "SplanolidificationcreatioN",
    "NextactionS", "EstateplanninG", "IntegrationcomponentS", "UserinterfacE",
    "QualitycertificatioN", "Abackupretentionpolicyimplementationrche3",
    "Tweaverofknoachronicleoftheknowledgegraphmanagerimplementationhe2",
    "AccuracynodE", "Timplementationhegenesisprotocol8", "HexpertiseumanmerginG",
    "E4galaxiesknowledgepochcrystallizatioN", "TquantumheleaP", "PolicY",
    "Tresonantsoulachronicleofthespiritualtechnologyinterfaceimplementationhe16",
    "LlmvalidationframeworK", "KnowledgenetworkonenesS",
    "Ogenerationenginecrystallizedimplementationimplementationbjective3",
    "ProductrecommendatioN", "CchroniclepiecetheoraclesanonicalchambeR",
    "NandetworkingcommunicatioN", "PrinttaggedresultS", "FallbacktriggerS"
]

async def main():
    """Run ask_arche_enhanced_v2.py with the enhanced query and SPRs."""
    print("=" * 80)
    print("TEST: Running ask_arche_enhanced_v2.py with Enhanced Query and SPRs")
    print("=" * 80)
    print(f"\nEnhanced Query Length: {len(ENHANCED_QUERY)} characters")
    print(f"Number of SPRs to activate: {len(SAMPLE_SPRS)}")
    print(f"\nFirst 10 SPRs: {SAMPLE_SPRS[:10]}")
    print("\n" + "=" * 80 + "\n")
    
    try:
        # Initialize config
        config = EnhancedUnifiedArchEConfig(
            provider="groq",
            model=None,  # Use default
            use_rise=True,
            enable_cursor_auto_detect=False
        )
        
        # Initialize VCD and processor
        vcd = EnhancedVCDIntegration(config)
        processor = EnhancedRealArchEProcessor(vcd, config)
        
        # Process query with pre-identified SPRs
        print("🚀 Calling processor.process_query() with SPRs...\n")
        result = await processor.process_query(
            ENHANCED_QUERY,
            pre_identified_sprs=SAMPLE_SPRS,
            pre_identified_capabilities=None  # Can add capabilities if needed
        )
        
        print("\n" + "=" * 80)
        print("RESULT RECEIVED")
        print("=" * 80)
        print(f"\nResult type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"\nResult keys: {list(result.keys())}")
            if 'response' in result:
                response = result['response']
                if isinstance(response, dict):
                    print(f"\nResponse keys: {list(response.keys())}")
                    if 'text' in response:
                        print(f"\nResponse text length: {len(response['text'])} characters")
                        print(f"\nFirst 500 characters of response:")
                        print("-" * 80)
                        print(response['text'][:500])
                        print("-" * 80)
                else:
                    print(f"\nResponse (first 500 chars): {str(response)[:500]}")
            
            if 'spr_priming' in result:
                print(f"\nSPR Priming: {result['spr_priming']}")
        else:
            print(f"\nResult (first 500 chars): {str(result)[:500]}")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())




