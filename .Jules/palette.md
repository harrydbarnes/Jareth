# Palette's Journal

## 2024-05-22 - Visual Feedback for Long Operations
**Learning:** Users can perceive the application as "frozen" if a long-running operation (like analyzing emails) only changes a text label.
**Action:** Always implement a moving visual indicator (spinner or progress bar) for operations expected to take more than 1 second.

## 2024-10-24 - Desktop Form Expectations
**Learning:** Users instinctively press 'Enter' to submit forms even in desktop applications, and expect the cursor to be ready in the first field.
**Action:** Always bind `<Return>` to the primary action and set `focus_set()` on the first input field for Tkinter apps.
