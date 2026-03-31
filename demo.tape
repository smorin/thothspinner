Output demo.gif
Set FontSize 14
Set Width 800
Set Height 400
Set Theme "Dracula"
Set PlaybackSpeed 1.0

Sleep 500ms

# Run the demo script showing ThothSpinner.track() in action
Type "uv run python examples/demo_for_gif.py"
Enter
Sleep 200ms

# Wait for 101 iterations × 0.025s ≈ 2.5s + buffer for startup and success display
Sleep 4000ms

# Show the CLI preview command for a couple of styles
Type "uv run thothspinner preview npm_dots"
Enter
Sleep 2000ms

Type "uv run thothspinner preview claude_stars"
Enter
Sleep 2000ms

Type "uv run thothspinner preview moon"
Enter
Sleep 2000ms

Sleep 500ms
