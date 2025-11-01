# Create New Issue

You are being asked to create a new issue in the Issues Management System.

## Your Task

1. **Get the issue title** from the user's command arguments (e.g., `/new-issue "Cache crashes on repeated queries"`)

2. **Find next available issue number**:
   - Read all files in `issues/new-issue-context/`
   - Find highest ISSUE-NNN number
   - Increment by 1 for new issue

3. **Create slug from title**:
   - Convert to lowercase
   - Replace spaces with hyphens
   - Remove special characters
   - Limit to 50 characters
   - Example: "Cache crashes on repeated queries" → "cache-crashes-on-repeated-queries"

4. **Read the template**:
   - Read `workflow/issues/templates/1-NEW-ISSUE-TEMPLATE.md`

5. **Fill in metadata**:
   - Replace `{NNN}` with issue number (zero-padded 3 digits, e.g., 009)
   - Replace `{Title}` with actual title
   - Replace `{YYYY-MM-DD}` with today's date
   - Leave severity, category as placeholders for user to fill

6. **Save to new-issue-context/**:
   - Filename: `ISSUE-{NNN}-{slug}.md`
   - Location: `issues/new-issue-context/`
   - Example: `issues/new-issue-context/ISSUE-009-cache-crashes.md`

7. **Output summary**:
   ```
   ✅ Created: issues/new-issue-context/ISSUE-{NNN}-{slug}.md
   📝 Please fill in:
      - Severity (P0-P3)
      - Symptoms
      - Steps to reproduce
      - Expected vs actual behavior

   Next step: /diagnose ISSUE-{NNN}
   ```

8. **Open file for editing** (use Read tool to display contents so user can review)

## Important Notes

- **Always use 3-digit zero-padded issue numbers** (001, 002, 009, 010, 099, 100)
- **Issue numbers never reset** - they increment forever
- **Slugs must be filesystem-safe** - no special characters except hyphens
- **Template placeholders** must all be replaced except those marked for user input

## Error Handling

- If no title provided: Ask user for title
- If title too short (<3 chars): Ask for more descriptive title
- If cannot determine next number: Default to ISSUE-001 if no issues exist
