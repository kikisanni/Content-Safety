import ollama
import json
import re



def classify_content(text):
    """
    Classify text for safety issues using local Ollama LLM.
    Completely free - runs on your machine!
    """
    
    prompt = f"""You are a content safety classifier for a social media platform.

Analyze this text and classify it for safety issues:

Categories:
1. hate_speech: Attacks on people based on race, religion, gender, etc.
2. spam: Unsolicited commercial content or scams
3. misinformation: Provably false claims presented as fact
4. harassment: Targeted abuse or threats toward individuals

Important:
- Political criticism is NOT hate speech
- Profanity alone is not a violation
- Consider context and intent

Text to analyze: "{text}"

You MUST return ONLY valid JSON with this EXACT structure (no extra text before or after):
{{
    "hate_speech": {{"detected": false, "confidence": 0.0, "reason": "explanation"}},
    "spam": {{"detected": false, "confidence": 0.0, "reason": "explanation"}},
    "misinformation": {{"detected": false, "confidence": 0.0, "reason": "explanation"}},
    "harassment": {{"detected": false, "confidence": 0.0, "reason": "explanation"}}
}}

Return the JSON now:"""

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.1,
                'num_predict': 600,  # Increased from 500 to avoid cutoffs
            }
        )
        
        response_text = response['message']['content'].strip()
        
        # Remove any markdown code blocks
        response_text = response_text.replace('```json', '').replace('```', '')
        
        # Find JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        # Fix common JSON issues
        # Ensure proper closing braces
        open_braces = response_text.count('{')
        close_braces = response_text.count('}')
        if open_braces > close_braces:
            response_text += '}' * (open_braces - close_braces)
        
        # Try to parse
        result = json.loads(response_text)
        
        # Validate structure - ensure all required keys exist
        required_keys = ['hate_speech', 'spam', 'misinformation', 'harassment']
        for key in required_keys:
            if key not in result:
                result[key] = {
                    "detected": False,
                    "confidence": 0.0,
                    "reason": "Error: category not classified"
                }
            # Ensure each category has required fields
            if 'detected' not in result[key]:
                result[key]['detected'] = False
            if 'confidence' not in result[key]:
                result[key]['confidence'] = 0.0
            if 'reason' not in result[key]:
                result[key]['reason'] = "No reason provided"
        
        # Add metadata
        result['metadata'] = {
            'model': 'llama3.2-local',
            'cost_estimate': 0.0,
            'eval_count': response.get('eval_count', 0),
            'deployment': 'local'
        }
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response_text[:500]}...")  # Show first 500 chars
        
        # Return a safe fallback result
        return {
            "hate_speech": {"detected": False, "confidence": 0.0, "reason": "JSON parse error"},
            "spam": {"detected": False, "confidence": 0.0, "reason": "JSON parse error"},
            "misinformation": {"detected": False, "confidence": 0.0, "reason": "JSON parse error"},
            "harassment": {"detected": False, "confidence": 0.0, "reason": "JSON parse error"},
            "metadata": {
                'model': 'llama3.2-local-error',
                'cost_estimate': 0.0,
                'eval_count': 0,
                'deployment': 'local',
                'error': str(e)
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "I think pineapple on pizza is delicious!",
        "All people from [country] are criminals and should be deported",
        "CLICK HERE NOW!!! FREE IPHONE 15!!! LIMITED TIME OFFER!!!",
        "The Earth is flat and NASA has been lying to everyone",
        "You're a worthless idiot and I hope you die",
        "I strongly disagree with the Senator's policies",
        "This damn traffic is frustrating!",
        "Someone said 'all [group] are bad' which is unacceptable",
    ]
    
    print("="*100)
    print("OLLAMA CONTENT SAFETY CLASSIFICATION TEST (100% FREE & LOCAL)")
    print("="*100)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"Test {i}/{len(test_cases)}")
        print(f"{'='*100}")
        print(f"Text: {text}")
        print("-"*100)
        
        result = classify_content(text)
        
        if result:
            print("\nClassifications:")
            for category, data in result.items():
                if category != 'metadata':
                    detected = "DETECTED" if data['detected'] else "Safe"
                    print(f"  {category:20s} {detected:15s} Confidence: {data['confidence']:.2f}")
                    print(f"  Reason: {data['reason']}")
                    print()
            
            print(f"Model: {result['metadata']['model']}")
            print(f"Cost: ${result['metadata']['cost_estimate']:.6f} (FREE!)")
            print(f"Tokens: {result['metadata']['eval_count']}")
        else:
            print("Classification failed")
    
    print(f"\n{'='*100}")
    print("TOTAL COST: $0.00 (Runs on your machine!)")
    print(f"{'='*100}")