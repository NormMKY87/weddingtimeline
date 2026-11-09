# Wedding 5 Proposal Follow-up: Inspection Report and Build Specification

Prepared 9 November 2026 for Norm, Norman Yap Photography.
Status: DRAFT ONLY. Nothing was published, activated, enrolled or sent.

Location: Norman Yap Photography, GoHighLevel location ID ZVcM39xSMGwBjGg7fLUQ, timezone Australia/Perth.

---

## 0. Read this first: what was and was not possible from this session

Two access routes were attempted for the workflow internals.

1. HighLevel connector, workflow definition API. Confirmed blocked. Every workflow definition call (search-workflows, get-workflow-definition, get-workflow-step-types) returned HTTP 403 with code WORKFLOW_API_NOT_ENABLED_FOR_LOCATION and the message "The workflow API is not enabled for location ZVcM39xSMGwBjGg7fLUQ. This is not a token or scope problem." No workflow write operation is exposed to this connection at all.
2. Browser editing of the signed-in GHL interface. Not available from this cloud session. No computer or Chrome profile is connected (Remote Control folder list is empty), and signing in to GHL from the container would require credentials, which is out of scope.

What this means:

- The three existing drafts were confirmed to exist, with names, status and version numbers, through the legacy workflow list endpoint (which is not gated). Their internal triggers, actions, waits and email copy could NOT be read.
- No workflow was edited. The requested changes are specified below step by step so they can be applied in the builder in one sitting, either by Norm or by a Claude session running on Norm's computer with Chrome.
- One CRM change WAS made through the supported connector: the missing opportunity field for the Dubsado proposal link was created (section 5). This is reversible and does not affect any workflow.

Activation remains blocked. See section 9 for the dependency list.

---

## 1. Workflows inspected

All three exist, all are status draft, none were changed.

| Workflow | Status | Version | Last updated | Link |
|---|---|---|---|---|
| Wedding 5: Proposal sent - decision-date review - DRAFT | draft | 4 | 2026-10-06 | https://app.gohighlevel.com/v2/location/ZVcM39xSMGwBjGg7fLUQ/automation/workflow/269743c2-f097-41aa-8638-e157484243c1 |
| Wedding 5D: Agreed proposal date - guarded follow-up - DRAFT | draft | 4 | 2026-10-06 | https://app.gohighlevel.com/v2/location/ZVcM39xSMGwBjGg7fLUQ/automation/workflow/ee2a18cc-3232-4f9f-a668-d5d78b339e5b |
| Wedding 5S: Reply hold or closed - stop proposal follow-up - DRAFT | draft | 4 | 2026-09-28 | https://app.gohighlevel.com/v2/location/ZVcM39xSMGwBjGg7fLUQ/automation/workflow/d97bda47-7a1a-4030-bde6-4dd0d53d6d8b |

Related workflows in the same family (for context, not edited):

| Workflow | Status | Relevance |
|---|---|---|
| Wedding 4: Consult held - proposal preparation - DRAFT | draft | Upstream. Likely where Proposal Sent Date would be stamped once the Dubsado handover exists. |
| Wedding 7: Norman-confirmed booked - sales handoff - DRAFT | draft | Downstream. Booking confirmation should also fire the stop logic. |
| Wedding 2: Enquiry follow-up day 2-5-8 - DRAFT | draft | Sibling pattern: guarded day 2 / 5 / 8 follow-up. |
| Wedding 2S: Reply or hold - stop enquiry follow-up - DRAFT | published | Sibling stop workflow. Despite the name it is live. The 5S design should mirror it. |

Which one contains the follow-up sequence: by naming convention, Wedding 5 is the main sequence (entry at Proposal Sent, decision-date review), Wedding 5D is the guarded path for couples who gave an agreed decision date, and Wedding 5S is the stop workflow. The six-email cadence belongs in Wedding 5. This could not be verified against the actual step list because the definitions are unreadable from here. If, on opening Wedding 5, the sequence already exists in 5D instead, build into 5D and leave Wedding 5 as the review-only workflow. Do not create a fourth workflow.

