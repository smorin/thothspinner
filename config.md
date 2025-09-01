# Spinner Element Nomenclature

## TL;DR - Configurable Elements:
- **spinner** (animated character), **message** (status text), **hint** (help text), **timer** (elapsed time), **progress** (completion counter)
- **Element styling**: individual colors, visibility, display order, formats
- **Timing**: animation speed, message changes, completion display duration
- **States**: success/error indicators, messages, and behaviors
- **Word lists**: customizable action words with add/replace options
- **Effects**: shimmer, fadeout animations

---

## Visual Structure: [spinner] [message]... [hint] [timer] [progress]

1. **spinner** - The animated character(s) at the beginning
   - Examples: ✻, ⠋, ·
   - Alternative names: indicator, icon, glyph, symbol

2. **message** - The text that comes after the spinner
   - Examples: "Photosynthesizing", "Installing packages"
   - Alternative names: label, text, action_text, status_text

3. **hint** - The fixed text after the animated message
   - Examples: "(esc to interrupt)", "(press q to quit)"
   - Alternative names: suffix, tail, append_text, help_text

4. **timer** - The running time display
   - Examples: "3.2s", "1:23", "2:14:35.123"
   - Alternative names: elapsed, duration_display, time_counter, elapsed_time

5. **progress** - The progress/completion display
   - Examples: "3/10", "45%", "7 of 15"
   - Alternative names: counter, progress_display, completion_counter

## Timing Elements:

6. **interval** - Time between animation frames in seconds
   - Examples: 0.1 (100ms), 0.08 (80ms)
   - Alternative names: frame_delay, tick_rate, refresh_rate

7. **duration** - Total runtime in seconds (if not infinite)
   - Examples: 5.0, 10.0
   - Alternative names: timeout, runtime, lifespan

8. **message_interval** - Time between message changes in seconds
   - Examples: 1.0, random between 0.5-3.0
   - Alternative names: word_change_delay, text_rotation_interval

## Layout & Display Elements:

9. **defaults** - Default configuration inherited by all elements
   - Examples: {"visible": true, "color": "#FFFFFF"}
   - Alternative names: default_config, base_settings

10. **elements** - Array defining element configuration, order, visibility, and styling
    - **Full Object Syntax**:
      ```json
      {"type": "spinner", "visible": true, "color": "#5555FF", "character": "✻"}
      {"type": "timer", "visible": false, "color": "#FFFF55", "format": {"style": "auto", "precision": 1}}
      {"type": "progress", "visible": true, "color": "#55FF55", "format": {"style": "fraction"}}
      ```
    - **Shorthand String Syntax** (uses defaults): `"spinner"`, `"message"`, `"timer"`
    - **Mixed Array Example**: `["spinner", "message", {"type": "timer", "format": {"style": "mm:ss"}}]`
    - Alternative names: element_config, display_elements

11. **column_layout** - Whether to display elements in a column format
    - Examples: true, false, {"enabled": true, "separator": "\n"}
    - Alternative names: vertical_layout, stacked_display

## Word List Configuration:

12. **action_words** - Configurable word lists for rotating messages
    - **Array syntax**: Simple list of words `["Loading", "Processing", "Working"]`
    - **Object syntax with mode**:
      - **replace mode**: `{"mode": "replace", "words": ["Custom", "Words", "Only"]}`
      - **add mode**: `{"mode": "add", "words": ["Extra", "More"]}`
    - Examples:
      ```json
      "action_words": ["Thinking", "Computing", "Processing"]
      "action_words": {"mode": "add", "words": ["Dreaming", "Pondering"]}
      "action_words": {"mode": "replace", "words": ["Custom", "Only"]}
      ```
    - Alternative names: word_list, message_words, rotating_text

## Format Specifications:

