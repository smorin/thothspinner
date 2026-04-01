Output docs/images/demo.gif
Set FontSize 14
Set Width 800
Set Height 500
Set Theme "Dracula"
Set PlaybackSpeed 0.75

Sleep 500ms

# Full component demo: spinner + message + progress + timer + hint
# Phases: Analyzing → Building → Testing → Deploying → success, then error sequence
# Runtime: ~10s (phases × 0.04s/step + pauses)
Type "uv run python examples/demo_for_gif.py"
Enter
Sleep 500ms
Sleep 12000ms

# Style sampler — 4 visually distinct styles
# Each preview runs for 3s; sleep 4s to cover display + printed name

Type "uv run thothspinner preview npm_dots"
Enter
Sleep 4000ms

Type "uv run thothspinner preview claude_stars"
Enter
Sleep 4000ms

Type "uv run thothspinner preview moon"
Enter
Sleep 4000ms

Type "uv run thothspinner preview earth"
Enter
Sleep 4000ms

Sleep 500ms
