# Todos

## Task Notification System
*Source: notes-2025-12-16.md (2025-12-16 01:55)*

- [ ] Design notification system architecture
  - Decide: Does it just notify constantly or be smarter?
  - Implement "is this active job done yet?" logic

- [ ] Implement job time estimates feature
  - Example: "fix the lightbulb" → estimate 15 minutes
  - Default assumption: most active tasks take ~30 minutes

- [ ] Build notification timing system
  - Notifications at: 30 minutes, 1 hour, 2 hours, 4 hours

- [ ] Add idle detection and notifications
  - Notify if no active task for 1 hour

- [ ] Optimize for engagement over input ease
  - Focus on "how much of the day do I have something?"
  - Make active task very vibrant and prominent

## LLM-Based Dinner Suggestion System
*Source: notes-2025-12-17.md (2025-12-17 01:30)*

- [ ] Design and create hierarchical food database structure
  - Define 10 general food categories
  - Define 10 subcategories per category
  - List 10 specific foods per subcategory (1,000 total)

- [ ] Extract and add metadata for each food
  - Spicy/not spicy classification
  - Hot/cold dish classification
  - Other relevant attributes

- [ ] Build relationship mappings
  - "Might also like" lists (~10 items per food)
  - "Might also dislike" lists (~10 items per food)

- [ ] Design interactive selection interface
  - Random selection algorithm (4 items → present 2)
  - Binary choice UI
  - Rejection reasoning input

- [ ] Implement filtering logic
  - Parse user rejection reasons
  - Identify commonalities between rejected items
  - Filter database based on learned preferences

## MAPS Community Organization
*Source: notes-2025-12-17.md (2025-12-17 09:30)*
*Updated: notes-2025-12-25.md (2025-12-25 06:22)*

- [ ] Follow up with Sister Mallak for volunteer confirmations
  - Need 2-3 volunteers for Open Mosque event on 1/24
  - Sr Mallak actively getting interested people
  - Also coordinating marketing with Sr Saraa

- [x] Explore mocktail event co-hosting with Saqib
  - Message scheduled, expecting response tomorrow
  - Saqib is somewhat interested in hosting
  - Could serve as exposure to community building

- [ ] Consider organizing own mocktail event
  - Use as leadership development and recruiting tool

- [ ] Set up follow-up tracking system for pending items from different people
  - Make explicit what is pending and from whom
  - Keep running tally in notes format

## Follow-Up Automation System
*Source: notes-2025-12-17.md (2025-12-17 09:30)*

- [ ] Research WhatsApp automation methods
  - Multiple ways exist to automate WhatsApp

- [ ] Explore Apple Shortcuts for text messaging automation
  - Can potentially write to scratchpad and send messages

- [ ] Design scratchpad-based message sending system
  - Write to scratchpad → trigger outbound messages

- [ ] Investigate shortcut-to-app/table integration
  - Can shortcut query a table and send messages directly?

## Camera App Development
*Source: notes-2025-12-21.md (2025-12-21 14:30)*

- [ ] Show Aafiyah the candidate names for camera app
  - Refined the app during Whistler trip

## Pacemaker Improvements
*Source: notes-2025-12-21.md (2025-12-21 14:30)*

- [ ] Enhance pacemaker notification system
  - Need something that pings more frequently
  - Current system not engaging enough

- [ ] Implement pacemaker changes
  *Source: notes-2025-12-25.md (2025-12-25 06:09)*
  - Haven't looked at for a while
  - Need to get back to implementing changes

## Open Mosque Project
*Source: notes-2025-12-22.md (2025-12-22 18:13)*
*Updated: notes-2025-12-25.md (2025-12-25 06:22)*

**Priority:** High
**Status:** In Progress

**Event Details:**
- Training: 1/8 7PM ✅ Confirmed
- Event: 1/24 1:30PM ✅ Confirmed
- Capacity: 60 people (MPR room limit)
- Agenda: 1:30-2:00 Open Social, 2:00-3:00 Talk, 3:00 Asr, After Asr Tour, End 3:30