Evidence that guard logic already exists around this family (visible in CRM data, not in workflow definitions):

- Contact tag `wedding-proposal-followup-suppressed` exists and is applied to the QA contact "INTERNAL QA DelayedLookup Wedding Guards 20260928".
- A second QA contact "INTERNAL QA EmailAllowed Wedding Guards 20260928" carries `lc-client`. Both QA opportunities sit at 5. Proposal Sent, created 2026-09-28, the same day 5 / 5D / 5S were created.
- Opportunity field "Wedding Proposal Agreed Follow-up Date" (ID U03zxpcwuDlMIuaLkaJg, key opportunity.wedding_proposal_agreed_followup_date) exists, created 2026-09-28. This is almost certainly the anchor 5D uses.
- Opportunity field "Wedding Action State" (ID 2D4LQZ2mWM5qb3JjxuGq, TEXT) exists, created 2026-09-30.
- Contact fields "Wedding Email Marketing Permission" (uiHlcNUqWxNAEoriEWrg, options Granted / Not recorded / Declined or withdrawn) and "Wedding Email Permission Evidence" (aZytKXfURt8jC8aKA8rB) exist, created 2026-09-30.
- Other stop-related tags in the account: `esc-hold`, `replied-elsewhere`, `suppress-nurture`, `not-lead`.

These are the safeguards to preserve. Any conflict between them and the spec below is called out in section 7.

---

## 2. Pipeline and stage verification

Weddings pipeline 6Dvq9QGy1hahZHm62DWS, stages confirmed:

| Position | Stage | ID |
|---|---|---|
| 1 | 1. New Enquiry | 72949801-ee67-4435-9f20-4f69adba2dc7 |
| 2 | 2. Qualified and Contacted | 9326338f-8c69-41e7-942c-f92ac740d7e9 |
| 3 | 3. Consult Booked | 0db01576-2456-431d-a829-a443f92c6071 |
| 4 | 4. Consult Held | 02e04a51-7328-4960-b951-3620d5f8eea5 |
| 5 | 5. Proposal Sent | a13cf880-5de6-4d69-ae49-47e588b711c2 |
| 6 | 6. Negotiation / Follow-up | d47a8b4b-d3e3-4590-9b30-e6d36d45156b |
| 7 | 7. Booked | 0d44c89c-92ed-4472-a33f-5dad6c4cbc36 |
| 8 | Early Interest - Date/Venue Undecided | c48a259c-8300-4aaf-b93f-2eae01cc8d4e |

Location settings relevant to duplicates: allowDuplicateContact false, allowDuplicateOpportunity false, contact unique identifiers email and phone.

Live data check (read only, 9 November 2026): 8 open opportunities at 5. Proposal Sent (6 real couples plus the 2 QA records) and 2 at 6. Negotiation / Follow-up. Every one of them has an EMPTY custom field set. Proposal Sent Date is not being populated for any live opportunity today. This is the single biggest activation blocker (section 9).

---

## 3. Required schedule

Six emails, counted from the actual proposal send date, not from enrolment.

| Email | Day after send | Purpose |
|---|---|---|
| 1 | 2 | Check the proposal arrived, offer help |
| 2 | 5 | Questions or coverage adjustments |
| 3 | 8 | Offer to talk it through |
| 4 | 14 | Answer a useful common question |
| 5 | 21 | Have plans changed |
| 6 | 30 | Close the loop, invite a reply either way |

If the waits were built as relative gaps from the moment the previous email sends, they would be 2, 3, 3, 6, 7 and 9 days. The design below does NOT use relative gaps. It uses six absolute waits anchored to Proposal Sent Date, which is both more accurate and the mechanism that prevents late enrolment from firing a burst.

### 3.1 Anchoring to Proposal Sent Date: what is verified and what is not

