![](_page_0_Picture_0.jpeg)

# **Custom Rich Progress Bar Guide**

## **Introduction to Rich Progress Bars**

Rich's **Progress** class provides flexible, live-updating progress bars for the terminal. By default, a progress display shows each task's description, a progress bar, the percentage completed, and an estimated remaining time 1. Rich supports multiple concurrent tasks – each task appears as a new row in the progress display, sharing the same columns (metrics) 2. These **columns** are modular components (like progress bar visuals, text displays for percentages or speeds, etc.) that Rich uses to render each task. This modular design makes it easy to customize what information is shown.

**Core behaviors of Rich's progress bar** that we typically want to replicate include: automatic live updating (via an internal refresh loop), the ability to add/update tasks with thread-safe methods, support for indefinite progress (unknown totals) with pulsing animations, and smart terminal behavior (e.g. not flooding the output when not in an interactive terminal).

The **new behavior** we want to introduce is support for *multiple sub-components* in the progress display. In practical terms, this could mean showing multiple progress bars or metrics for a single overall process. For example, you might have an **overall progress** tracking the total work, and a secondary **sub-task progress** tracking the current step in detail (like a file download progress alongside an overall task counter). By composing multiple progress indicators, users can get a richer view of a multi-phase or multi-component operation.

Rich does not natively allow different tasks in one Progress instance to have different column layouts <sup>3</sup>. All tasks share the same set of columns. This means if you need fundamentally different metrics or visual components for different aspects of a job, you have to get creative. In this guide, we'll explore two approaches to build a custom progress bar that **reuses Rich's components** (to keep familiar metrics like percentage, time, speed) and adds new capabilities for multiple sub-components:

- Approach 1: Extending Rich's Progress with custom columns or subclasses. We'll subclass Rich's building blocks (like ProgressColumn or even Progress itself) to integrate additional metrics or visual elements into a single unified progress display. This approach keeps one Progress instance (one live progress bar table), which is suitable if all your information can be shown in one table row per task (even if that row becomes complex with multiple sub-bars or texts).
- Approach 2: Composing multiple Progress instances using low-level Live rendering. We'll use Rich's lower-level primitives such as Live (for manual refresh control) and Group (to combine renderables) to display multiple progress bars at once. Essentially, we run separate Progress objects side by side or stacked, each handling a different aspect (e.g. one for overall progress, one for a sub-task). This is useful when the different progress components have distinct column sets or update cycles. It gives maximum flexibility at the cost of a bit more manual management.

We will also discuss **testing** these custom progress bars. Rich's own test suite provides good patterns: using a Console with force\_terminal=True to simulate an interactive terminal for capture, disabling auto-

refresh threads for deterministic output, and verifying the rendered text or components 4 5. By following similar practices, we can ensure our custom progress bar works correctly and remains stable as Rich updates.

Let's dive into the design and implementation of each approach.

## **Designing a Custom Progress Bar by Extending Rich**

In this approach, we leverage Rich's extension points to add new behaviors while preserving core functionality. The key concept here is Rich's **ProgressColumn** API, which is how Rich renders each part of a progress bar. Each column (for example, the bar itself or the percentage text) is an object that knows how to render itself given a task's state. Rich provides many built-in **ProgressColumn** classes (for bar, percentage, speed, etc.), and you can **create your own by subclassing ProgressColumn 6**.

### Using Custom ProgressColumn for Additional Metrics

If you want to show additional metrics or even an extra progress bar *within* the same task row, you can implement a custom column. For instance, suppose each task has a "sub-task" progress value in addition to the main progress. We could create a SubProgressColumn that renders a secondary progress bar or text.

To do this, you can take advantage of the fact that Rich's Task objects can carry arbitrary fields. When updating a task, any extra keyword arguments you supply are stored in task.fields 7. A custom ProgressColumn can read these fields and use them in rendering. For example, if we update a task with progress.update(task\_id, phase\_completed=20, phase\_total=100), the task's fields will include those values. Our custom column can then use task.fields["phase\_completed"] and task.fields["phase\_total"] to draw a smaller progress bar for the sub-task.

Below is a conceptual example of a custom column that displays a secondary bar for a sub-task phase:

```
from rich.progress import ProgressColumn, ProgressBar

class PhaseProgressColumn(ProgressColumn):
    """A custom column to display a sub-task progress bar within a main task."""
    def render(self, task):
        # Retrieve sub-task progress values from the task's fields (with
    defaults)
        completed = task.fields.get("phase_completed", 0)
        total = task.fields.get("phase_total", None)
        # Use Rich's ProgressBar to render a smaller bar for the sub-task
        sub_bar = ProgressBar(total=total, completed=completed, width=20)
        return sub_bar
```

In this example, PhaseProgressColumn.render returns a ProgressBar renderable. We specify a fixed width (20 characters) for the sub-bar for consistency. If total is None, Rich's ProgressBar will

render a pulsing bar (useful if the sub-task length is indeterminate). Now we can use this new column in our Progress:

```
from rich.progress import Progress, BarColumn, TextColumn
# Define our progress with an extra column for the sub-task bar
progress = Progress(
    TextColumn("{task.description}"),
    BarColumn(),
```

When we add tasks to this Progress, we should include the sub-task total in the initial fields, for example:

```
task_id = progress.add_task("Processing file", total=100, phase_total=50,
phase_completed=0)
```

And when updating, we update both the main progress and the sub progress fields:

```
progress.update(task_id, advance=5, phase_completed=25)
```

This will increment the main progress by 5 and set the sub-task progress to 25/50. The output would show one row with the description, a main progress bar (reflecting 5/100), a secondary bar (reflecting 25/50), and the main percentage. We have essentially **composed two bars in one task row**.

**Important:** All custom ProgressColumns should be relatively lightweight to render, since Rich may call them frequently. default. Rich will cache column outputs uр certain By to а rate (ProgressColumn.max\_refresh) to avoid excessive re-rendering (8). For our PhaseProgressColumn, rendering is quick, so we don't set a max refresh (it inherits None, meaning refresh as often as the main loop runs). If your column performed heavier calculations, consider setting a max\_refresh to, say, 0.5 seconds to throttle updates.

This column-based approach works best when your new behaviors **fit into the paradigm of "one row per task"**. We reused Rich's **ProgressBar** component for the sub-bar to keep the look consistent with the main bar. We also reused **TextColumn** format strings and Rich's field mechanism for showing percentages and other text – for example, TextColumn("{task.percentage:>3.0f}%") uses Rich's built-in formatting of Task.percentage. Many of Rich's built-in columns (like TimeRemainingColumn, TransferSpeedColumn, etc.) can be directly added to your Progress if relevant, or you can copy their approach for custom metrics. The snippet below shows how easy it is to compose built-ins and custom columns:

```
from rich.progress import TimeRemainingColumn, TaskProgressColumn
progress = Progress(
    "[progress.description]{task.description}", # description (using markup
syntax)
    BarColumn(),
    PhaseProgressColumn(),
    TaskProgressColumn(show_speed=True),
    # our custom column
    TaskProgressColumn(),
    # built-in column showing
percentage or speed
    TimeRemainingColumn(),
    # built-in ETA for main task
)
```

In this configuration, we included TaskProgressColumn(show\_speed=True), which will display the percentage if known, or the iterations-per-second if the total is not known 9, and a TimeRemainingColumn for ETA. We still have our PhaseProgressColumn in there for the sub-task bar, demonstrating that **custom and built-in columns can co-exist**. This addresses the requirement to use some of the same metrics Rich already has (percentage, speed, time remaining) while adding new ones.

### Subclassing Progress for Custom Rendering (Optional)

Most customizations can be achieved by adding/removing columns. However, in some cases you might want to alter the overall layout or behavior of the progress display itself. For example, you might want to wrap the entire progress table in a panel, or display multiple tables. Rich allows this by letting you override Progress.get\_renderables() in a subclass <sup>10</sup>.

For instance, to draw a border around the progress, you could do:

```
from rich.panel import Panel
from rich.progress import Progress
class PanelProgress(Progress):
    def get_renderables(self):
        # Wrap the default tasks table in a Panel
        yield Panel(self.make_tasks_table(self.tasks))
```

