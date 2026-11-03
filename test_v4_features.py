"""
KhelBot V4 Manual Integration Test Script.
Runs live integration queries across DuckDuckGo web search and Groq Llama 3.3.
Run via: python test_v4_features.py
"""

import asyncio
import os
import sys

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.web_search import search_web
from services.gemini import (
    generate_funfact,
    generate_freeform_answer,
    generate_match_recap
)


async def run_integration_tests():
    print("🚀 Starting KhelBot V4 Feature Tests...\n")

    print("--- 1. Testing Web Search (DuckDuckGo with Cache) ---")
    query = "RCB vs CSK IPL pitch report weather today"
    print(f"Searching for: '{query}'")
    search_result = await search_web(query)
    print("Search Result Preview (First 200 chars):")
    print(f"{search_result[:200]}...\n")

    print("--- 2. Testing /funfact (Web Search + AI) ---")
    topic = "cricket world record broken 2026"
    live_context = await search_web(topic)
    fact = await generate_funfact(live_context=live_context)
    print("Generated Fact:")
    print(fact)
    print("-" * 50 + "\n")

    print("--- 3. Testing /roast (Web Search + AI) ---")
    target = "RCB"
    print(f"Generating roast for: {target}")
    live_context = await search_web(f"{target} cricket recent worst performance troll news")
    prompt = f"Roast this cricket team or player: {target}\n\n--- LIVE WEB SEARCH DATA ---\n{live_context}\n--- END ---\nYOUR TASK: Write a savage, funny roast in Hinglish using the search data."
    roast = await generate_freeform_answer(prompt, live_context=live_context)
    print("Generated Roast:")
    print(roast)
    print("-" * 50 + "\n")

    print("--- 4. Testing /today (Web Search + AI) ---")
    print("Generating today's match list...")
    live_context = await search_web("IPL 2026 today match schedule cricket")
    prompt = f"Show me all cricket matches happening TODAY. Use this web data: {live_context}\nFormat as a quick Hinglish list."
    today_matches = await generate_freeform_answer(prompt, live_context=live_context)
    print("Generated Today Matches:")
    print(today_matches)
    print("-" * 50 + "\n")
    
    print("--- 5. Testing /pitch (Web Search + AI) ---")
    target_match = "CSK vs MI"
    print(f"Generating pitch report for: {target_match}")
    live_context = await search_web(f"{target_match} today match pitch report weather conditions toss prediction")
    prompt = f"Give a detailed Pitch and Weather Report for {target_match} based on this data: {live_context}\nHinglish mein bolo."
    pitch = await generate_freeform_answer(prompt, live_context=live_context)
    print("Generated Pitch Report:")
    print(pitch)
    print("-" * 50 + "\n")

    print("✅ All tests complete!")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