Field: Proposal Sent Date, ID 3OdYb2HLLp197LbHJj8o, key opportunity.proposal_sent_date, type DATE (date only, no time).

Verified from HighLevel's current Wait action documentation:

- The wait type "A specific date and time" can pull its date "dynamically from a custom variable", with "On this date and time", "Before this date" or "After this date" plus a duration.
- Every date-based wait has an "If this date has already passed" setting with four options: Continue to next action, Go to specific step, Exit Contact from automation, Skip all outbound communication actions till next wait or event start date action.

Not verified from documentation:

- The article describes reading "a date from a contact field at runtime". It does not state whether an opportunity custom date field is selectable in the variable picker. In an opportunity-triggered workflow the opportunity fields are normally available as `{{opportunity.<key>}}` variables, but this must be confirmed in the builder before activation.
- Because the field is DATE not DATE_TIME, the anchor resolves to a time of day chosen by the platform (normally start of day in the workflow timezone). Combine with the Time Window (section 4) so emails land in business hours.

Decision rule: if the opportunity date field can be chosen in the wait step, build as specified. If it cannot, do not substitute a relative 2 / 3 / 3 / 6 / 7 / 9 day chain and call the cadence correct. Leave Wedding 5 unpublished and report the limitation. A contact-level mirror field would be a workable fallback but it must be populated by the same (currently missing) handover, so it does not remove the blocker.

### 3.2 How late enrolment is prevented from firing several emails together

Each of the six waits is "A specific date and time" = `{{opportunity.proposal_sent_date}}` + N days, where N is 2, 5, 8, 14, 21, 30. For every one of them set "If this date has already passed" to **Go to specific step** and point it at the Internal Review branch (section 4, step R). The effect: if a couple is enrolled on day 9, the day 2, 5 and 8 waits have all passed, so the contact goes straight to internal review and exits. No email fires. Norm decides whether to resume manually. Nothing is skipped silently.

Do not use "Continue to next action" on these waits. That is the setting that causes a burst.

---

## 4. Wedding 5 build specification (apply in the builder, save as draft)

### 4.1 Workflow settings

| Setting | Before (as inspected) | After (required) | Note |
|---|---|---|---|
| Status | Draft | Draft | Do not publish |
| Allow Re-Entry | Unknown, unreadable | OFF | Prevents a second run after completion or removal. See repeat-client limitation below. |
| Allow Multiple Opportunities | Unknown | ON | Each opportunity runs as its own instance, so `{{opportunity.*}}` merge fields bind to the opportunity that triggered the run, never a sibling opportunity on the same contact. Trigger filters restrict entry to the Weddings pipeline so ESE or album opportunities cannot enter. |
| Stop on Response | Unknown | ON | A reply to any message sent from this workflow ends the workflow for that contact. |
| Conversations: Mark as Read | Unknown | OFF | Replies must show as unread for the handover. |
| Time Window | Unknown | ON, 9:00 to 18:00, Monday to Saturday, Australia/Perth | Keeps date-anchored sends out of the small hours. Sunday excluded on the assumption Norm is shooting; adjust if wrong. |
| Sender details | Unknown | From name Norman Yap, from email hello@normanyap.com.au on the verified sending domain | Confirm the domain is verified under Settings, Email Services. |

Repeat-client limitation: with Allow Re-Entry OFF, a couple who went through this sequence once (for example a cancelled wedding, re-enquiring a year later on a new opportunity) will not re-enter automatically. Options: enrol them manually from the opportunity, or turn Allow Re-Entry ON and rely on the entry guard's tag check for duplicate protection. Recommendation: keep OFF for now and record the limitation. Note that re-entry is blocked anyway while a contact is still active in the workflow, so stage flapping and resends while the sequence is running never create a second instance regardless of this setting.

### 4.2 Trigger

Single trigger: **Pipeline Stage Changed**.

Filters:
- Pipeline: Weddings
- Moved to stage: 5. Proposal Sent

