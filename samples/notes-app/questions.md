# Open Questions & Design Decisions

## Task Notification System
*Source: notes-2025-12-16.md (2025-12-16 01:55)*

### Core Design Questions

**Q: Does it just annoy me all day long?**
- Status: Open
- Context: Considering how frequently notifications should appear
- Related: Need to balance engagement with annoyance

**Q: What does it do?**
- Status: Open
- Context: Fundamental question about the notification system's core behavior
- Need to define: Specific actions and triggers

**Q: How smart should the notifications be?**
- Status: Exploring
- Options being considered:
  - Simple time-based reminders
  - Context-aware "is this active job done yet?" approach
- Leaning toward: Smarter, context-aware approach

### Estimation & Timing

**Q: How to estimate task duration accurately?**
- Status: Open
- Current assumption: Most tasks take ~30 minutes
- Example case: "fix the lightbulb" → 15 minutes
- Need to determine: Algorithm or heuristics for estimation

**Q: Are the notification intervals appropriate?**
- Status: Needs validation
- Proposed: 30 min, 1 hour, 2 hours, 4 hours
- Need to test: Do these intervals feel natural?

**Q: What defines "idle" state?**
- Status: Proposed solution
- Current proposal: No active task for 1 hour
- Need to validate: Is 1 hour the right threshold?

### Engagement & UX

**Q: What makes an active task "vibrant"?**
- Status: Open
- Context: "that active one be very vibrant - in and out, in and out"
- Need to define: Visual design, placement, interaction patterns

**Q: How to measure engagement success?**
- Status: Open
- Key metric proposed: "how much of the day do I have something?"
- Need to define: Specific success criteria and measurement approach

### Future Integration Priority

**Q: Which integration should come first?**
- Status: Open
- Options: Workouts, prayer times, calendar events
- Note: All marked as "secondary" initially
- Need to decide: Implementation order once core system is built

## MAPS Board Meeting & Organization
*Source: notes-2025-12-17.md (2025-12-17 09:30)*

### Meeting Clarity

**Q: What is the goal of today's meeting?**
- Status: Unclear
- Context: Meeting with Imam Adam and Alejandra
- Personal position: Waiting on volunteer confirmations before can truly start
- Potential use: Learn about board focus and relationship-building strategy

**Q: What role does Alejandra have on the board?**
- Status: Unknown
- Note: Will find out during the meeting

**Q: What is the board's focus for the upcoming year?**
- Status: Open
- Known: Expansion is one focus
- Want to learn: Other priorities beyond expansion

**Q: How does the board see building relationships between Muslims and the wider community?**
- Status: Open
- Context: Strategic question for understanding organizational direction

## Follow-Up Automation
*Source: notes-2025-12-17.md (2025-12-17 09:30)*

### WhatsApp Automation

**Q: How can WhatsApp be automated?**
- Status: Exploring
- Note: "I've heard there's different ways to do that"
- Need to: Research available methods

### Apple Shortcuts Integration

**Q: Can Apple Shortcuts write to a scratchpad that triggers messages?**
- Status: Uncertain
- Context: Need ability to write to scratchpad → send messages from scratchpad
- Belief: Apple Shortcuts likely has this capability

**Q: Can I create my own shortcut for my own app?**
- Status: Wondering
- Context: Considering direct integration between personal app and shortcuts

**Q: Can a shortcut query a table and send messages directly?**
- Status: Open
- Context: Looking for most direct path from data table to outbound messages
- Use case: Automated follow-up reminders based on pending items in a table

## Community Development Strategy
*Source: notes-2025-12-17.md (2025-12-17 09:30)*

### Recruiting Approaches

**Q: What's the best way to recruit program runners vs volunteers?**
- Status: Identified as different challenges
- Observation: "It's one kind of recruiting to find people interested in volunteering. It's a different kind of recruiting to find people who can run programs."
- Need to: Develop distinct strategies for each type

### Mocktail Event Strategy

**Q: Who else could be encouraged to host mocktail events?**
- Status: Exploring
- Known interests: Saqib is somewhat interested
- Known plans: Sister Sarwat thinking January or February
- Strategy: Multiple events with consistent leadership attendance for exposure

## Travel & Personal Practice
*Source: notes-2025-12-21.md (2025-12-21 14:30)*

### Work-Life Balance During Travel

**Q: Should I wake up early during travel to add notes, or prioritize rest?**
- Status: Open
- Tension: Desire to maintain note-taking practice vs. need for rest
- Context: "It's hard to get time during travel to add notes. Need to wake up early? But it's good to rest."
- Consideration: Travel time could be for rejuvenation rather than productivity

### Exercise During Travel

**Q: How to maintain exercise consistency during travel?**
- Status: Reflecting
- Context: "Did some weightlifting. Happy for that. Wish I did more."
- Observation: Some exercise happened but not as much as desired
- Related: Recent Whistler trip with lots of walking and swimming

## Implementation Workflow
*Source: notes-2025-12-23.md (2025-12-23 16:00)*

### Complexity vs Simplicity

**Q: Is the Chatter integration being overthought?**
- Status: Investigating
- Category: Process/Design

**Question:**
Is it necessary to push implementation plans to Chatter, or can they just be written to markdown files?

**Context:**
> "I wonder if I'm overthinking the chatter part. and I can just do a slash implementation plan on her workspace. And instead of pushing it to chatter, just just write it into. userstory-implementation-plan.md."

**Considerations:**
- Testing shows `/implement` command working well
- Files can be shared in Chatter after creation if needed
- Direct file writing is simpler
- Complex integration may not add value
- Markdown files are portable and shareable

**Current Testing:**
- Trying slash implement on workspace at work
- Seems to be working great

**Leaning Toward:**
Simpler approach - just write to markdown files directly, share as needed

## Claude Mobile Audio
*Source: notes-2025-12-23.md (2025-12-23 16:00)*

### Voice Output Implementation

**Q: How to get Claude for mobile to talk/provide audio responses?**
- Status: Open
- Category: Technical

**Question:**
What's the technical approach to enable Claude for mobile to provide spoken/audio responses?

**Context:**
> "I still don't know how to get Cla for mobile to talk to me. Is that going to be via an API call or what?"

**Considerations:**
- Is it via API call?
- What are the available methods?
- Integration with mobile platform capabilities
- Text-to-speech integration?

**Need to Research:**
- Claude API audio capabilities
- Mobile platform text-to-speech options
- Integration approaches

## Personal Health & Diet
*Source: notes-2025-12-25.md (2025-12-25 06:09)*

### Protein Shake Mono-Diet

**Q: What can I do if I only eat protein shakes for a month?**
- Status: Open
- Category: Health/Nutrition

**Question:**
What would be the effects and outcomes of consuming only protein shakes for a full month?

**Context:**
Discussed losing weight and the challenge of maintaining a strict diet with macro counting.

> "Discussed losing weight. I need a more strict diet. Count the macros etc. it feels really hard. I wonder what I can do if I only eat protein shakes for a month."

**Considerations:**
- Nutritional completeness - would this meet all dietary needs?
- Weight loss effectiveness
- Sustainability and adherence
- Health risks or concerns
- Energy levels and performance impact
- Comparison to other structured diet approaches

**Related:**
- Connected to weight loss goals
- Alternative to complex macro counting
- Simplified meal planning approach

**Need to Research:**
- Nutritional requirements vs. protein shake composition
- Medical/health implications
- Success/failure stories from others
- Professional nutritionist perspective