13. **timer_format** - Object specification for timer display format
    - Properties:
      - **style**: Format style options
        - "seconds" - "3s", "45s", "123s"
        - "seconds_decimal" - "3.2s", "45.7s", "123.4s"
        - "seconds_precise" - "3.245s", "45.789s"
        - "mm:ss" - "01:23", "05:43"
        - "hh:mm:ss" - "0:01:23", "2:14:35"
        - "auto" - "3s" → "1:23" → "2:14:35" (changes based on duration)
        - "auto_ms" - Like auto with decimals under 10 seconds
        - "compact" - "3s", "1:23", "2:14:35" (no leading zeros)
        - "milliseconds" - "3245ms", "45789ms"
        - "full_ms" - "1:23.456", "2:14:35.789"
      - **precision**: Decimal places for seconds (0-3)
      - **show_ms**: Include milliseconds (true/false)
    - Examples: `{"style": "auto", "precision": 1}`, `{"style": "mm:ss"}`
    - Alternative names: time_display_format, duration_format

14. **progress_format** - Object specification for progress display format
    - Properties:
      - **style**: Format style options
        - "fraction" - "3/10", "15/100"
        - "percentage" - "30%", "75%"
        - "of_text" - "3 of 10", "15 of 100"
        - "count_only" - "3", "15"
        - "ratio" - "3:10", "15:100"
      - **show_total**: Whether to display total count (true/false)
      - **zero_pad**: Pad numbers with zeros (true/false)
    - Examples: `{"style": "fraction"}`, `{"style": "percentage", "zero_pad": true}`
    - Alternative names: counter_format, progress_display_format

## State Configurations:

15. **states** - Configuration for completion and error states
    - **completion** - Settings for successful completion
      - **type**: What happens when spinner completes
        - "disappear" - Entire spinner vanishes immediately
        - "indicator" - Shows only done indicator, other elements disappear
        - "message" - Shows only done message, other elements disappear
        - "both" - Shows indicator + message, other elements disappear
        - "none" - Animation stops, current state remains visible
      - **indicator**: Character to display (replaces spinner)
      - **message**: Text to display on completion
      - **duration**: Display duration in seconds (null = permanent)
      - **color**: Color for completion elements
    - **error** - Settings for failed completion
      - **indicator**: Character to display (replaces spinner)
      - **message**: Text to display on error
      - **duration**: Display duration in seconds (null = permanent)
      - **color**: Color for error elements
    - Alternative names: completion_config, state_management

16. **animate_away_interval** - Time between each letter removal during done message fadeout
    - Examples: 0.1, 0.05 (defaults to same as interval)
    - Alternative names: fadeout_delay, removal_interval

**Note**: The JSON examples below are for illustration purposes only. The final design may use JSON, TOML, YAML, or other configuration formats.

So a full config might look like:
```json
{
    "spinner": "✻",
    "message": "Processing",
    "hint": "(esc to interrupt)",
    "interval": 0.1,
    "duration": null,
    "message_interval": 1.0,
    "defaults": {
        "visible": true,
        "color": "#FFFFFF"
    },
    "elements": [
        {"type": "spinner", "color": "#5555FF", "character": "✻"},
        "message",
        {"type": "progress", "color": "#55FF55", "format": {"style": "fraction"}},
        {"type": "timer", "visible": false, "color": "#FFFF55", "format": {"style": "auto", "precision": 1}},
        {"type": "hint", "color": "#888888"}
    ],
    "column_layout": false,
    "action_words": {"mode": "add", "words": ["Contemplating", "Analyzing"]},
    "states": {
        "completion": {
            "type": "both",
            "indicator": "✅",
            "message": "Complete!",
            "duration": 2.0,
            "color": "#55FF55"
        },
        "error": {
            "indicator": "❌",
            "message": "Failed!",
            "duration": 3.0,
            "color": "#FF5555"
        }
    },
    "animate_away_interval": 0.1
}
```

## Simplified Shorthand Example:
```json
{
    "spinner": "⠋",
    "message": "Loading",
    "interval": 0.08,
    "defaults": {"visible": true, "color": "#00FF00"},
    "elements": ["spinner", "message", "timer"],
    "action_words": ["Thinking", "Working", "Processing"],
    "states": {
        "completion": {"type": "indicator", "indicator": "✓", "duration": 1.0}
    }
}
```

## Essential Elements:
- frames (character sequence)
- interval (animation speed)
- defaults (inherited element configuration)
- elements (consolidated element configuration with order, visibility, colors, and formats)
- states (unified completion and error configuration)
- action_words (customizable word lists with add/replace modes)
- animate_away_interval (fadeout timing)
- shimmer_type & shimmer_width
