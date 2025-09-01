# ThothSpinner - Product Requirements Document v1.0

## Executive Summary

ThothSpinner is a configurable progress bar component library for Python, compatible with Rich and Textual frameworks. It provides highly customizable animated progress indicators with multiple display elements that can be styled, ordered, and configured through a simple configuration system.

## Core Philosophy

Build components from simplest to most complex, with each component being independently testable and configurable. All visual components support color customization via hex codes and optional shimmer effects for enhanced visual appeal.

---

## Component Build Order & Requirements

### 1. Hint Component (Simplest)

**Purpose**: Display static helper text to guide users (e.g., "(esc to interrupt)")

**Requirements**:
- **Text Display**: Render static text string without modification
- **Color Support**: Accept hex color codes (e.g., #888888) and convert to ANSI escape codes
- **Visibility Control**: Can be shown or hidden via configuration
- **Position**: Typically appears after dynamic elements as suffix text
- **No Animation**: Static display only, no frame updates needed

**Configuration Options**:
```json
{
  "type": "hint",
  "text": "(esc to interrupt)",
  "visible": true,
  "color": "#888888"
}
```

**Test Requirements**:
- Verify text displays correctly
- Test hex color conversion to ANSI codes
- Validate visibility toggle works
- Ensure no memory leaks from static display

---

### 2. Spinner Component

**Purpose**: Display animated character that cycles through predefined frames

**Requirements**:
- **Frame Animation**: Cycle through array of characters (e.g., ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
- **Timing Control**: Configurable interval between frames (default 0.08s for NPM style, 0.1s for Claude style)
- **Color Support**: Accept hex color codes for spinner characters
- **Frame Sets**: Support multiple built-in frame sets:
  - NPM dots: Unicode braille patterns
  - Claude stars: ["·", "✢", "✳", "✶", "✻", "✽"] with reverse cycle
  - Custom: User-defined character arrays
- **State Transformation**: Can change to static icon on completion/error

**Configuration Options**:
```json
{
  "type": "spinner",
  "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
  "interval": 0.08,
  "color": "#D97706"
}
```

**Test Requirements**:
- Verify frame cycling at correct intervals
- Test custom frame arrays
- Ensure smooth animation without flicker
- Test interrupt handling (Ctrl+C)

---

### 3. Progress Component

**Purpose**: Display completion status as current/total counter

**Requirements**:
- **Value Tracking**: Maintain current and total values
- **Display Formats**:
  - `fraction`: "3/10", "45/100"
  - `percentage`: "30%", "45%"
  - `of_text`: "3 of 10", "45 of 100"
  - `count_only`: "3", "45"
  - `ratio`: "3:10", "45:100"
- **Zero Padding**: Optional padding with zeros (e.g., "03/10")
- **Color Support**: Hex color codes for progress text
- **State Changes**: Can change color or disappear on success/error
- **Update Methods**: Support increment, set, and percentage updates

**Configuration Options**:
```json
{
  "type": "progress",
  "current": 0,
  "total": 100,
  "format": {
    "style": "percentage",
    "zero_pad": false
  },
  "color": "#55FF55"
}
```

**Test Requirements**:
- Test all format styles with various values
- Verify zero padding works correctly
- Test boundary conditions (0%, 100%, overflow)
- Validate state change behaviors
- Test real-time updates during operation

---

### 4. Timer Component

**Purpose**: Display elapsed time in various formats

**Requirements**:
- **Time Tracking**: Accurate elapsed time from start
- **Display Formats**:
  - `seconds`: "3s", "45s"
  - `seconds_decimal`: "3.2s", "45.7s"
  - `seconds_precise`: "3.245s" (3 decimal places)
  - `mm:ss`: "01:23", "05:43"
  - `hh:mm:ss`: "0:01:23", "2:14:35"
  - `auto`: Changes format based on duration
    - < 60s: "3s"
    - < 1hr: "1:23"
    - >= 1hr: "2:14:35"
  - `auto_ms`: Like auto but with decimals under 10 seconds
  - `compact`: No leading zeros
  - `milliseconds`: "3245ms"
  - `full_ms`: "1:23.456"
- **Precision Control**: 0-3 decimal places for seconds
- **Color Support**: Hex color codes
- **State Changes**: Can stop counting, change color, or disappear on completion
- **Update Frequency**: Refresh based on precision needs

**Configuration Options**:
```json
{
  "type": "timer",
  "format": {
    "style": "auto",
    "precision": 1,
    "show_ms": false
  },
  "color": "#FFFF55"
}
```

**Test Requirements**:
- Test all format styles at different time ranges
- Verify precision settings work correctly
- Test format transitions in "auto" mode
- Validate timer accuracy over long periods
- Test pause/resume functionality

---

### 5. Message Component

**Purpose**: Display rotating action words with shimmer effects

**Requirements**:
- **Action Words System**:
  - Default set of 87 action words (from example_progress.py)
  - Words include: "Accomplishing", "Actualizing", "Baking", "Brewing", "Calculating", etc.
- **Word List Management**:
  - `replace` mode: Use only custom words
  - `add` mode: Append to default word list
  - Array syntax for simple replacement
  - Object syntax for mode control
- **Rotation Logic**:
  - Random selection from word pool
  - Configurable interval (0.5-3.0 seconds random by default)
  - Smooth transition between words
- **Shimmer Effect** (Primary Feature):
  - 3-character width light wave
  - **Direction Control**:
    - `left-to-right`: Default direction
    - `right-to-left`: Reverse direction
    - `event-triggered`: Direction changes based on events (e.g., sending vs receiving data)
    - Configurable default direction preference
  - Uses lighter shade (#FFA500) over base color (#D97706)
  - Speed synchronized with frame interval
  - Resets position when word changes
  - Character-by-character color application
  - Can be triggered to change direction via API call
- **Ellipsis Addition**: Automatic "..." suffix to action words
- **Color Support**: Full hex color configuration

**Configuration Options**:
```json
{
  "type": "message",
  "action_words": {
    "mode": "add",
    "words": ["Contemplating", "Analyzing"]
  },
  "interval": {
    "min": 0.5,
    "max": 3.0
  },
  "color": "#D97706",
  "shimmer": {
    "enabled": true,
    "width": 3,
    "light_color": "#FFA500",
    "speed": 1.0,
    "direction": "left-to-right",
    "event_triggered": false
  },
  "suffix": "..."
}
```
**Default Action Words**
```json
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
```

**Shimmer Implementation Details**:
```python
# Shimmer effect logic from example_progress.py
shimmer_position = -shimmer_width  # Start off-screen
for i, char in enumerate(text):
    if shimmer_position <= i < shimmer_position + shimmer_width:
        # Apply light color to characters in shimmer zone
        output += light_color + char + reset + base_color
    else:
        # Regular color for other characters
        output += char
shimmer_position += 1  # Move shimmer right
if shimmer_position > len(text):
    shimmer_position = -shimmer_width  # Reset
```

**Test Requirements**:
- Test default word list displays correctly
- Verify add/replace modes work as expected
- Test random selection distribution
- Validate shimmer effect smoothness
- Test shimmer reset on word change
- Verify interval timing accuracy
- Test with very short and very long words

---

## ThothSpinner Parent Component

**Purpose**: Container component that orchestrates all individual components with global configuration and state management

**Requirements**:
- **Component Composition**: Manage multiple components (Spinner, Message, Progress, Timer, Hint) as a unified display
- **Configuration Hierarchy**:
  - Global defaults at parent level
  - Individual component overrides
  - Inheritance system for common properties
- **Element Ordering**: Define display order of components via configuration
- **Global State Management**:
  - Success/error states affect all child components
  - Coordinated state transitions
  - Event propagation to components

**Configuration Options**:
```json
{
  "name": "ThothSpinner",
  "defaults": {
    "color": "#D97706",
    "visible": true,
    "success": {
      "color": "#00FF00",
      "duration": null,  // Permanent by default
      "behavior": "indicator"  // Or "disappear", "message", "both"
    },
    "error": {
      "color": "#FF0000",
      "duration": null,
      "behavior": "indicator"
    }
  },
  "elements": [
    {"type": "spinner", "success": {"indicator": "✓"}, "error": {"indicator": "✗"}},
    {"type": "message"},
    {"type": "progress"},
    {"type": "timer"},
    {"type": "hint", "text": "(esc to cancel)"}
  ],
  "fade_away": {
    "enabled": false,  // Instant disappear by default
    "direction": "left-to-right",
    "interval": 0.05  // Time between each element disappearing
  }
}
```

**State Management Features**:
- **Success/Error Behaviors**:
  - `disappear`: Element vanishes (instant or fade-away)
  - `indicator`: Show static symbol (spinner → ✓/✗)
  - `message`: Show custom text
  - `both`: Show indicator + message
  - `color_only`: Just change color, keep animating
- **Duration Control**:
  - `null`: Permanent until manually cleared
  - Number: Auto-clear after N seconds
  - Different durations for success vs error
- **Fade-Away Animation**:
  - Elements disappear sequentially
  - Left-to-right or right-to-left
  - Configurable interval between elements

**Potential API Methods Examples**:
```python
spinner = ThothSpinner(config)
spinner.start()  # Begin in 'in_progress' state
spinner.update_progress(50, 100)
spinner.set_message("Custom message")
spinner.set_shimmer_direction("right-to-left")  # For event-triggered changes
spinner.success()  # Transition to 'success' state
spinner.error("Custom error message")  # Transition to 'error' state
spinner.reset()  # Return to 'in_progress' state
spinner.clear()  # Clear display and stop
```

---

## State System

**Purpose**: Define clear lifecycle states for the spinner with consistent behavior across all components

### Core States

1. **`in_progress`** (Default State)
   - Initial state when spinner starts
   - All configured animations are active
   - Components display their normal behavior
   - This is the working/active state

2. **`success`** (Terminal State)
   - Triggered when operation completes successfully
   - Components transform based on success configuration
   - Can be permanent or auto-clear after duration
   - No return to in_progress without explicit reset

3. **`error`** (Terminal State)
   - Triggered when operation fails
   - Components show error indicators/colors
   - Can be permanent or auto-clear after duration
   - No return to in_progress without explicit reset

### State Configuration

**Unified Animation Control**:
All components use `animating: true/false` for consistency:
- Spinner: Controls frame rotation
- Message: Controls word cycling
- Timer: Controls time counting
- Progress: Static by nature (no animation)
- Hint: Static by nature (no animation)

**Configuration Example**:
```json
{
  "states": {
    "in_progress": {
      "spinner": {"animating": true, "color": "#D97706"},
      "message": {"animating": true, "shimmer": true},
      "timer": {"animating": true},
      "progress": {"visible": true},
      "hint": {"visible": true}
    },
    "success": {
      "behavior": "indicator",  // "disappear", "message", "both", "color_only"
      "duration": null,  // null = permanent, number = seconds to display
      "fade_away": false,
      "spinner": {"animating": false, "icon": "✓", "color": "#00FF00"},
      "message": {"animating": false, "text": "Complete!", "shimmer": false},
      "timer": {"animating": false, "color": "#00FF00"},
      "progress": {"visible": true, "color": "#00FF00", "value": "100%"},
      "hint": {"visible": false}
    },
    "error": {
      "behavior": "indicator",
      "duration": 5.0,  // Display for 5 seconds then clear
      "fade_away": true,  // Use fade-away animation
      "spinner": {"animating": false, "icon": "✗", "color": "#FF0000"},
      "message": {"animating": false, "text": "Failed", "shimmer": false},
      "timer": {"animating": false, "color": "#FF0000"},
      "progress": {"visible": true, "color": "#FF0000"},
      "hint": {"text": "Check logs for details", "color": "#FF0000"}
    }
  }
}
```

### State Transition Rules

1. **Valid Transitions**:
   - `in_progress` → `success`
   - `in_progress` → `error`
   - Any state → `in_progress` (via reset())
   - Any state → cleared (via clear())

2. **Invalid Transitions**:
   - `success` → `error` (must reset first)
   - `error` → `success` (must reset first)

3. **Transition Triggers**:
   ```python
   # Start in in_progress
   spinner.start()

   # Transition to success
   spinner.success()
   spinner.success("Custom success message")

   # Transition to error
   spinner.error()
   spinner.error("Custom error message")

   # Reset to in_progress
   spinner.reset()

   # Clear and stop
   spinner.clear()
   ```

---

## Color System Requirements

**All Components Must Support**:
- **Hex Color Input**: Accept colors as #RRGGBB format
- **ANSI Conversion**: Convert hex to appropriate ANSI escape codes
- **Terminal Compatibility**: Work with 256-color and true-color terminals
- **Default Colors**:
  - Claude Orange: #D97706
  - Claude Orange Light: #FFA500 (for shimmer)
  - Gray: #808080 (for hints)
  - Green: #00FF00 (for success)
  - Red: #FF0000 (for errors)

**Color Conversion Example**:
```python
def hex_to_ansi(hex_color):
    # Convert #RRGGBB to ANSI escape code
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"\033[38;2;{r};{g};{b}m"
```

---

## Component State Behaviors

**Each Component Behaves Differently Across Three States**:

### Spinner Component States

| State | Behavior | Configuration Options |
|-------|----------|----------------------|
| **in_progress** | Animating through frame sequence | `animating: true`, frame interval, color |
| **success** | Static success icon or disappear | `animating: false`, icon (✓/✅), color (#00FF00) |
| **error** | Static error icon or disappear | `animating: false`, icon (✗/❌), color (#FF0000) |

### Message Component States

| State | Behavior | Configuration Options |
|-------|----------|----------------------|
| **in_progress** | Cycling through action words with shimmer | `animating: true`, shimmer direction, word interval |
| **success** | Display success text or last word | `animating: false`, custom text, shimmer off |
| **error** | Display error text or last word | `animating: false`, custom text, shimmer off |

### Progress Component States

| State | Behavior | Configuration Options |
|-------|----------|----------------------|
| **in_progress** | Shows current/total progress | Updates in real-time, format style |
| **success** | Shows 100% or final value | Color change, optional text override |
| **error** | Shows failure point or custom text | Color change, "Failed" text option |

### Timer Component States

| State | Behavior | Configuration Options |
|-------|----------|----------------------|
| **in_progress** | Counting elapsed time | `animating: true`, format style, precision |
| **success** | Stops at final time | `animating: false`, success color |
| **error** | Stops at error time | `animating: false`, error color |

### Hint Component States

| State | Behavior | Configuration Options |
|-------|----------|----------------------|
| **in_progress** | Shows helper text | Static text, default color |
| **success** | Success message or hidden | Custom text, success color, visibility |
| **error** | Error hint or hidden | Custom text, error color, visibility |

### Behavior Inheritance

Components inherit state configurations in this priority order:
1. Component-specific state config (highest priority)
2. Global state config for that state
3. Component defaults
4. Global defaults (lowest priority)

**Example showing inheritance**:
```json
{
  "defaults": {
    "color": "#D97706",  // Global default
    "animating": true
  },
  "states": {
    "success": {
      "global_color": "#00FF00",  // State default
      "animating": false,
      "spinner": {
        "icon": "✓"  // Component-specific override
      }
    }
  }
}
```

**Interruption Handling**:
- Clean shutdown on Ctrl+C with cursor restoration
- Components save state before cleanup
- Optional cleanup message display

---

## Testing Strategy

### Unit Tests (Per Component)
1. **Initialization**: Component creates with default settings
2. **Configuration**: All config options apply correctly
3. **Color Rendering**: Hex colors convert and display properly
4. **Shimmer Effects**: Animation renders smoothly
5. **State Management**: Component updates reflect immediately
6. **Memory Management**: No leaks during long runs

### Integration Tests
1. **Component Combination**: Multiple components work together
2. **Performance**: Smooth animation at 60+ FPS
3. **Terminal Compatibility**: Works on various terminal emulators
4. **Library Integration**: Works with Rich and Textual
5. **Configuration Loading**: JSON/YAML/TOML parsing works

### Visual Tests
1. **Manual Inspection**: Components look correct
2. **Screenshot Comparison**: Automated visual regression
3. **Animation Smoothness**: No flicker or jank
4. **Color Accuracy**: Colors match specifications

---

## Development Phases

### Phase 1: Foundation (Week 1)
- Implement Hint component with tests
- Implement Spinner component with tests
- Basic color system implementation

### Phase 2: Counters (Week 2)
- Implement Progress component with tests
- Implement Timer component with tests
- Shimmer effect system

### Phase 3: Dynamic Text (Week 3)
- Implement Message component with tests
- Complete shimmer integration
- Action words system

### Phase 4: Integration (Week 4)
- Combine all components
- Configuration system
- Rich/Textual adapters
- Documentation and examples

---

## Success Criteria

1. **All components render correctly** in common terminal emulators
2. **Shimmer effects animate smoothly** without performance impact
3. **Configuration system is intuitive** and well-documented
4. **Tests achieve 90%+ coverage** with all edge cases handled
5. **Examples demonstrate** all major use cases
6. **Performance maintains 60+ FPS** with all effects enabled
7. **Memory usage remains stable** during long-running operations

---

## Example Usage

```python
from thothspinner import Spinner, Progress, Timer, Message, Hint

# Simple spinner with default settings
spinner = Spinner()
spinner.start()

# Complex configuration
config = {
    "elements": [
        {"type": "spinner", "color": "#D97706", "shimmer": {"enabled": True}},
        {"type": "message", "shimmer": {"enabled": True, "width": 3}},
        {"type": "progress", "format": {"style": "percentage"}},
        {"type": "timer", "format": {"style": "auto"}},
        {"type": "hint", "text": "(esc to cancel)", "color": "#888888"}
    ]
}

# Create from configuration
progress_bar = ThothSpinner(config)
progress_bar.start()
```