**Immediate Tasks:**
- [ ] Check on marketing status with Sr Mallak (deadline was 12/19)
  - Sr Mallak working with Sr Saraa on marketing

- [x] Follow up on final date confirmation from Sr Alejandra
  - Confirmed on 2025-12-25: Training and event dates now confirmed

- [ ] Follow up with Sr Mallak on volunteer confirmations
  - Need 2-3 volunteers for day of event
  - Sr Mallak actively getting interested people

- [ ] Begin inviting immediate circle to event
  - Have dates, can start outreach

- [ ] Manage invite list for open mosque in Claude Code notes
  - Track people to invite using notes system

**Other Coordination (Others' Responsibilities):**
- Ibrahim getting tour script from Sr Oraib
- Imam Adam preparing presentation
- Committee (incl. Sr Alejandra) providing feedback on presentation

## Personal Projects

### Kids Camera with Aafiyah
*Source: notes-2025-12-22.md (2025-12-22 18:13)*

**Priority:** High
**Status:** In Progress

- [ ] Get kids camera to initial better version
  - Focus on a few basic things that work
  - Close on the project with Aafiyah 💗💖

### Pacemaker Development
*Source: notes-2025-12-22.md (2025-12-22 18:13)*

**Priority:** High - Critical for sleep schedule and daily productivity
**Status:** In Progress

- [ ] Get pacemaker to a good spot
  - It's close to what's needed
  - Address issues with being off pace
  - Key for sleeping on time

## Personal Management

### Laptop Backlog
*Source: notes-2025-12-22.md (2025-12-22 18:13)*

- [ ] Clear out laptop backlog
  - Has been challenging to get cleared

### Dad Interview
*Source: notes-2025-12-22.md (2025-12-22 18:13)*
*Updated: notes-2025-12-25.md (2025-12-25 06:29)*

- [x] Schedule time with dad for interview
  - Completed: Used otter.ai for the interview, worked well
  - Me and him don't work well with calendars
  - Found approach that worked for both

### Distraction Accountability Experiment
*Source: notes-2025-12-22.md (2025-12-22 18:13)*

- [ ] Try selfie accountability system for distractions
  - Take selfie picture every time opening a distraction
  - Test today to see if brings needed accountability

## Future Integrations
*Source: notes-2025-12-16.md (2025-12-16 01:55)*

- [ ] Integrate with workout tracking
  - Active workout becomes "the thing"

- [ ] Integrate with prayer time reminders
  - Prayer time becomes "the thing"

- [ ] Integrate with calendar
  - Calendar events become "the thing"

## Notes Processing Workflow
*Source: notes-2025-12-23.md (2025-12-23 16:00)*

**Priority:** Medium
**Status:** In Design

- [ ] Create slash command for review/audit/scheduling
  - Process notes into actionable schedule
  - Generate time blocks for tasks
  - Output structured schedule

- [ ] Implement iOS Shortcuts integration
  - Connect to calendar for time blocking
  - Add items to reminders automatically
  - Enable automated scheduling from notes

- [ ] Test simplified implementation plan workflow
  - Use /implement to write to markdown files directly
  - Skip Chatter integration complexity
  - Write to `userstory-implementation-plan.md` format

## Claude Mobile
*Source: notes-2025-12-23.md (2025-12-23 16:00)*

- [ ] Figure out how to get Claude for mobile to provide audio/talk
  - Investigate if it's via API call
  - Determine technical approach for voice output

## Tools & Integrations

### mdql
*Source: notes-2025-12-25.md (2025-12-25 06:09)*

**Priority:** High - marked as "first on the todo list"
**Status:** Not Started

- [ ] Try out mdql
  - "Mdql could be cool. I should try it out."
  - "First on the todo list. That's the most basic one."

### CLAUDE.md Sharing
*Source: notes-2025-12-25.md (2025-12-25 06:09)*

**Priority:** Medium
**Status:** Not Started

- [ ] Post CLAUDE.md file on Twitter
  - Good discussion on Twitter about using md files
  - Share CLAUDE.md file as reference for others

## Personal Health

### Weight Loss & Diet
*Source: notes-2025-12-25.md (2025-12-25 06:09)*

**Priority:** Medium
**Status:** Planning

- [ ] Implement strict diet with macro counting
  - "I need a more strict diet. Count the macros etc."
  - Feels really hard but necessary

## Photo Lab - Kids Camera Project
*Source: notes-2025-12-26.md (2025-12-26)*

**Priority:** High
**Status:** In Progress - First version working

**Core System:**
- [x] Complete first version with 30 challenges
- [x] Integrate OpenAI for photo evaluation

**Feature Development:**

- [ ] Implement multi-model comparison system
  - Capture each photo submission
  - Get evaluations from OpenAI, Gemini, and Grok
  - Store results for comparison
  - Analyze which model provides best feedback for kids

- [ ] Research and implement on-device ML
  - Explore iOS native image processing capabilities
  - Train on-device model for photo feedback
  - Implement privacy-preserving evaluation
  - Test performance vs cloud models

- [ ] Design and implement contrast challenges
  - Create challenge type that requires two photos
  - Build comparison UI (zoomed in vs out, different angles)
  - Design evaluation criteria for comparison challenges
  - Add to challenge library

- [ ] Add camera feature challenges
  - Focus adjustment challenge
  - Grayscale/black-and-white mode challenge
  - Portrait mode challenge
  - Other iPhone camera feature challenges

- [ ] Build crowdsourced challenge system
  - Design challenge submission interface
  - Create review/moderation system
  - Implement challenge approval workflow

- [ ] Consider skill tree / progression system
  - Evaluate if prerequisite challenges needed
  - Consider splitting intermediate into two levels
  - Design progression visualization
  - Decision: strict tree vs flexible levels

- [ ] Implement challenge variations system
  - Design variation management
  - Create color variation set (red, black, white, green, blue)
  - Create shape variation sets
  - Build UI for presenting variations

- [ ] Build multi-level privacy & content filtering
  - **On-device filter:**
    - Research iOS content detection APIs
    - Implement face detection → block save
    - Implement nudity detection → block save
    - Implement people detection filter
    - Implement weapons/violence detection
  - **AI judge filter:**
    - Add content flagging to evaluation prompt
    - Create secondary review system
    - Handle flagged content appropriately

- [ ] Implement indoor/outdoor mode system
  - Detect or allow manual selection of environment
  - Create indoor challenge set
  - Create outdoor challenge set
  - Tag challenges as indoor-only/outdoor-only/either
  - Adjust clues based on environment

- [ ] Build parent's report & progress tracking
  - Design report UI
  - **Visual progression:**
    - Show early vs recent photos
    - Create side-by-side comparison view
    - Build timeline visualization
  - **Abstract skill metrics:**
    - Implement focus quality scoring
    - Implement brightness/exposure analysis
    - Implement composition evaluation
    - Implement interestingness/creativity scoring
    - Create trend analysis: before vs after
  - **Feedback summary:**
    - Aggregate all feedback data
    - Identify strength areas
    - Identify improvement areas
    - Generate personalized recommendations
  - **Variation suggestions:**
    - Link weaknesses to specific variation sets
    - Suggest targeted practice challenges
  - **Parent feedback collection:**
    - Create parent survey
    - Track: Did app help child improve?
    - Track: Was it fun?
    - Track: Were kids engaged?
    - Collect satisfaction metrics

**Testing & Feedback:**

- [ ] Create concrete feedback form for Aafiyah
  - Design structured feedback questions
  - Include challenge rating system
  - Add fun/engagement assessment

- [ ] Get Aafiyah to test and provide feedback
  - Share feedback form
  - Review and incorporate feedback

- [ ] Prepare beta testing group
  - Contact Zia (Aizat's daughter)
  - Contact Irdina (Aimi's daughter)
  - Contact Malik (Nik's son)
  - Contact Hamza (Saqib's son)
  - Contact Alora (Lawrence's daughter)

- [ ] Conduct beta testing with friends' kids
  - Distribute app to beta testers
  - Collect ratings and feedback
  - Monitor engagement
  - Address issues found

- [ ] Collect parent feedback from beta testers
  - Share parent survey
  - Analyze satisfaction metrics
  - Iterate based on parent input
