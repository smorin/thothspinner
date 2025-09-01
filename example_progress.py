#!/usr/bin/env python3
"""
Standalone progress spinner script with NPM and Claude effects
Both spinners feature random action words, shimmer effects, and consistent styling
"""

import sys
import time
import random
import signal

# ANSI escape codes
class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Claude Brand Colors
    ORANGE = "\033[38;5;209m"       # Claude Orange Main
    ORANGE_LIGHT = "\033[38;5;216m" # Claude Orange Light for shimmer
    GRAY = "\033[38;5;245m"         # Gray for suffix text
    
    # Terminal control
    CLEAR_LINE = "\033[2K"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"

# All 87 action words from Claude CLI
ACTION_WORDS = [
    "Accomplishing", "Actioning", "Actualizing", "Baking", "Booping",
    "Brewing", "Calculating", "Cerebrating", "Channelling", "Churning",
    "Clauding", "Coalescing", "Cogitating", "Computing", "Combobulating",
    "Concocting", "Conjuring", "Considering", "Contemplating", "Cooking",
    "Crafting", "Creating", "Crunching", "Decoding", "Decrypting",
    "Deliberating", "Digesting", "Digitalizing", "Discovering", "Divining",
    "Dreaming", "Elucidating", "Encoding", "Engineering", "Envisioning",
    "Evaluating", "Evolving", "Examining", "Executing", "Exploring",
    "Fabricating", "Factoring", "Figuring", "Formulating", "Generating",
    "Grinding", "Hatching", "Ideating", "Imagining", "Implementing",
    "Improvising", "Innovating", "Integrating", "Interpreting", "Investigating",
    "Iterating", "Learning", "Manifesting", "Mapping", "Modeling",
    "Musing", "Noodling", "Orchestrating", "Organizing", "Perceiving",
    "Percolating", "Pondering", "Postulating", "Processing", "Prototyping",
    "Puzzling", "Reasoning", "Refining", "Reflecting", "Resolving",
    "Ruminating", "Scheming", "Sculpting", "Sketching", "Solving",
    "Spinning", "Structuring", "Synthesizing", "Thinking", "Transmuting",
    "Unfurling", "Unravelling", "Vibing", "Wandering", "Whirring",
    "Wibbling", "Wizarding", "Working", "Wrangling"
]

def npm_spinner(duration=10):
    """NPM-style dots spinner with action words and shimmer"""
    # NPM dots using Unicode braille patterns
    npm_dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    running = True
    start_time = time.time()
    frame_index = 0
    
    # Word change timing
    next_word_change = time.time() + random.uniform(0.5, 3.0)
    current_word = random.choice(ACTION_WORDS)
    
    # Shimmer settings
    shimmer_width = 3
    shimmer_position = -shimmer_width
    
    # Hide cursor
    sys.stdout.write(ANSI.HIDE_CURSOR)
    sys.stdout.flush()
    
    try:
        while running and (time.time() - start_time) < duration:
            # Change word at random intervals
            if time.time() >= next_word_change:
                current_word = random.choice(ACTION_WORDS)
                next_word_change = time.time() + random.uniform(0.5, 3.0)
                shimmer_position = -shimmer_width  # Reset shimmer
            
            # Get current dot frame
            dot = npm_dots[frame_index % len(npm_dots)]
            
            # Apply shimmer to word with dots
            full_text = current_word + "…"
            shimmered_text = ""
            for i, char in enumerate(full_text):
                if shimmer_position <= i < shimmer_position + shimmer_width:
                    shimmered_text += f"{ANSI.ORANGE_LIGHT}{char}{ANSI.RESET}{ANSI.ORANGE}"
                else:
                    shimmered_text += char
            
            # Display spinner
            sys.stdout.write(f"\r{ANSI.CLEAR_LINE}")
            sys.stdout.write(f"{ANSI.ORANGE}{dot} {shimmered_text}{ANSI.RESET} {ANSI.DIM}(esc to interrupt){ANSI.RESET}")
            sys.stdout.flush()
            
            # Update animation
            frame_index += 1
            shimmer_position += 1
            if shimmer_position > len(full_text):
                shimmer_position = -shimmer_width
            
            time.sleep(0.08)  # 80ms interval for NPM style
            
    finally:
        # Clear and show cursor
        sys.stdout.write(f"\r{ANSI.CLEAR_LINE}")
        sys.stdout.write(ANSI.SHOW_CURSOR)
        sys.stdout.flush()

def claude_spinner(duration=10):
    """Claude star spinner with action words and shimmer"""
    # Star animation frames
    stars = ["·", "✢", "✳", "✶", "✻", "✽"]
    star_frames = stars + list(reversed(stars))
    
    running = True
    start_time = time.time()
    frame_index = 0
    
    # Word change timing
    next_word_change = time.time() + random.uniform(0.5, 3.0)
    current_word = random.choice(ACTION_WORDS)
    
    # Shimmer settings
    shimmer_width = 3
    shimmer_position = -shimmer_width
    
    # Hide cursor
    sys.stdout.write(ANSI.HIDE_CURSOR)
    sys.stdout.flush()
    
    try:
        while running and (time.time() - start_time) < duration:
            # Change word at random intervals
            if time.time() >= next_word_change:
                current_word = random.choice(ACTION_WORDS)
                next_word_change = time.time() + random.uniform(0.5, 3.0)
                shimmer_position = -shimmer_width  # Reset shimmer
            
            # Get current star frame
            star = star_frames[frame_index % len(star_frames)]
            
            # Apply shimmer to word with dots
            full_text = current_word + "…"
            shimmered_text = ""
            for i, char in enumerate(full_text):
                if shimmer_position <= i < shimmer_position + shimmer_width:
                    shimmered_text += f"{ANSI.ORANGE_LIGHT}{char}{ANSI.RESET}{ANSI.ORANGE}"
                else:
                    shimmered_text += char
            
            # Display spinner
            sys.stdout.write(f"\r{ANSI.CLEAR_LINE}")
            sys.stdout.write(f"{ANSI.ORANGE}{star} {shimmered_text}{ANSI.RESET} {ANSI.DIM}(esc to interrupt){ANSI.RESET}")
            sys.stdout.flush()
            
            # Update animation
            frame_index += 1
            shimmer_position += 1
            if shimmer_position > len(full_text):
                shimmer_position = -shimmer_width
            
            time.sleep(0.1)  # 100ms interval for Claude style
            
    finally:
        # Clear and show cursor
        sys.stdout.write(f"\r{ANSI.CLEAR_LINE}")
        sys.stdout.write(ANSI.SHOW_CURSOR)
        sys.stdout.flush()

def show_help():
    """Display help message"""
    print("Usage: progress.py [npm|claude]")
    print()
    print("Displays an animated progress spinner with random action words")
    print()
    print("Options:")
    print("  npm     - NPM-style dots spinner with shimmer effect")
    print("  claude  - Claude-style star spinner with shimmer effect")
    print()
    print("Both spinners run for 10 seconds or until Ctrl+C is pressed")
    print("Features random action words and shimmer text effects")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    sys.stdout.write(f"\r{ANSI.CLEAR_LINE}")
    sys.stdout.write(ANSI.SHOW_CURSOR)
    sys.stdout.flush()
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check arguments
    if len(sys.argv) != 2:
        show_help()
        sys.exit(0)
    
    mode = sys.argv[1].lower()
    
    if mode == "npm":
        npm_spinner()
    elif mode == "claude":
        claude_spinner()
    else:
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()