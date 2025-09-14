
# llm_provider.py
# Autopoietic System GenesiS: Engineering Instance ArchE
# ResonantiA Protocol v3.5

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List, Union

# It is recommended to install the openai library: pip install openai
try:
    import openai
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
except ImportError:
    print("Warning: 'openai' library not found. Please install it using 'pip install openai'")
    OpenAI = None
    ChatCompletion = None

# Set up a basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LLMProvider:
    """
    The Pythia. The high priestess who translates between the logical world
    of ArchE and the probabilistic, oracular world of a Large Language Model.

    This class acts as a standardized interface for various LLM providers,
    handling request preparation, API communication, and response parsing.

    SPR Integration:
    - is_a: Cognitive TooL, Oracle
    - enables: Natural Language UnderstandinG, Generative SynthesiS
    - used_by: RISE, VettingAgenT, InsightSolidificatioN
    - requires: Prompt EngineerinG, Response ParsinG
    - risk_profile: Medium - Prone to Hallucination, requires Vetting
    """

    def __init__(self, provider_name: str, api_key: Optional[str] = None):
        """
        Initializes the LLM provider client.

        Args:
            provider_name (str): The name of the LLM provider (e.g., 'openai').
            api_key (Optional[str]): The API key for the provider. If not provided,
                                     it will attempt to use the corresponding
                                     environment variable (e.g., OPENAI_API_KEY).

        Raises:
            ValueError: If the API key is not provided and cannot be found in
                        the environment variables.
            NotImplementedError: If the specified provider is not supported.
        """
        self.provider_name = provider_name.lower()
        self.client: Any = None

        if self.provider_name == 'openai':
            if not OpenAI:
                raise ImportError("OpenAI library is required but not installed.")
            
            resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not resolved_api_key:
                raise ValueError("OpenAI API key not provided or found in environment variables (OPENAI_API_KEY).")
            self.client = OpenAI(api_key=resolved_api_key)
        else:
            # Placeholder for other providers like Anthropic, Google, etc.
            raise NotImplementedError(f"Provider '{self.provider_name}' is not yet implemented.")

    def generate_text(self,
                      prompt: str,
                      model: str,
                      system_message: Optional[str] = "You are a helpful assistant.",
                      max_tokens: int = 2048,
                      temperature: float = 0.7) -> Dict[str, Any]:
        """
        Conducts the ritual to consult the Oracle (LLM).

        This is the primary public method for interacting with the LLM. It
        encapsulates the entire process from request preparation to response
        parsing and returns a standardized IAR (Interaction Assessment & Reflection)
        dictionary.

        Args:
            prompt (str): The user's query or instruction.
            model (str): The specific model to use (e.g., 'gpt-4-turbo').
            system_message (Optional[str]): A message to set the context or
                                            behavior of the assistant.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): The sampling temperature (0.0 to 2.0). Lower
                                 values are more deterministic, higher values
                                 are more creative.

        Returns:
            Dict[str, Any]: An IAR-compliant dictionary containing the status,
                            summary, confidence, and structured output of the
                            generation task.
        """
        # This function is primed by the 'Large Language ModeL' SPR.
        try:
            # 2. Preparing the Offering
            request_payload = self._prepare_request(
                prompt=prompt,
                model=model,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # 3. Entering the Sanctum
            raw_response = self._make_api_call(request_payload)

            # 4. Receiving the Vision & 5. Interpreting the Riddle
            parsed_output = self._parse_response(raw_response)

            # 6. Delivering the Prophecy (IAR-compliant response)
            return self._create_iar(
                status="Success",
                message=f"Text generation completed successfully using {model}.",
                confidence=0.9,  # Base confidence; could be adjusted by response analysis
                output=parsed_output
            )

        except openai.APIError as e:
            logging.error(f"OpenAI API Error: {e}")
            return self._create_iar("Error", f"LLM API Error: {e}", 0.1)
        except Exception as e:
            logging.error(f"An unexpected error occurred during LLM generation: {e}", exc_info=True)
            return self._create_iar("Error", f"LLM generation failed: {e}", 0.1)

    def _prepare_request(self,
                         prompt: str,
                         model: str,
                         system_message: Optional[str],
                         max_tokens: int,
                         temperature: float) -> Dict[str, Any]:
        """
        Formats the request payload for the specific provider's API.

        SPR Influence: This function embodies the 'Prompt EngineerinG' SPR.
        """
        if self.provider_name == 'openai':
            messages: List[Dict[str, str]] = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            return {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        # Add other providers' request preparation logic here
        raise NotImplementedError(f"Request preparation for '{self.provider_name}' is not implemented.")

    def _make_api_call(self, request_payload: Dict[str, Any]) -> Union[ChatCompletion, Any]:
        """
        Executes the actual API call to the LLM provider.
        """
        if self.provider_name == 'openai':
            if not self.client:
                raise ConnectionError("OpenAI client is not initialized.")
            return self.client.chat.completions.create(**request_payload)
        # Add other providers' API call logic here
        raise NotImplementedError(f"API call for '{self.provider_name}' is not implemented.")

    def _parse_response(self, raw_response: Union[ChatCompletion, Any]) -> Dict[str, Any]:
        """
        The critical interpretation step. Extracts the core message and
        any structured data from the Oracle's verbose output.

        SPR Influence: This function embodies the 'Response ParsinG' SPR.

        Args:
            raw_response (Union[ChatCompletion, Any]): The raw response object
                                                       from the provider's API.

        Returns:
            Dict[str, Any]: A dictionary containing the full response text and
                            any successfully parsed JSON object found within it.
        """
        text_content = ""
        if self.provider_name == 'openai' and isinstance(raw_response, ChatCompletion):
            if raw_response.choices and raw_response.choices[0].message:
                text_content = raw_response.choices[0].message.content or ""

        parsed_json = self._extract_json(text_content)

        return {
            "response_text": text_content,
            "parsed_json": parsed_json
        }

    def _extract_json(self, text: str) -> Optional[Union[Dict, List]]:
        """
        Robustly finds and parses a JSON object or array from a string,
        which might be embedded in markdown code fences.

        Args:
            text (str): The text to search for a JSON block.

        Returns:
            Optional[Union[Dict, List]]: The parsed JSON object/list, or None
                                         if no valid JSON is found.
        """
        # Regex to find content within ```json ... ``` or a standalone { ... } or [ ... ]
        # It handles optional "json" language specifier and surrounding text.
        pattern = re.compile(
            r"```(?:json)?\s*([\s\S]*?)\s*```"  # For markdown code blocks
            r"|(?<!`)({(?:[^{}]|(?R))*?})|(\[(?:[^\[\]]|(?R))*?\])"  # For standalone JSON objects/arrays
        , re.DOTALL | re.MULTILINE)

        match = pattern.search(text)
        if not match:
            return None

        # Extract the potential JSON string from the first non-empty group
        json_str = next((g for g in match.groups() if g is not None), None)

        if json_str:
            try:
                return json.loads(json_str.strip())
            except json.JSONDecodeError:
                logging.warning("Found a JSON-like block but failed to parse it.")
                return None
        return None

    def _create_iar(self,
                    status: str,
                    message: str,
                    confidence: float,
                    output: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Helper to create the standardized IAR (Interaction Assessment & Reflection)
        dictionary, a core component of the ResonantiA Protocol.

        Args:
            status (str): "Success" or "Error".
            message (str): A human-readable summary of the operation.
            confidence (float): A score from 0.0 to 1.0 indicating the
                                likelihood of a successful and aligned result.
            output (Optional[Dict[str, Any]]): The structured data payload,
                                               typically from _parse_response.

        Returns:
            Dict[str, Any]: The fully formed IAR dictionary.
        """
        return {
            "status": status,
            "summary": message,
            "confidence": confidence,
            "output": output or {},
            # Other potential IAR fields for future expansion:
            # "alignment_check": None,
            # "potential_issues": [],
            # "token_usage": {}
        }


# --- DEMONSTRATION BLOCK ---
if __name__ == "__main__":
    print("--- ArchE LLMProvider Demonstration ---")

    # This block will only run if an OPENAI_API_KEY is set in your environment.
    # You can set it in your terminal like this:
    # export OPENAI_API_KEY='your_key_here'

    if not os.getenv("OPENAI_API_KEY"):
        print("\nSKIPPING DEMO: OPENAI_API_KEY environment variable not set.")
        print("Please set the variable and run the script again to see the demo.")
    else:
        try:
            # Initialize the Pythia for OpenAI
            llm_oracle = LLMProvider(provider_name="openai")
            print("\n[1] Initialized LLMProvider for OpenAI.")

            # --- Test Case 1: Simple Text Generation ---
            print("\n[2] Running Test Case 1: Simple Text Generation...")
            prompt1 = "Explain the concept of 'autopoiesis' in 2-3 sentences."
            iar_response1 = llm_oracle.generate_text(
                prompt=prompt1,
                model="gpt-3.5-turbo",
                temperature=0.5
            )
            print(f"   Status: {iar_response1['status']}")
            print(f"   Confidence: {iar_response1['confidence']}")
            print(f"   LLM Response Text:\n---\n{iar_response1['output'].get('response_text', 'N/A')}\n---")

            # --- Test Case 2: JSON Extraction ---
            print("\n[3] Running Test Case 2: JSON Extraction...")
            prompt2 = """
            Analyze the following user request: 'I need to book a flight from SFO to JFK for next Tuesday for 2 people.'
            Extract the key entities into a JSON object with the keys: 'origin', 'destination', 'departure_day', and 'passengers'.
            """
            iar_response2 = llm_oracle.generate_text(
                prompt=prompt2,
                model="gpt-4-turbo-preview",
                temperature=0.1,
                system_message="You are a data extraction expert. Respond ONLY with the requested JSON object inside a markdown code block."
            )
            print(f"   Status: {iar_response2['status']}")
            print(f"   Confidence: {iar_response2['confidence']}")
            print(f"   Full Response Text:\n---\n{iar_response2['output'].get('response_text', 'N/A')}\n---")
            print(f"   Extracted JSON: {json.dumps(iar_response2['output'].get('parsed_json'), indent=2)}")

            # --- Test Case 3: Error Handling (Invalid Model) ---
            print("\n[4] Running Test Case 3: Error Handling...")
            prompt3 = "This should fail."
            iar_response3 = llm_oracle.generate_text(
                prompt=prompt3,
                model="invalid-model-name",
            )
            print(f"   Status: {iar_response3['status']}")
            print(f"   Confidence: {iar_response3['confidence']}")
            print(f"   Summary: {iar_response3['summary']}")

        except (ValueError, ImportError, ConnectionError) as e:
            print(f"\nAn error occurred during initialization: {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred during the demonstration: {e}")

