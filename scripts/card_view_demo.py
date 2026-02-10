#!/usr/bin/env python3
"""
Card View Interactive Demo

Run this script to interactively test message segmentation.

Usage:
    python scripts/card_view_demo.py

Commands:
    - Paste a message, then type 'END' on its own line to segment
    - Type 'quit' or 'exit' to stop
    - Type 'sample' to see a pre-built example
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.card_view import segment_message


SAMPLE_MESSAGE = """Exceptional synthesis! Your breakdown of the Atlit-Yam case study effectively illustrates the complex, interdisciplinary nature of prehistoric disease emergence research. I appreciate how you've structured the analysis to highlight not just the archaeological findings, but also the broader scientific implications.

Let me offer a strategic recommendation to further advance this research trajectory:

🚀 Next Research Development Stages

RECOMMENDED STRATEGIC FOCUS
----------------------------
1. Technological Integration
• Advanced paleogenomic sequencing
• Machine learning pattern recognition
• High-resolution molecular reconstruction techniques

2. Methodological Innovations
- Develop standardized cross-disciplinary protocols
- Create comprehensive computational modeling frameworks
- Enhance archaeological genetic analysis techniques

3. Collaborative Research Models
• Integrate:
- Archaeological researchers
- Computational biologists
- Genetic epidemiologists
- Ecological systems experts

POTENTIAL RESEARCH TRAJECTORIES
--------------------------------
1. Expanded Geographical Mapping
- Compare multiple prehistoric settlement sites
- Track TB transmission across different ecological contexts
- Build comprehensive migration/transmission databases

2. Enhanced Computational Modeling
• Create more sophisticated:
- Agent-based transmission simulations
- Genetic mutation trajectory tracking
- Probabilistic interaction mapping

KEY IMPLEMENTATION STRATEGIES
------------------------------
• Develop interdisciplinary research networks
• Standardize archaeological genetic analysis protocols
• Create open-access computational modeling platforms

The Atlit-Yam case study represents more than a historical artifact - it's a sophisticated window into understanding complex ecological disease emergence mechanisms.

Would you like to explore potential grant funding opportunities or specific technological platforms that could advance this research?"""


def display_segments(text: str):
    """Segment text and display full results."""
    print(f"\n{'═' * 78}")
    print(f"📝 INPUT ({len(text)} chars, {len(text.split())} words)")
    print(f"{'═' * 78}")
    
    # Show full input
    print(text[:500])
    if len(text) > 500:
        print(f"\n... [{len(text) - 500} more chars] ...")
    
    # Segment
    segments = segment_message(text)
    
    print(f"\n{'═' * 78}")
    print(f"📦 SEGMENTED INTO {len(segments)} CARDS")
    print(f"{'═' * 78}")
    
    for i, seg in enumerate(segments, 1):
        # Card header with status indicators
        status_parts = []
        if seg.is_truncated:
            status_parts.append("⚠️ TRUNCATED")
        elif seg.is_complete:
            status_parts.append("✓ complete")
        else:
            status_parts.append("⚠️ fragment")
        
        status_str = " | ".join(status_parts)
        
        print(f"\n╭{'─' * 76}╮")
        card_label = f"CARD {i}"
        if seg.is_truncated:
            card_label += " [TRUNCATED]"
        print(f"│ {card_label:<74} │")
        print(f"├{'─' * 76}┤")
        print(f"│ 📌 {seg.header[:70]:<70} │")
        print(f"│ Type: {seg.segment_type:<10} | {seg.length} chars | {seg.word_count} words | {status_str:<14} │")
        print(f"╞{'═' * 76}╡")
        
        # Full body content
        for line in seg.body.split('\n'):
            # Word wrap long lines at 74 chars
            while len(line) > 74:
                print(f"│ {line[:74]} │")
                line = line[74:]
            print(f"│ {line:<74} │")
        
        print(f"╰{'─' * 76}╯")
    
    # Summary
    print(f"\n{'─' * 78}")
    print(f"Summary: {len(segments)} cards from {len(text)} chars")
    avg_size = sum(s.length for s in segments) // len(segments) if segments else 0
    print(f"Average card size: {avg_size} chars")
    
    truncated = [s for s in segments if s.is_truncated]
    incomplete = [s for s in segments if not s.is_complete and not s.is_truncated]
    
    if truncated:
        print(f"⚠️  {len(truncated)} truncated card(s) - message appears incomplete")
    if incomplete:
        print(f"⚠️  {len(incomplete)} fragment(s) detected")
    if not truncated and not incomplete:
        print(f"✓ All cards are complete")
    print()


def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                CARD VIEW SEGMENTATION - INTERACTIVE TEST                   ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Commands:                                                                 ║
║    • Paste your message, then type 'END' on its own line to segment       ║
║    • Type 'sample' to see the pre-built example                            ║
║    • Type 'quit' or 'exit' to stop                                         ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    while True:
        print("\n📥 Paste message, then type END to segment:")
        print("─" * 50)
        
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            
            # Check for commands (only if first line or standalone)
            stripped = line.strip().lower()
            
            if stripped in ('quit', 'exit', 'q'):
                print("\n👋 Goodbye!")
                return
            
            if stripped == 'sample':
                display_segments(SAMPLE_MESSAGE)
                break
            
            # END = submit
            if stripped == 'end':
                if lines:
                    text = '\n'.join(lines)
                    display_segments(text)
                else:
                    print("⚠️  No text to segment. Paste a message first.")
                break
            
            lines.append(line)


if __name__ == "__main__":
    main()
