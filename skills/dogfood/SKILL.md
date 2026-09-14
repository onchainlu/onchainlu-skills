---
name: dogfood
description: "Exploratory QA of web apps: find bugs, evidence, reports."
metadata:
  hermes:
    tags: [qa, testing, browser, web, dogfood]
    related_skills: []
---

# Dogfood: Systematic Web Application QA Testing

## Overview

This skill guides you through systematic exploratory QA testing of web applications using the browser toolset. You will navigate the application, interact with elements, capture evidence of issues, and produce a structured bug report.

## Prerequisites

- For hosted runs, use the `browser_exec` route and its Browser Use CLI helpers (see Runtime Mapping below)
- A target URL and testing scope from the user

## Runtime Mapping

`browser_exec` is the canonical hosted browser route. Batch navigation, waiting, extraction, and actions inside one `browser_exec` call rather than assuming separate browser tools or spending one call per browser step. Use only helpers that are present in the hosted runtime:

| QA concept | Hosted route |
|---|---|
| Navigate / wait | `new_tab(url)` for the first page, then `goto_url(url)` and `wait_for_load()` |
| Snapshot / DOM or accessibility inspection | `page_info()` for a page summary; use `cdp('Accessibility.getFullAXTree')` when a full accessibility tree is needed |
| Console inspection | Use the available `cdp(...)` helper for the required CDP Runtime inspection; if that route is unavailable, record console checks as unavailable rather than inventing a tool |
| Screenshot | `capture_screenshot()`; retain the returned path as evidence |
| Actions | `click_at_xy(x, y)`, `fill_input(selector, text)`, or `js(expr)` as appropriate; use `cdp(...)` only for a known CDP action |

The legacy `browser_*` names below are conceptual aliases for these QA concepts, not guaranteed tools. Use them only when those tools are actually present; otherwise translate the step to the mapping above. Do not invent helper names or signatures.

## Inputs

The user provides:
1. **Target URL** — the entry point for testing
2. **Scope** — what areas/features to focus on (or "full site" for comprehensive testing)
3. **Output directory** (optional) — where to save screenshots and the report (default: `./dogfood-output`)

## Workflow

Follow this 5-phase systematic workflow:

### Phase 1: Plan

1. Create the output directory structure:
   ```
   {output_dir}/
   ├── screenshots/       # Evidence screenshots
   └── report.md          # Final report (generated in Phase 5)
   ```
2. Identify the testing scope based on user input.
3. Build a rough sitemap by planning which pages and features to test:
   - Landing/home page
   - Navigation links (header, footer, sidebar)
   - Key user flows (sign up, login, search, checkout, etc.)
   - Forms and interactive elements
   - Edge cases (empty states, error pages, 404s)

### Phase 2: Explore

For each page or feature in your plan:

1. **Navigate and wait** using the hosted route: in one `browser_exec` call, use `new_tab(url)` for the first page or `goto_url(url)` for an existing tab, followed by `wait_for_load()`.

2. **Take a snapshot** with `page_info()`; use `cdp('Accessibility.getFullAXTree')` when a full accessibility tree is needed.

3. **Check the console** through the available `cdp(...)` Runtime inspection route when supported. Do this after every navigation and significant interaction; if unavailable, record that limitation rather than calling an absent tool.

4. **Take a screenshot** with `capture_screenshot()` to visually assess the page and retain the returned path as evidence.

5. **Test interactive elements** systematically inside the same `browser_exec` call where practical:
   - Click at a known viewport location with `click_at_xy(x, y)`
   - Fill an input with `fill_input(selector, text)`
   - Use `js(expr)` or a known `cdp(...)` action only when appropriate
   - Test form validation with invalid inputs and empty submissions

6. **After each interaction**, check for:
   - Console errors: the available `cdp(...)` Runtime route, or record console inspection as unavailable
   - Visual changes: `capture_screenshot()`
   - Expected vs actual behavior

### Phase 3: Collect Evidence

For every issue found:

1. **Take a screenshot** showing the issue with `capture_screenshot()`.
   Save the returned path — you will reference it in the report.

2. **Record the details**:
   - URL where the issue occurs
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Console errors (if any)
   - Screenshot path

3. **Classify the issue** using the issue taxonomy (see `references/issue-taxonomy.md`):
   - Severity: Critical / High / Medium / Low
   - Category: Functional / Visual / Accessibility / Console / UX / Content

### Phase 4: Categorize

1. Review all collected issues.
2. De-duplicate — merge issues that are the same bug manifesting in different places.
3. Assign final severity and category to each issue.
4. Sort by severity (Critical first, then High, Medium, Low).
5. Count issues by severity and category for the executive summary.

### Phase 5: Report

Generate the final report using the template at `templates/dogfood-report-template.md`.

The report must include:
1. **Executive summary** with total issue count, breakdown by severity, and testing scope
2. **Per-issue sections** with:
   - Issue number and title
   - Severity and category badges
   - URL where observed
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshot references (use `MEDIA:<screenshot_path>` for inline images)
   - Console errors if relevant
3. **Summary table** of all issues
4. **Testing notes** — what was tested, what was not, any blockers

Save the report to `{output_dir}/report.md`.

## Tools Reference

| Hosted helper | Purpose |
|---|---|
| `new_tab(url)`, `goto_url(url)`, `wait_for_load()` | Navigate and wait for the page |
| `page_info()` / `cdp('Accessibility.getFullAXTree')` | Page summary or accessibility-tree inspection |
| `cdp(...)` | Known CDP Runtime inspection when supported |
| `capture_screenshot()` | Capture evidence and retain its returned path |
| `click_at_xy(x, y)`, `fill_input(selector, text)`, `js(expr)` | Perform supported page actions |

## Tips

- **Always check the console** after navigating and significant interactions using the available `cdp(...)` Runtime route; if unavailable, record the limitation.
- **Use `capture_screenshot()`** when visual evidence is needed, and retain its returned path.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Check responsive behavior** by noting any layout issues visible in screenshots.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
- When reporting screenshots to the user, include `MEDIA:<screenshot_path>` so they can see the evidence inline.
