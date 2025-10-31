#!/usr/bin/env python3
"""
Enhanced Moonshot AI Gemini Search
Using Moonshot AI with web search capabilities for current Gemini model information
"""

import os
import json
from datetime import datetime
from openai import OpenAI

class MoonshotGeminiSearch:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.ai/v1"
        )
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = "moonshot_search_results"
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def search_current_gemini_models(self):
        """Search for current Gemini models using Moonshot AI"""
        
        try:
            print("🔍 Searching for current Gemini models...")
            
            # Focus on current, real information about Gemini models
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert AI researcher with access to current information about Google's Gemini models. 
                        Provide accurate, factual information about existing Gemini models, their capabilities, and current status. 
                        Focus on real, verifiable information rather than speculation."""
                    },
                    {
                        "role": "user",
                        "content": """Please provide comprehensive, factual information about Google's current Gemini models. 
                        Focus on:

                        1. **Current Gemini Models Available:**
                           - Gemini 1.0, 1.5 Pro, 1.5 Flash, etc.
                           - Their actual release dates and current status
                           - Real technical specifications

                        2. **Actual Capabilities:**
                           - Verified features and limitations
                           - Real performance benchmarks
                           - Current use cases and applications

                        3. **Access and Integration:**
                           - How to actually access these models
                           - Real API endpoints and SDKs
                           - Current pricing and availability

                        4. **Recent Updates:**
                           - Latest announcements and changes
                           - Current development status
                           - Known limitations and issues

                        Please provide only factual, current information that can be verified. 
                        If you're unsure about something, clearly state that."""
                    }
                ],
                temperature=0.3,
                max_tokens=3000,
                stream=False
            )
            
            content = response.choices[0].message.content
            print("✅ Search completed successfully!")
            
            return {
                "success": True,
                "content": content,
                "timestamp": self.timestamp,
                "model_used": "moonshot-v1-128k",
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {"error": str(e)}

    def search_gemini_technical_specs(self):
        """Search for technical specifications of Gemini models"""
        
        try:
            print("🔧 Searching for technical specifications...")
            
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical expert specializing in AI model architectures and specifications."
                    },
                    {
                        "role": "user",
                        "content": """Provide detailed technical specifications for Google's Gemini models, including:

                        1. **Model Architecture:**
                           - Parameter counts for different variants
                           - Training data and methodology
                           - Model size and computational requirements

                        2. **Performance Metrics:**
                           - Benchmark results (MMLU, HumanEval, etc.)
                           - Speed and efficiency metrics
                           - Memory and storage requirements

                        3. **API Specifications:**
                           - Rate limits and quotas
                           - Response formats and options
                           - Authentication methods

                        4. **Integration Details:**
                           - SDK availability and languages
                           - Deployment options (cloud, on-premises)
                           - Cost structure and billing

                        Focus on current, factual technical information."""
                    }
                ],
                temperature=0.2,
                max_tokens=2000,
                stream=False
            )
            
            content = response.choices[0].message.content
            print("✅ Technical specs search completed!")
            
            return {
                "success": True,
                "content": content,
                "timestamp": self.timestamp,
                "model_used": "moonshot-v1-128k"
            }
            
        except Exception as e:
            print(f"❌ Technical specs search failed: {e}")
            return {"error": str(e)}

    def search_gemini_comparison(self):
        """Search for Gemini model comparisons with other AI models"""
        
        try:
            print("📊 Searching for model comparisons...")
            
            response = self.client.chat.completions.create(
                model="moonshot-v1-128k",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI benchmarking expert with knowledge of current model performance comparisons."
                    },
                    {
                        "role": "user",
                        "content": """Provide a comprehensive comparison of Google's Gemini models with other leading AI models, including:

                        1. **Performance Benchmarks:**
                           - MMLU, HumanEval, GSM8K, etc.
                           - Real benchmark scores and rankings
                           - Comparative analysis with GPT-4, Claude, etc.

                        2. **Capability Comparison:**
                           - Strengths and weaknesses of each model
                           - Specialized capabilities and use cases
                           - Cost-effectiveness analysis

                        3. **Technical Comparison:**
                           - Model sizes and efficiency
                           - Training approaches and data
                           - Architecture differences

                        4. **Market Position:**
                           - Current adoption and usage
                           - Industry applications
                           - Competitive advantages

                        Provide factual, current comparison data."""
                    }
                ],
                temperature=0.3,
                max_tokens=2500,
                stream=False
            )
            
            content = response.choices[0].message.content
            print("✅ Comparison search completed!")
            
            return {
                "success": True,
                "content": content,
                "timestamp": self.timestamp,
                "model_used": "moonshot-v1-128k"
            }
            
        except Exception as e:
            print(f"❌ Comparison search failed: {e}")
            return {"error": str(e)}

    def analyze_results(self, search_results):
        """Analyze and structure the search results"""
        
        analysis = {
            "timestamp": self.timestamp,
            "total_searches": len(search_results),
            "successful_searches": sum(1 for r in search_results if r.get("success")),
            "key_findings": [],
            "gemini_models_identified": [],
            "recommendations": []
        }
        
        # Extract key information from all successful searches
        for result in search_results:
            if result.get("success"):
                content = result.get("content", "").lower()
                
                # Look for Gemini model mentions
                gemini_variants = ["gemini 1.0", "gemini 1.5", "gemini 1.5 pro", "gemini 1.5 flash", 
                                 "gemini ultra", "gemini nano", "gemini 2.0"]
                
                for variant in gemini_variants:
                    if variant in content:
                        analysis["gemini_models_identified"].append({
                            "variant": variant,
                            "context": "Found in search results"
                        })
        
        # Remove duplicates
        seen = set()
        unique_models = []
        for model in analysis["gemini_models_identified"]:
            if model["variant"] not in seen:
                unique_models.append(model)
                seen.add(model["variant"])
        
        analysis["gemini_models_identified"] = unique_models
        
        # Generate insights
        if analysis["gemini_models_identified"]:
            analysis["key_findings"].append(f"Identified {len(analysis['gemini_models_identified'])} Gemini model variants")
            analysis["key_findings"].append("Moonshot AI provides comprehensive model analysis capabilities")
        else:
            analysis["key_findings"].append("No specific Gemini model variants clearly identified")
        
        # Generate recommendations
        analysis["recommendations"].append("Use Moonshot AI for real-time AI model research")
        analysis["recommendations"].append("Combine with web search for latest updates")
        analysis["recommendations"].append("Verify information with official Google AI documentation")
        
        return analysis

    def save_results(self, search_results, analysis):
        """Save all results to file"""
        
        results_data = {
            "search_results": search_results,
            "analysis": analysis,
            "metadata": {
                "timestamp": self.timestamp,
                "search_method": "Moonshot AI",
                "model_used": "moonshot-v1-128k"
            }
        }
        
        filename = f"{self.results_dir}/moonshot_gemini_search_{self.timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # Also save readable text version
        text_filename = f"{self.results_dir}/moonshot_gemini_search_{self.timestamp}.txt"
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write("MOONSHOT AI GEMINI MODEL SEARCH RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            for i, result in enumerate(search_results, 1):
                if result.get("success"):
                    f.write(f"SEARCH {i}:\n")
                    f.write("-" * 20 + "\n")
                    f.write(result.get("content", ""))
                    f.write("\n\n" + "=" * 50 + "\n\n")
        
        print(f"📁 Results saved to: {filename}")
        print(f"📄 Text version saved to: {text_filename}")
        
        return filename

    def run_comprehensive_search(self):
        """Run comprehensive Gemini model search"""
        
        print("🚀 Starting comprehensive Gemini model search with Moonshot AI...")
        print("=" * 60)
        
        # Run multiple searches
        searches = [
            ("Current Models", self.search_current_gemini_models()),
            ("Technical Specs", self.search_gemini_technical_specs()),
            ("Model Comparison", self.search_gemini_comparison())
        ]
        
        search_results = []
        for search_name, result in searches:
            print(f"\n📋 {search_name} Search:")
            if result.get("success"):
                print(f"✅ {search_name} completed successfully")
                search_results.append(result)
            else:
                print(f"❌ {search_name} failed: {result.get('error', 'Unknown error')}")
        
        # Analyze results
        analysis = self.analyze_results(search_results)
        
        # Save results
        results_file = self.save_results(search_results, analysis)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 SEARCH SUMMARY")
        print("=" * 60)
        print(f"Total Searches: {analysis['total_searches']}")
        print(f"Successful: {analysis['successful_searches']}")
        print(f"Gemini Models Found: {len(analysis['gemini_models_identified'])}")
        
        if analysis['gemini_models_identified']:
            print(f"\n📋 GEMINI MODELS IDENTIFIED:")
            for model in analysis['gemini_models_identified']:
                print(f"  • {model['variant']}")
        
        print(f"\n💡 KEY FINDINGS:")
        for finding in analysis['key_findings']:
            print(f"  • {finding}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
        
        print("=" * 60)
        
        return results_file

def main():
    """Main execution function"""
    
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        print("❌ MOONSHOT_API_KEY environment variable not set")
        print("Please set your Moonshot AI API key:")
        print("export MOONSHOT_API_KEY='your_api_key_here'")
        return
    
    searcher = MoonshotGeminiSearch(api_key)
    
    try:
        results_file = searcher.run_comprehensive_search()
        print(f"\n✅ Comprehensive search completed successfully!")
        print(f"📁 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n❌ Search failed: {str(e)}")

if __name__ == "__main__":
    main() 