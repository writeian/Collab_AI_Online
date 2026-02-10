# Pin & Library Tools - User Testing Checklist

**Instructions:** Please test each feature below and check the box when completed. If you encounter any issues, bugs, or quality problems, please describe them in detail in the "Issues Found" section at the bottom.

---

## Part 1: Pin Tool Testing

### Basic Pin Functionality

- [ ] **Pin a Message**
  - Find a message in a chat (from you or the AI)
  - Click the pin button/icon on the message
  - Verify: Button changes to show "pinned" state
  - Verify: Message appears in your pins list (if visible)

- [ ] **Pin a Comment**
  - Find a comment on a message
  - Click the pin button/icon on the comment
  - Verify: Button changes to show "pinned" state
  - Verify: Comment appears in your pins list (if visible)

- [ ] **Unpin an Item**
  - Find a pinned message or comment
  - Click the unpin button/icon
  - Verify: Button changes back to unpinned state
  - Verify: Item is removed from pins list

- [ ] **Pin the Same Item Twice**
  - Try pinning an already-pinned message
  - Verify: No error occurs
  - Verify: Item remains pinned (doesn't duplicate)

### Shared vs Personal Pins

- [ ] **Create a Personal Pin**
  - Pin a message without selecting "shared" option
  - Verify: Pin is created successfully
  - Note: Personal pins should only be visible to you

- [ ] **Create a Shared Pin** (if option available)
  - Pin a message and select "shared" option (if available in UI)
  - Verify: Pin is created successfully
  - Note: Shared pins should be visible to all room members

### Pin Display & UI

- [ ] **View Pins List**
  - Navigate to where pins are displayed (sidebar, menu, etc.)
  - Verify: Your pinned items appear in the list
  - Verify: Pins show correct content (message/comment text)
  - Verify: Pins show correct metadata (date, source chat, etc.)

- [ ] **Pin Button States**
  - Check unpinned items: Button shows "Pin" or pin icon
  - Check pinned items: Button shows "Pinned" or filled pin icon
  - Verify: Visual state is clear and consistent

- [ ] **Pin Button Responsiveness**
  - Click pin button multiple times quickly
  - Verify: Button doesn't get stuck in loading state
  - Verify: No duplicate pins created
  - Verify: UI updates smoothly

### Error Scenarios

- [ ] **Pin While Not Logged In**
  - Log out (if possible)
  - Try to pin a message
  - Verify: Appropriate error message appears
  - Verify: Pin action is prevented

- [ ] **Pin Deleted Message/Comment**
  - Pin a message
  - Delete the original message (if possible)
  - Verify: Pin still exists (snapshot preserved)
  - Verify: Pin shows appropriate "deleted" indicator (if implemented)

---

## Part 2: Library Tool Testing

### Document Upload

- [ ] **Upload a PDF Document**
  - Go to Library tool in sidebar
  - Click "Choose File" or upload button
  - Select a PDF file (under 10 MB)
  - Verify: File uploads successfully
  - Verify: Progress indicator shows during upload
  - Verify: Document appears in documents list after upload
  - Verify: Document name is displayed correctly

- [ ] **Upload a DOCX Document**
  - Upload a Word document (.docx)
  - Verify: Upload succeeds
  - Verify: Document appears in list

- [ ] **Upload a TXT Document**
  - Upload a plain text file (.txt)
  - Verify: Upload succeeds
  - Verify: Document appears in list

- [ ] **Upload Multiple Documents**
  - Upload 2-3 different documents one after another
  - Verify: All uploads succeed
  - Verify: All documents appear in list
  - Verify: Storage usage updates correctly

### File Size Limits

- [ ] **Upload File Over 10 MB**
  - Try to upload a file larger than 10 MB
  - Verify: Error message appears before upload starts
  - Verify: Upload is prevented
  - Verify: Error message is clear and helpful

- [ ] **Upload File Near Limit**
  - Upload a file close to 10 MB (e.g., 9.5 MB)
  - Verify: Upload succeeds
  - Verify: Storage usage updates correctly

- [ ] **Exceed Total Storage Limit**
  - Upload documents until you approach 10 MB total
  - Try to upload another document that would exceed the limit
  - Verify: Error message appears
  - Verify: Upload is prevented
  - Verify: Error message shows available space

### Storage Usage Display

- [ ] **Storage Indicator Visibility**
  - Check Library tool sidebar
  - Verify: Storage usage is displayed (e.g., "5.2 MB / 10 MB")
  - Verify: Usage percentage or bar is shown (if implemented)

- [ ] **Storage Updates After Upload**
  - Note current storage usage
  - Upload a new document
  - Verify: Storage usage updates immediately
  - Verify: New usage is accurate

- [ ] **Storage Updates After Delete**
  - Note current storage usage
  - Delete a document
  - Verify: Storage usage decreases
  - Verify: New usage is accurate

### Document Search

- [ ] **Search Within Documents**
  - Upload at least one document with known content
  - Use the search box in Library tool
  - Enter a search term that appears in your document
  - Verify: Search results appear
  - Verify: Results show relevant text snippets
  - Verify: Results show which document they came from

- [ ] **Search with No Results**
  - Search for a term that doesn't exist in any document
  - Verify: "No results" message appears (or empty state)
  - Verify: Message is clear and helpful

- [ ] **Search Across Multiple Documents**
  - Upload 2-3 documents with different content
  - Search for a term that appears in multiple documents
  - Verify: Results from all matching documents appear
  - Verify: Results are ranked by relevance

- [ ] **Search Empty Library**
  - Search when no documents are uploaded
  - Verify: Appropriate message appears
  - Verify: No errors occur

### Document Management

- [ ] **Delete a Single Document**
  - Find a document in the list
  - Click delete button/icon
  - Verify: Confirmation dialog appears (if implemented)
  - Verify: Document is removed from list after deletion
  - Verify: Storage usage decreases

- [ ] **Delete Multiple Documents**
  - Delete 2-3 documents one after another
  - Verify: Each deletion succeeds
  - Verify: List updates correctly after each deletion
  - Verify: Storage usage updates correctly

- [ ] **Delete Last Document**
  - Delete all documents until none remain
  - Verify: "No documents" placeholder appears
  - Verify: Storage shows 0 MB / 10 MB
  - Verify: No errors occur

### AI Integration (Document Context)

- [ ] **AI Uses Document Content**
  - Upload a document with specific content (e.g., "The capital of France is Paris")
  - Ask the AI a question related to that content (e.g., "What is the capital of France?")
  - Verify: AI response includes information from your document
  - Verify: AI response is accurate

- [ ] **AI Uses Multiple Documents**
  - Upload 2-3 documents with different topics
  - Ask a question that relates to content in multiple documents
  - Verify: AI synthesizes information from multiple documents
  - Verify: Response is comprehensive

- [ ] **Synthesis Mode - Summarize All Documents**
  - Upload multiple documents (3-5 documents)
  - Ask: "Summarize all sources" or "Synthesize all documents" or "Give me an overview of all documents"
  - Verify: AI provides a comprehensive summary
  - Verify: Summary covers all documents
  - Verify: Summary identifies common themes (if applicable)

- [ ] **AI Ignores Unrelated Documents**
  - Upload documents about Topic A
  - Upload one document about Topic B
  - Ask a question about Topic A
  - Verify: AI primarily uses Topic A documents
  - Verify: Topic B document doesn't interfere

- [ ] **AI Without Documents**
  - Don't upload any documents
  - Ask a general question
  - Verify: AI responds normally (doesn't break)
  - Verify: No errors occur

### UI/UX Quality

- [ ] **Library Tool Visibility**
  - Open a chat
  - Verify: Library tool appears in sidebar/tools section
  - Verify: Tool card can be expanded/collapsed
  - Verify: Tool is clearly labeled

- [ ] **Upload Progress Feedback**
  - Upload a large document (several MB)
  - Verify: Progress indicator shows during upload
  - Verify: Progress updates smoothly
  - Verify: Status messages are clear (e.g., "Extracting text...", "Indexing...")

- [ ] **Document List Display**
  - Upload multiple documents
  - Verify: List is scrollable if many documents
  - Verify: Document names are readable (not truncated awkwardly)
  - Verify: List updates smoothly when documents are added/deleted

- [ ] **Error Messages**
  - Try various error scenarios (file too large, upload failure, etc.)
  - Verify: Error messages are clear and helpful
  - Verify: Error messages explain what went wrong
  - Verify: Error messages suggest how to fix the issue

- [ ] **Loading States**
  - Perform actions that take time (upload, search, delete)
  - Verify: Loading indicators appear
  - Verify: UI doesn't freeze during loading
  - Verify: Loading states are clear and not confusing

### Performance & Reliability

- [ ] **Large Document Upload**
  - Upload a document close to 10 MB
  - Verify: Upload completes successfully
  - Verify: Processing time is reasonable (under 30 seconds for 10 MB)
  - Verify: No browser freezing or crashes

- [ ] **Many Documents**
  - Upload 10+ documents (if possible within storage limit)
  - Verify: List displays all documents
  - Verify: Scrolling works smoothly
  - Verify: Search works across all documents

- [ ] **Rapid Actions**
  - Quickly upload, delete, and search multiple times
  - Verify: No errors occur
  - Verify: UI remains responsive
  - Verify: Actions complete correctly

- [ ] **Page Refresh**
  - Upload some documents
  - Refresh the page
  - Verify: Documents still appear after refresh
  - Verify: Storage usage is still accurate
  - Verify: No data loss

---

## Part 3: Integration & Edge Cases

### Cross-Feature Integration

- [ ] **Pin Library-Related Messages**
  - Upload a document
  - Ask AI a question about the document
  - Pin the AI's response
  - Verify: Pin works normally
  - Verify: Pinned message shows correct content

- [ ] **Library in Multiple Rooms**
  - Create/join multiple rooms (if possible)
  - Upload documents in different rooms
  - Verify: Documents are scoped to correct room
  - Verify: Documents from Room A don't appear in Room B
  - Verify: AI only uses documents from current room

### Browser Compatibility

- [ ] **Test in Chrome/Edge**
  - Complete basic upload, search, and pin tests
  - Verify: All features work correctly

- [ ] **Test in Firefox**
  - Complete basic upload, search, and pin tests
  - Verify: All features work correctly

- [ ] **Test in Safari** (if available)
  - Complete basic upload, search, and pin tests
  - Verify: All features work correctly

### Mobile/Responsive (if applicable)

- [ ] **Mobile View**
  - Test on mobile device or narrow browser window
  - Verify: Library tool is accessible
  - Verify: Upload button works
  - Verify: Document list is readable
  - Verify: Pin buttons are usable

---

## Issues Found

**Please describe any bugs, errors, or quality issues you encountered:**

### Pin Tool Issues

1. **Issue:** [Describe the issue]
   - **Steps to reproduce:** [What you did]
   - **Expected:** [What should have happened]
   - **Actual:** [What actually happened]
   - **Screenshot/Details:** [Any additional info]

2. **Issue:** [Describe the issue]
   - **Steps to reproduce:** [What you did]
   - **Expected:** [What should have happened]
   - **Actual:** [What actually happened]

### Library Tool Issues

1. **Issue:** [Describe the issue]
   - **Steps to reproduce:** [What you did]
   - **Expected:** [What should have happened]
   - **Actual:** [What actually happened]
   - **Screenshot/Details:** [Any additional info]

2. **Issue:** [Describe the issue]
   - **Steps to reproduce:** [What you did]
   - **Expected:** [What should have happened]
   - **Actual:** [What actually happened]

### General Issues

1. **Issue:** [Describe the issue]
   - **Steps to reproduce:** [What you did]
   - **Expected:** [What should have happened]
   - **Actual:** [What actually happened]

---

## Overall Feedback

**What worked well:**
- [Your feedback]

**What could be improved:**
- [Your feedback]

**Any other comments:**
- [Your feedback]

---

**Thank you for testing!** Please return this completed checklist with any issues found.

