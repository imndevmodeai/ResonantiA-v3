#!/usr/bin/env python3
"""
Kimi-K2 API Integration for Latest Gemini Models Search
ResonantiA Protocol v3.1-CA Implementation Resonance Tool

This script uses the Kimi-K2 API to search for the latest Gemini models
and extract comprehensive information about Google AI's current offerings.
"""

import json
import os
import sys
from datetime import datetime
import logging
from typing import Dict, List, Any
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kimi_k2_search.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class KimiK2Search:
    def __init__(self, api_key: str = None, base_url: str = "https://api.moonshot.cn/v1"):
        self.api_key = api_key or os.getenv('MOONSHOT_API_KEY')
        self.base_url = base_url
        self.results_dir = "kimi_k2_search_results"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
        if not self.api_key:
            logging.warning("No API key provided. Set MOONSHOT_API_KEY environment variable or pass api_key parameter.")

    def search_gemini_models(self, query: str = "latest Gemini models 2025 Google AI") -> Dict[str, Any]:
        """Search for latest Gemini models using Kimi-K2 API"""
        
        if not self.api_key:
            return {"error": "API key required for Kimi-K2 search"}
        
        try:
            logging.info(f"Searching Kimi-K2 for: {query}")
            
            # Prepare the search query with specific instructions
            search_prompt = f"""
            Please search for and provide comprehensive information about the latest Gemini models from Google AI in 2025. 
            Include the following details:
            
            1. Latest Gemini model names and versions
            2. Key features and capabilities
            3. Performance benchmarks and comparisons
            4. Release dates and availability
            5. Technical specifications
            6. Use cases and applications
            7. Pricing and access information
            8. Integration methods and APIs
            
            Query: {query}
            
            Please provide a detailed, well-structured response with accurate, up-to-date information.
            """
            
            # API request payload
            payload = {
                "model": "kimi-k2-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert AI researcher specializing in large language models and AI technology. Provide accurate, comprehensive, and up-to-date information about AI models, particularly focusing on Google's Gemini series."
                    },
                    {
                        "role": "user",
                        "content": search_prompt
                    }
                ],
                "temperature": 0.6,
                "max_tokens": 4000,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                logging.info("Kimi-K2 search completed successfully")
                
                return {
                    "success": True,
                    "query": query,
                    "timestamp": self.timestamp,
                    "content": content,
                    "model_used": "kimi-k2-instruct",
                    "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                }
            else:
                logging.error(f"API request failed: {response.status_code} - {response.text}")
                return {
                    "error": f"API request failed: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logging.error(f"Kimi-K2 search failed: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}

    def search_with_tools(self, query: str = "latest Gemini models 2025") -> Dict[str, Any]:
        """Search using Kimi-K2's tool calling capabilities"""
        
        if not self.api_key:
            return {"error": "API key required for Kimi-K2 search"}
        
        try:
            logging.info(f"Searching Kimi-K2 with tools for: {query}")
            
            # Define web search tool
            tools = [{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for current information about AI models, technology news, and latest developments",
                    "parameters": {
                        "type": "object",
                        "required": ["query"],
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for web search"
                            }
                        }
                    }
                }
            }]
            
            # Tool implementation
            def web_search(query: str) -> dict:
                """Simulate web search - in real implementation, this would call a web search API"""
                return {
                    "search_results": f"Web search results for: {query}",
                    "status": "simulated_search",
                    "note": "This is a simulated web search. In production, integrate with actual web search API."
                }
            
            tool_map = {"web_search": web_search}
            
            # Initial request
            payload = {
                "model": "kimi-k2-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert AI researcher. Use the web search tool to find the latest information about Gemini models, then provide a comprehensive analysis."
                    },
                    {
                        "role": "user",
                        "content": f"Search for the latest Gemini models from Google AI in 2025 and provide detailed information about their capabilities, performance, and availability."
                    }
                ],
                "temperature": 0.6,
                "tools": tools,
                "tool_choice": "auto",
                "max_tokens": 4000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                choice = result['choices'][0]
                finish_reason = choice['finish_reason']
                
                if finish_reason == "tool_calls":
                    # Handle tool calls
                    messages = payload["messages"]
                    messages.append(choice['message'])
                    
                    for tool_call in choice['message']['tool_calls']:
                        tool_name = tool_call['function']['name']
                        tool_args = json.loads(tool_call['function']['arguments'])
                        
                        if tool_name in tool_map:
                            tool_result = tool_map[tool_name](**tool_args)
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call['id'],
                                "name": tool_name,
                                "content": json.dumps(tool_result)
                            })
                    
                    # Make final request with tool results
                    final_payload = {
                        "model": "kimi-k2-instruct",
                        "messages": messages,
                        "temperature": 0.6,
                        "max_tokens": 4000
                    }
                    
                    final_response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=final_payload,
                        timeout=60
                    )
                    
                    if final_response.status_code == 200:
                        final_result = final_response.json()
                        content = final_result['choices'][0]['message']['content']
                        
                        return {
                            "success": True,
                            "query": query,
                            "timestamp": self.timestamp,
                            "content": content,
                            "model_used": "kimi-k2-instruct",
                            "tools_used": True,
                            "tokens_used": final_result.get('usage', {}).get('total_tokens', 0)
                        }
                
                else:
                    # Direct response without tool calls
                    content = choice['message']['content']
                    return {
                        "success": True,
                        "query": query,
                        "timestamp": self.timestamp,
                        "content": content,
                        "model_used": "kimi-k2-instruct",
                        "tools_used": False,
                        "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                    }
            else:
                logging.error(f"API request failed: {response.status_code} - {response.text}")
                return {
                    "error": f"API request failed: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logging.error(f"Kimi-K2 tool search failed: {str(e)}")
            return {"error": f"Tool search failed: {str(e)}"}

    def analyze_results(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search results to extract key insights"""
        
        if not search_result.get("success"):
            return {"error": "No successful search results to analyze"}
        
        content = search_result.get("content", "")
        
        analysis = {
            "timestamp": self.timestamp,
            "query": search_result.get("query", ""),
            "model_used": search_result.get("model_used", ""),
            "tokens_used": search_result.get("tokens_used", 0),
            "tools_used": search_result.get("tools_used", False),
            "key_insights": [],
            "gemini_models_found": [],
            "recommendations": []
        }
        
        # Extract Gemini model information
        gemini_keywords = ["Gemini", "gemini", "1.5", "2.0", "Pro", "Flash", "Nano", "Ultra", "Advanced"]
        
        for keyword in gemini_keywords:
            if keyword.lower() in content.lower():
                analysis["gemini_models_found"].append({
                    "keyword": keyword,
                    "context": "Found in Kimi-K2 response"
                })
        
        # Generate insights
        if analysis["gemini_models_found"]:
            analysis["key_insights"].append(f"Kimi-K2 identified {len(analysis['gemini_models_found'])} Gemini model references")
            analysis["key_insights"].append("Using advanced 1T parameter MoE model for comprehensive analysis")
        else:
            analysis["key_insights"].append("No specific Gemini model information found in Kimi-K2 response")
        
        # Generate recommendations
        analysis["recommendations"].append("Kimi-K2 provides cutting-edge AI analysis capabilities")
        analysis["recommendations"].append("Consider using tool calling for real-time web search integration")
        analysis["recommendations"].append("Leverage Kimi-K2's agentic capabilities for autonomous research")
        
        return analysis

    def save_results(self, search_result: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Save search results and analysis to file"""
        
        results_data = {
            "search_result": search_result,
            "analysis": analysis,
            "metadata": {
                "timestamp": self.timestamp,
                "search_method": "Kimi-K2 API",
                "model_used": search_result.get("model_used", "kimi-k2-instruct")
            }
        }
        
        filename = f"{self.results_dir}/kimi_k2_gemini_search_{self.timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Results saved to {filename}")
        return filename

    def run(self, query: str = "latest Gemini models 2025 Google AI", use_tools: bool = False) -> str:
        """Execute the full Kimi-K2 search workflow"""
        
        try:
            logging.info(f"Starting Kimi-K2 search for query: {query}")
            
            # Perform search
            if use_tools:
                search_result = self.search_with_tools(query)
            else:
                search_result = self.search_gemini_models(query)
            
            if not search_result.get("success"):
                logging.error(f"Search failed: {search_result.get('error', 'Unknown error')}")
                return None
            
            # Analyze results
            analysis = self.analyze_results(search_result)
            
            # Save results
            results_file = self.save_results(search_result, analysis)
            
            # Print summary
            print("\n" + "="*60)
            print("KIMI-K2 GEMINI MODEL SEARCH RESULTS")
            print("="*60)
            print(f"Query: {query}")
            print(f"Model Used: {search_result.get('model_used', 'Unknown')}")
            print(f"Tokens Used: {search_result.get('tokens_used', 0)}")
            print(f"Tools Used: {search_result.get('tools_used', False)}")
            print(f"Results saved to: {results_file}")
            
            if analysis.get('gemini_models_found'):
                print(f"\nGEMINI MODELS DETECTED: {len(analysis['gemini_models_found'])}")
                for model in analysis['gemini_models_found']:
                    print(f"• {model['keyword']}")
            
            print(f"\nKIMI-K2 RESPONSE PREVIEW:")
            content = search_result.get("content", "")
            preview = content[:500] + "..." if len(content) > 500 else content
            print(preview)
            
            print("\nKEY INSIGHTS:")
            for insight in analysis.get('key_insights', []):
                print(f"• {insight}")
            
            print("\nRECOMMENDATIONS:")
            for rec in analysis.get('recommendations', []):
                print(f"• {rec}")
            
            print("="*60)
            
            return results_file
            
        except Exception as e:
            logging.error(f"Kimi-K2 search workflow failed: {str(e)}")
            raise

def main():
    """Main execution function"""
    
    # Check for API key
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        print("❌ MOONSHOT_API_KEY environment variable not set")
        print("Please set your Moonshot AI API key:")
        print("export MOONSHOT_API_KEY='your_api_key_here'")
        print("\nYou can get an API key from: https://platform.moonshot.ai")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "latest Gemini models 2025 Google AI"
    
    use_tools = "--tools" in sys.argv
    if use_tools:
        sys.argv.remove("--tools")
        query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else query
    
    searcher = KimiK2Search(api_key=api_key)
    
    try:
        results_file = searcher.run(query, use_tools=use_tools)
        if results_file:
            print(f"\n✅ Kimi-K2 search completed successfully!")
            print(f"📁 Results saved to: {results_file}")
        else:
            print(f"\n❌ Search failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Search failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 