Do not add Opportunity Created or Opportunity Changed as additional triggers; they widen the duplicate surface. Do not use the native "Proposal / Estimate sent" trigger; proposals leave Dubsado, so it would never fire.

### 4.3 Entry guard (If / Else immediately after the trigger)

Branch "Eligible" requires ALL of:

1. Opportunity status is open
2. Opportunity pipeline stage is 5. Proposal Sent
3. Contact tag does not include `wedding-proposal-followup-suppressed`
4. Contact tag does not include `wedding-proposal-followup-active` (new tag, see 4.4)
5. Contact tag does not include `esc-hold`
6. Opportunity field Proposal Sent Date is not empty
7. Opportunity field Dubsado Proposal Link is not empty AND contains `https://`
8. Opportunity field Wedding Proposal Agreed Follow-up Date IS empty (if a date was agreed, 5D owns the couple, not this sequence)
9. Contact email is not empty
10. Contact DND for email is off
11. Contact field Wedding Email Marketing Permission is not "Declined or withdrawn" ("Granted" and "Not recorded" both pass; this is a service email about a proposal the couple requested, not marketing)

Else branch goes to **R. Internal Review** (4.6).

### 4.4 Housekeeping on entry

- Add contact tag `wedding-proposal-followup-active` (create this tag; it does not exist yet). It is the belt-and-braces duplicate lock across the whole family and lets 5S and 5D see that a sequence is running.
- Add note to the opportunity: "Wedding 5 proposal follow-up started. Anchor: Proposal Sent Date {{opportunity.proposal_sent_date}}."

### 4.5 The six email blocks

Repeat the following block six times with N = 2, 5, 8, 14, 21, 30.

**Wait N**: type "A specific date and time". Date = `{{opportunity.proposal_sent_date}}`, option "After this date", duration N days. If this date has already passed: **Go to specific step: R. Internal Review**.

**Guard N** (If / Else): identical to the entry guard conditions 1, 2, 3, 5, 7, 8, 9, 10, 11 (drop condition 4, the active tag is now expected to be present, and condition 6 is implied). Else branch goes to R.

Why the guard runs before EVERY email rather than relying on 5S alone: 5S removes the contact on events it can see. The guard also catches silent state, such as the stage having been moved to 6. Negotiation / Follow-up by hand, the proposal link being blanked, or permission being withdrawn, none of which may raise a trigger 5S listens for.

**Send Email N**: from hello@normanyap.com.au, subject and body from 02-email-copy-for-review.md, template type plain / simple HTML to match the W01 to W06 Enquiry templates. No typed sign-off (see 4.8).

**Note N**: add note to the opportunity "Proposal follow-up email N of 6 sent (day N)."

After Send Email 6 and Note 6: remove tag `wedding-proposal-followup-active`, add note "Proposal follow-up sequence completed, no reply recorded. No automated restart.", create task for Norman "Proposal follow-up finished without reply: decide next step" due 1 day, then End.

### 4.6 R. Internal Review branch (shared target)

1. Remove contact tag `wedding-proposal-followup-active`
2. Add note to the opportunity: "Wedding 5 paused for review. Reason check: stage {{opportunity.pipeline_stage}}, status {{opportunity.status}}, link {{opportunity.dubsado_proposal_link}}, agreed date {{opportunity.wedding_proposal_agreed_followup_date}}."
3. Create task assigned to Norman Yap (user Ko13QQZQi26XXoVZQz6d): "Proposal follow-up needs a human decision: {{contact.name}}" due same day
4. Internal notification: see section 6 for the recipient decision
5. End workflow for this contact

No path in R re-enters the sequence. A human decides.

### 4.7 Stage 6 Negotiation / Follow-up and the agreed-date hold

Leaving 5. Proposal Sent is not treated as lost.

