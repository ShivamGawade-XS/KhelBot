import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini import generate_live_context

async def main():
    match_data = {
        "name": "Royal Challengers Bengaluru vs Gujarat Titans",
        "status": "Royal Challengers Bengaluru won by 5 wkts",
        "venue": "M.Chinnaswamy Stadium",
        "score": [
            {"inning": "Gujarat Titans", "r": 205, "w": 3, "o": 20},
            {"inning": "RCB", "r": 206, "w": 5, "o": 18.5}
        ]
    }
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Re-wrap to catch exception
    from services.gemini import _model, SYSTEM_PERSONALITY, _format_match_for_prompt
    
    prompt = f"""Analyze this LIVE cricket match and give exciting Hinglish commentary:

MATCH DATA:
{_format_match_for_prompt(match_data)}

YOUR TASK:
1. Summarize the current match situation in 2-3 lines
2. Analyze the momentum — kaun haavi hai? (who's dominating?)
3. Highlight key moments or turning points
4. Give your take — kya lagta hai aage kya hoga? (what do you think will happen?)

Remember: Be enthusiastic, use Hinglish, and keep it under 250 words!"""

    try:
        full_prompt = f"{SYSTEM_PERSONALITY}\n\n{prompt}"
        print("Calling Gemini...")
        response = await _model.generate_content_async(full_prompt)
        print("Response:", response.text)
    except Exception as e:
        print("EXCEPTION:", type(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