According to Rich's docs, overriding get\_renderables is the way to go if the Progress class doesn't do exactly what you need 10. The example above yields a single Panel containing the tasks table (which is what make\_tasks\_table returns). You could extend this idea: for example, yield multiple renderables for complex layouts (multiple tables, additional headings, etc.). Keep in mind that Progress.\_\_enter\_\_/ \_\_exit\_\_\_ (or start()/(stop()) handle starting and stopping the internal Live display, so if you change rendering, ensure you still call those to manage the display lifecycle.

**When to favor Approach 1:** Using custom columns and minor Progress subclassing is ideal when you want to enhance the progress display *per task*, and all tasks share that enhanced format. It keeps everything in one unified progress bar on the screen, which is conceptually simple for a CLI application. It leverages Rich's internal update loop and synchronization, so you don't have to manage manual refreshing

(as long as you stick to using the Progress context manager or with ...: block). This approach is also easier to package as a drop-in component – e.g., you could bundle your custom columns in a module so other developers can use Progress(\*your\_columns) to get the new functionality.

However, if your progress components are too different to be forced into one table (for example, an overall counter vs. a file download with speed, which require different columns), Approach 1 may hit a limit: *you can't have different columns for each task in one Progress* 3. In that case, consider approach 2.

## **Using Multiple Progress Bars with Live (Composition Approach)**

Approach 2 treats each sub-component as its own Progress instance, and uses a higher-level container to display them together. This is useful if, say, you want an **overall progress bar** (e.g. "Tasks completed out of total") and a **detailed progress bar** for the current task (e.g. "Current task download progress with speed and ETA"). These two have different column requirements, so we'll give each its own Progress and combine them.

Rich's documentation confirms this strategy: if you need different columns per task, you can create multiple Progress instances and render them in a Live display <sup>3</sup>. A Live is essentially a context manager that can continually update the terminal with a renderable (or group of renderables) without flicker. We can use a Live to hold a Group of our progress bars. The Group (from rich.console) is a simple way to bundle multiple renderables so they are treated as one; it will display them one after the other in the given order.

Here's how we can set it up:

```
from rich.live import Live
from rich.console import Group
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn,
TransferSpeedColumn, TimeRemainingColumn
# Define two separate Progress instances with different columns
overall_progress = Progress(
    TextColumn("[bold blue]Overall: {task.completed}/{task.total} done"),
   BarColumn(),
   TaskProgressColumn(), # shows percentage of overall tasks
)
detail_progress = Progress(
   TextColumn("[bold yellow]{task.fields[filename]}"), # filename from task
fields
   BarColumn().
   DownloadColumn(),
                             # shows downloaded bytes/total bytes
    TransferSpeedColumn(),
    TimeRemainingColumn(),
)
# Add tasks to each Progress.
```

```
total_files = 5
overall_task = overall_progress.add_task("All Files", total=total_files)
```

In the above snippet, overall\_progress is configured to show a simple overall counter (completed/ total) and a bar, while detail\_progress is configured with columns suited for download progress (filename, bytes, speed, ETA). We would use the detail\_progress for each file download.

Now, to run them together, we can use Live :

```
from time import time, sleep
with Live(Group(overall_progress, detail_progress), refresh_per_second=10) as
live:
    # Start both Progress instances without their own internal Live
    overall progress.start() # start the internal Live for overall (or use
context manager)
    detail_progress.start()  # start internal Live for detail
    for filename in files_to_download:
        # start a new download task in detail progress
        file_task = detail_progress.add_task(filename, filename=filename,
total=get file size(filename))
        # Download loop (simulate or real)
        while not detail progress.tasks[file task].finished:
            # ... perform download chunk ...
            detail progress.update(file task, advance=chunk size)
            sleep(0.1) # simulate delay
        # Mark file done
        detail progress.remove task(file task)
        # Update overall progress
        overall progress.update(overall task, advance=1)
    # After loop, stop the progress bars
    overall progress.stop()
    detail_progress.stop()
```

In this pseudocode, we manually manage the start/stop of each progress and iterate through tasks. The Live(Group(...)) ensures that on every refresh (10 times per second here), it will redraw both progress bars one after the other. Each Progress's <u>\_\_\_rich\_\_</u> method produces its table of tasks, so the Group effectively stacks two tables. As each file is downloaded, the detail progress bar updates, and once a file is downloaded, we remove that task (to clean up the finished bar) and advance the overall progress.

A few things to note in this approach:

• We had to call overall\_progress.start() and detail\_progress.start(). This actually triggers each Progress's internal Live. An alternative is to not call their start() at all, and instead

manually refresh via the outer Live. In simpler scenarios, you can skip starting the inner Lives and just update tasks, then call <code>live.refresh()</code> to reflect changes. But here we leveraged their internal mechanism (which will still use a separate thread for auto-refresh). Because we are in a single outer Live, this is a bit advanced – to avoid conflicts, you might set <code>auto\_refresh=False</code> on those Progress instances and handle updates explicitly. The implementation can vary; the key is that only one Live display should be actively rendering to the terminal at a time (to avoid LiveError: Only one live display may be active issues, which is what happens if you use two Progress context managers simultaneously) <sup>11</sup>.

- We used Group(progress1, progress2) to vertically stack the two progress displays. If you wanted them side by side instead, you could use a Columns layout or Rich's Layout system. For example, you could create a Layout with two rows or columns and update each with one Progress's renderable. For most CLI progress use-cases, stacking vertically is the easiest to read.
- Each Progress instance can have its own style and columns. In our example, detail\_progress expects a task field filename to display in the text column. We provided that when adding the task with filename=... in add\_task. This shows how using fields allows you to pass context-specific data to specific progress bars (the overall progress doesn't care about filenames, but the detail one does).

**When to favor Approach 2:** Use this when your progress components are logically separate or need distinct formatting. It shines in scenarios like: - An overall progress vs. a per-item progress (as in the download example). - Multiple unrelated progress bars (e.g., one showing CPU usage and another showing task progress, updated by different parts of the program). - Situations where you might want to show/hide entire progress bars independently or update them on different schedules.

The trade-off is that you have to manage multiple Progress objects. This means ensuring that you update the correct one, and coordinating their start/stop if you use their internal refresh. It also means output from each needs to be combined carefully. Using Live as shown takes care of rendering; you just need to be mindful of not using two auto-refreshing Lives concurrently. In complex cases, you might set all inner Progresses to auto\_refresh=False and drive the refresh with one loop, calling refresh() on each or re-rendering the Live Group periodically.

Rich's own guidance is that multiple Progress bars can be combined in a Live, and indeed they provide examples like <a href="live\_progress.py">live\_progress.py</a> and <a href="live\_dynamic\_progress.py">dynamic\_progress.py</a> in the Rich repository for this pattern <a href="live\_approach">3</a>. This approach is essentially building a custom dashboard manually.

## **Testing Your Custom Progress Bar**

Writing tests for live-progress outputs can be tricky due to their interactive nature, but Rich's design makes it possible by faking a terminal environment. The key points are:

• **Force terminal output:** By default, Rich detects when output is not a real terminal (for example, during tests or when piping to a file) and will suppress or simplify the live updates (to avoid dumping a flood of control characters) <sup>5</sup>. In tests, we want to see the full output including progress bar rendering. To achieve this, create a Console with force\_terminal=True. For example:

console = Console(force\_terminal=True, width=80, file=io.StringIO()). Directing
the console to a StringIO allows us to capture everything printed. Rich's author confirms that
force\_terminal=True is needed to bypass the hide-in-file behavior <sup>12</sup>.

- Use a fixed width and disable color if needed: Setting a width (e.g., 80 columns) helps ensure the output format is predictable (bars will have consistent lengths, line wraps won't occur). You might also set Console(color\_system=None) or use Rich's Console(record=True) to capture output without ANSI codes if you plan to assert plain text. Alternatively, you can keep ANSI codes and compare to expected strings with codes Rich's own tests do the latter by comparing exact escape sequences for the bars <sup>13</sup> <sup>14</sup>.
- **Control timing:** If your progress uses time-based features (like speeds or ETA), you should control the timer. Rich allows injecting a custom time function via the get\_time parameter on Progress. In tests, you can pass a fake time function that returns predictable values (or increments in a controlled way) <sup>15</sup> <sup>16</sup>. This ensures that things like Task.elapsed or Task.speed are deterministic. Rich's tests use this technique to simulate time progression without real delays.
- **Disable auto-refresh threads:** For deterministic tests, it's often easier to set auto\_refresh=False on Progress. This prevents background threads from updating the output asynchronously. You can then manually call progress.refresh() at points of interest or simply use the context manager which refreshes at entry/exit. In Rich's tests, they frequently construct Progress(..., auto\_refresh=False) <sup>17</sup> and then use the context manager or manual updates in a tight loop (which they control).
- Capture and assert output: After running your progress logic in a test, you can get the output from the Console. If you used file=io.StringIO() , just do output = console.file.getvalue(). If used record=True, you do output console.export text(). Then you can check for expected substrings or patterns. For example, you might assert that the task description or percentage appears in the output. In our custom PhaseProgressColumn example, you could assert that both the main and sub progress values appear. If you rendered multiple bars, you might look for multiple progress bar glyph sequences in the output.

**Example:** Suppose we want to test that our custom progress with sub-task bar works:

```
from io import StringIO
from rich.console import Console

def test_phase_progress_display():
    console = Console(force_terminal=True, width=60, file=StringIO())
    progress = Progress(
        "Test:", # simple description text
        BarColumn(),
        PhaseProgressColumn(),
        TaskProgressColumn(),
```

```
console=console,
        auto refresh=False,
    )
    task = progress.add_task("Test Task", total=100, phase_total=50)
    progress.update(task, completed=20, phase_completed=10)
    # Manually render once
    console.print(progress) # or progress.refresh() if within context
    output = console.file.getvalue()
# The output should contain "20%" for main progress and possibly the sub-bar
state.
    assert "20%" in output
    # Since the sub bar is 10/50, 20% of phase, it might not show numeric but
bar length.
    # We can assert the presence of the sub-bar character (e.g., "" or similar
block).
    assert " in output # (assuming the block character for progress is
present)
```

This test creates a Progress with our PhaseProgressColumn, updates the task, prints the progress display once, and then inspects the output. We used <a href="mailto:auto\_refresh=False">auto\_refresh=False</a> and a manual <a href="mailto:console.print(progress">console.print(progress)</a> to render the progress at its current state. We also set a known console width, so the bar lengths and wrapping are fixed.

When writing tests, consider what *behavior* you want to verify: - The presence of certain text (e.g., task descriptions, percentages). - That the progress bar reaches 100% or a finished state when expected. - If your custom logic hides or shows elements (like hiding the sub-task bar when not needed), test both scenarios. - Thread-safety or race conditions (for example, if your custom progress updates from multiple threads, you might simulate that, though testing concurrency can be complex).

Rich's own tests are a good reference. They construct progress instances with a fake clock and capture output to verify the rendering exactly <sup>18</sup> <sup>19</sup>. They even compare the raw ANSI output for correctness in some cases. For most projects, you can be a bit less strict (for example, checking percentages rather than exact bar graphics), unless the exact formatting is critical.

Finally, ensure you clean up your progress instances after tests (using context managers or calling stop()), so that no background threads linger. In our examples, using auto\_refresh=False avoids starting threads altogether.

## **Step-by-Step Implementation Checklist**

To wrap up, here is a step-by-step outline for implementing a custom Rich progress bar with multiple sub-components and testing it:

1. **Define Requirements and Components**: Break down what you need to display. Decide which parts can be shown in one progress bar row and which require separate progress bars. For example,

determine if you need one unified progress with extra columns or multiple progress bars (overall vs detail, etc.).

- 2. Reuse or Subclass Columns: For any new metric or visual element in the same row, implement a custom ProgressColumn. Subclass ProgressColumn and override render(task) to return a Rich renderable (text, bar, etc.) using task data. Leverage task.fields to pass dynamic data. *Example:* create a column for a secondary progress bar (sub-task) or a combined text like "X of Y done" (though Rich actually has MofNCompleteColumn built-in for that).
- 3. **Compose the Progress Layout**: Create your Progress instance(s). If one Progress suffices, pass in the sequence of columns (string format or ProgressColumn objects) that includes your custom ones and any built-in ones you need. Adjust options like transient (whether to clear on exit), refresh\_per\_second, etc., as needed. If using multiple Progress instances, configure each with its own columns tailored to its purpose.
- 4. (Optional) Subclass Progress for Layout Tweaks: If you need to change how the progress is rendered as a whole (e.g., wrapping in a Panel, adding a header, or grouping tasks in sections), create a subclass of Progress and override methods like get\_renderables() or make\_tasks\_table(). This is advanced use only do this if simply adding columns or using multiple progress bars doesn't achieve your design. Test this subclass in a simple scenario to ensure it still updates correctly.
- 5. Integrate into Your Application: Use the custom progress in your code. For a single Progress, use it as a context manager (with progress:) or start/stop it manually. Add tasks and update them as your work progresses, making sure to supply the extra fields your custom columns expect. For multiple Progress bars, use a Live context to display them together (as shown in Approach 2). Ensure you update each progress and call refresh() or rely on Live to update the screen. Watch out that you don't start multiple Lives at once combine them under one Live if needed.
- 6. **Testing**: Write tests for critical rendering aspects:
- 7. Set up a fake console with force\_terminal=True and a StringIO buffer.
- 8. Create your progress object(s) with console= that fake console. If using multiple, you might render them via Group and console.print(Group(...)) in the test.
- 9. Use deterministic timing (pass a fixed get\_time or disable auto-refresh) to avoid flaky results.
- 10. Simulate a short run: add a task, do a few updates (maybe in a fast loop or directly set completion), then finalize (stop the progress or exit context).
- 11. Capture the output and assert that expected content appears. For example, verify that the descriptions, percentages, or any custom text from your columns is present. If you know the exact output (e.g., you expect a specific format), assert equality; otherwise, contains checks might be sufficient.
- 12. Use Rich's own tests as guidance for patterns (they use force\_terminal and even compare colored output strings) 13.
- 13. Don't forget edge cases: test what happens at 0% and 100%, test indeterminate state if applicable (total=None), and test with multiple tasks if your progress should handle concurrency.

14. Packaging and Compatibility: Since you are building this outside of Rich's core library, ensure you list Rich as a dependency (with an appropriate version). The guide assumes the latest version of Rich (which as of writing is 13.x/14.x), so confirm your code against the Rich changelog if needed. For instance, class and function names used (like ProgressColumn), TaskProgressColumn, etc.) are stable in Rich 10+ versions. If you distribute your custom progress bar as a separate package, you might want to add an example in your README demonstrating usage, so others know how to integrate your custom columns with Rich's Progress.

By following these steps, you can create a robust custom progress bar solution that builds upon Rich's powerful features. You get to reuse Rich's well-tested components (for things like rendering bars, calculating time remaining, etc. 1 9) and focus on the novel parts of your progress display. At the same time, you avoid reinventing the wheel for core behaviors (like live updating and synchronization) that Rich already handles internally.

With a careful design, your custom progress bar will feel like a natural extension of Rich – providing familiar information (percentages, time, counts) in a new format that supports multiple sub-components, all while maintaining smooth terminal output and clear visuals for users. Happy coding!

## Sources:

- Rich Progress documentation (Rich v13+): configuration of default and custom columns 1 6 7, limitations and multi-progress tips 3, and subclassing for custom rendering 10.
- Rich library source code: implementation of Progress and ProgressColumn, showing how tasks and fields are used in rendering <sup>20</sup> <sup>21</sup>.
- Rich GitHub Discussions: advice from the author on testing progress bars with force\_terminal=True 5.
- Rich test suite examples: using Console(file=StringIO(), force\_terminal=True) and disabling auto-refresh for deterministic output in unit tests 4 22.

1 2 3 6 7 10 21 Progress Display — Rich 14.1.0 documentation https://rich.readthedocs.io/en/stable/progress.html

 4
 13
 14
 15
 16
 17
 18
 19
 22
 test\_progress.py

 https://github.com/Textualize/rich/blob/ea9d4db5d84b4e834979304e3053bf757daae322/tests/test\_progress.py

<sup>5</sup> <sup>12</sup> Unit tests for progress bar in pytest · Textualize rich · Discussion #1093 · GitHub https://github.com/Textualize/rich/discussions/1093

### 8 9 20 progress.py

https://github.com/pypa/pipenv/blob/4e5f9a79839f0e6701422341dcdf8edebb5063eb/pipenv/patched/pip/\_vendor/rich/ progress.py

11 showing multiple \*different\* progress bars · Textualize rich · Discussion #1500 · GitHub https://github.com/Textualize/rich/discussions/1500