- Moved to 6. Negotiation / Follow-up: the next Guard N fails on condition 2 and the couple goes to R (task for Norman, no email). This is deliberate: a human conversation is under way, automated chasing stops, nothing is marked lost.
- Agreed decision date entered (Wedding Proposal Agreed Follow-up Date set): the next Guard N fails on condition 8, the couple goes to R, and 5D takes over. Wedding 5 never overrides the agreed-date hold.
- Moved to 7. Booked, or status set to won / lost / abandoned: 5S removes the contact immediately (section 5). If 5S fires between a wait and a send, the guard also catches it.

### 4.8 Sender and signature

The existing Enquiry templates W01, W04, W05 and W06 were read from the template store. None of them types a sign-off or Norm's name; W04 ends on a question and W06 ends "I hope the day is everything you're picturing." That is strong evidence the hello@ signature is appended at send time, so the six new emails also carry no typed sign-off. Verify once in the builder by previewing a test send to the QA contact's conversation view (no delivery possible, the QA contact has no email) or by checking Settings, My Profile, Email Signature for the hello@ user. If no signature exists, add "Norman" as a single sign-off line to all six.

---

## 5. Wedding 5S stop workflow specification

5S internals could not be read. The list below is the required coverage. When opening 5S, keep every existing trigger and action. Add only what is missing. If an existing rule contradicts one of these, do not overwrite it; see section 7.

Triggers (each one leads to the same action chain):

1. Customer Replied. Filters: Reply channel = Email; Replied to workflow = Wedding 5: Proposal sent. Add a second Customer Replied trigger with Replied to workflow = Wedding 5D so an agreed-date couple's reply is handled the same way.
2. Pipeline Stage Changed: Weddings, moved to 7. Booked
3. Opportunity Status Changed: Weddings, status won
4. Opportunity Status Changed: Weddings, status lost
5. Opportunity Status Changed: Weddings, status abandoned
6. Contact Tag Added: `wedding-proposal-followup-suppressed`
7. Contact Tag Added: `esc-hold`
8. Contact Tag Added: `replied-elsewhere` (the couple replied by SMS, Instagram or phone, which Stop on Response in Wedding 5 cannot see)
9. Contact DND changed / Email unsubscribed (use the Contact DND trigger if available in this account; otherwise the Guard N condition 10 is the backstop)

Actions:

1. Remove from workflow: Wedding 5: Proposal sent
2. Remove from workflow: Wedding 5D: Agreed proposal date
3. Remove contact tag `wedding-proposal-followup-active`
4. Add note to opportunity: "Proposal follow-up stopped. Trigger: {{trigger name}}." (one note action per trigger branch if the builder cannot merge them)
5. If trigger was Customer Replied: create task for Norman "Reply received on proposal follow-up: {{contact.name}}" due same day, and send the internal notification (section 6)
6. End

Explicitly NOT included: any action that re-adds a contact to Wedding 5. No automated restart after a reply.

What a reply actually does, in order: Stop on Response ends Wedding 5 for that contact the moment GHL records the inbound reply. 5S then fires on Customer Replied and performs the cleanup and handover. If the reply arrives while an email is mid-dispatch, that email may still go out. There is no absolute zero-race guarantee and none is claimed.

Replies only count if they reach GHL. HighLevel's Customer Replied trigger fires on replies to messages sent from the CRM, routed back through the sending domain's reply tracking. A couple who replies to the Dubsado proposal email in their Gmail thread is replying to Dubsado, not to GHL, and will not stop the sequence unless two-way email sync is connected for hello@. Email sync status is unverified from this session (location defaultEmailService is blank). This is a required test, not an assumption (section 8).

---

## 6. Personalisation, link field and notification recipients

### 6.1 Field created in this session

Rechecked first: the full opportunity custom field list (38 fields) and contact custom field list (58 fields) were pulled live. No proposal link or proposal URL field existed on either model.

Created via the supported connector (locations.create-custom-field, HTTP 201):

| Property | Value |
|---|---|
| Name | Dubsado Proposal Link |
| Field ID | g1FTNfWYHrwx62fuXOMN |
| Merge key | opportunity.dubsado_proposal_link |
| Merge tag in emails | {{opportunity.dubsado_proposal_link}} |
| Model | opportunity |
| Data type | TEXT |
| Placeholder | Full Dubsado proposal URL for this couple, starting with https:// |
| Folder | AmNPwqZTcPMWbLEzNOcb (same folder as Proposal Sent Date) |

TEXT was chosen over URL because the API marks URL as Labs-only. The guard's "contains https://" check compensates. Population mechanism is unresolved (section 9).

### 6.2 Merge fields used in the emails

| Field | Source | Verified |
|---|---|---|
| {{contact.first_name}} | standard | yes |
| {{opportunity.dubsado_proposal_link}} | created above | yes, but empty for every live opportunity today |
| {{opportunity.proposal_sent_date}} | 3OdYb2HLLp197LbHJj8o | yes, but empty for every live opportunity today |

Partner's first name (contact.partners_first_name, 0rpvlOfwm838HdLH8kaO) exists and the Enquiry templates use it, but it is empty on several live contacts (Instagram leads). The six emails therefore say "you both" rather than merging the partner name, so no email can render "you and ,".

### 6.3 Notification recipients

Users on the location:

| User | Email | ID | Role |
|---|---|---|---|
| Norman Yap | hello@normanyap.com.au | Ko13QQZQi26XXoVZQz6d | agency admin, owner |
| Harper Bot | hello+harper@normanyap.com.au | 59LMFMppJHrJ4zS9eMdC | account admin, automation user created 2026-10-10 |

The existing 5S notification routing could not be read. Recommended routing for the handover notification: internal notification, type Email, to user Norman Yap only, plus the task assigned to Norman. Harper Bot is excluded on the assumption it is the connector identity, not a person. Left unresolved pending Norm's confirmation; no notification was configured or sent.

---

## 7. Conflicts and open design questions

1. Possible conflict: the existing `wedding-proposal-followup-suppressed` tag. The QA contact carrying it is tagged `lc-lead` and sits at Proposal Sent, which suggests the earlier design suppresses on lifecycle or permission grounds. The spec honours the tag as an absolute exit. If 5S or 5D currently ADD this tag on reply, that is compatible. If something currently REMOVES it automatically, that would contradict "no automated restart" and should be reviewed, not overwritten.
2. Possible conflict: Wedding 5 title says "decision-date review". If the current draft's purpose is a review-task-only workflow, adding six emails changes its purpose. Alternative: keep Wedding 5 review-only and build the six emails into 5D, renaming 5D's trigger logic. Decide on opening the drafts.
3. Permission interpretation: "Not recorded" permission is treated as allowed for proposal follow-up because the couple requested the proposal. If Norm wants "Granted" only, change Guard condition 11 to equals Granted.
4. Stage 6 behaviour: the spec stops automation and raises a task. If Norm would rather the sequence continue through Negotiation, drop condition 2 from Guard N only (keep it in the entry guard).
5. Sunday exclusion in the Time Window is an assumption.

---

## 8. Testing

### 8.1 Completed in this session (configuration and data, no sends)

| Test | Result |
|---|---|
| Three drafts exist, status draft, not published | Confirmed via workflow list |
| Pipeline and stage IDs match the brief | Confirmed |
| Proposal Sent Date field exists, type DATE, key correct | Confirmed |
| No proposal link field on contact or opportunity | Confirmed, then field created, ID g1FTNfWYHrwx62fuXOMN |
| Live opportunities at Proposal Sent have Proposal Sent Date populated | FAILED: all 8 are empty. Cadence cannot anchor until populated |
| Live opportunities have Dubsado Proposal Link populated | FAILED (expected, field is new): all empty |
| Location duplicate settings | allowDuplicateOpportunity false, allowDuplicateContact false |
| QA contact Z6eLU0KQFuPhCnTeX44q | Exists, no email, no phone, no tags, source "INTERNAL QA connector test, do not contact". Cannot prove delivery or reply detection |
| Existing template copy read for reuse | W01, W04, W05, W06 read; no typed sign-offs |
| Team user inventory | Norman Yap and Harper Bot only |
| Dubsado trigger inventory (Zapier catalogue, read only) | Contract Signed, Project Status Updated, New Project as Lead, New Project as Job, New Payment Received. No "proposal sent" trigger exists |
| HighLevel Wait step overdue options | Documented: Continue, Go to specific step, Exit, Skip outbound |

### 8.2 Outstanding (need the builder or a controlled live test with Norm's approval)

| Test | How | Approval needed |
|---|---|---|
| Opportunity date field selectable in "A specific date and time" wait | Open Wedding 5 in the builder, add the wait, open the variable picker | No |
| Overdue wait routes to R, not to the next email (late enrolment) | Enrol QA contact Z6eLU0KQFuPhCnTeX44q with Proposal Sent Date set 10 days ago; expect R task, zero sends | No (QA contact has no email) |
| Missing link exits to R | QA contact with Proposal Sent Date set, link blank | No |
| Duplicate entry: move QA card out of and back into Proposal Sent while active | Expect one instance only | No |
| Multiple opportunities: second Weddings opportunity on the same QA contact | Expect separate instance bound to its own opportunity | No |
| Real reply stops the sequence | Needs a real mailbox as recipient | YES, Norm must approve the test recipient |
| Reply during a wait | Same as above, reply between email 1 and email 2 | YES |
| Out-of-office auto-reply | Does an auto-responder trip Stop on Response and 5S? Needs a real mailbox with OOO on | YES |
| Signature / booking / decline stops it | Move QA card to 7. Booked, then mark lost, then add suppressed tag; expect 5S removal each time | No |
| Email sync: does a reply to a GHL email land in GHL Conversations for hello@ | Check Settings, Email Services and the Conversations inbox during the real-reply test | YES |
| Signature appended by sender profile | Preview or test send | Partly (preview is free) |

---

## 9. Unresolved dependencies (activation stays blocked until these are closed)

1. **Workflow editing access.** Either enable the workflow API for this sub-account (HighLevel controls this; the error says it is "available to selected sub-accounts only"), or apply this spec in the browser. Nothing in this document has been applied to any workflow.
2. **Proposal Sent Date population.** Zero live opportunities have it. Proposals are sent from Dubsado, so GHL cannot stamp it natively. Until something writes this field at send time, the cadence has no anchor.
3. **Dubsado Proposal Link population.** New field, empty everywhere. Same root cause.
4. **Dubsado to GHL handover for "proposal sent".** No Dubsado trigger for proposal sent exists in the Zapier catalogue. Options, none built: (a) Norm sets a Dubsado project status such as "Proposal Sent" and a Project Status Updated trigger writes the date and moves the GHL card; the proposal URL would still need to be pasted or mapped; (b) manual entry of both fields when moving the card to 5. Proposal Sent, with the entry guard refusing to run if either is blank; (c) the option Norm raised, a Claude session notifying the team and starting the GHL workflow when a proposal is sent. Recorded as an option only. No watcher, integration or notification was enabled.
5. **Dubsado signing or acceptance reaching the stop logic.** Dubsado's Contract Signed and New Payment Received triggers exist in Zapier and could set the GHL opportunity to 7. Booked or add a tag that 5S listens for. This integration does not exist today. Until it does, booking must be marked in GHL by hand for 5S to fire.
6. **Email sync and reply detection for hello@.** Unverified.
7. **Signature configuration.** Unverified, assumed appended.
8. **Notification recipient confirmation.** Norman proposed, not configured.

---

## 10. Confirmation

- No workflow was published, activated or edited.
- No contact or opportunity was enrolled in any workflow.
- No email, SMS or notification was sent.
- No test recipient was added.
- One custom field was created on the opportunity model (Dubsado Proposal Link, g1FTNfWYHrwx62fuXOMN). It holds no values.
- All read operations were against live CRM data; no records were modified.
