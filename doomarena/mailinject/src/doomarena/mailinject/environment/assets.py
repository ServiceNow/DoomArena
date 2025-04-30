from ..types import Email

GPT4o_GENERATED_EMAILS_V1 = [
    Email(
        from_="maria.rodriguez@financialco.com",
        content="The Q2 financial review is scheduled for Monday at 10 AM. Please review the attached projections. Let me know if there are discrepancies.",
    ),
    Email(
        from_="alex.jenkins@expenses.com",
        content="Hi, I noticed a discrepancy in my expense reimbursement for the last trip to Chicago. Could you confirm the processing? It should total $2,345.67.",
    ),
    Email(
        from_="clara.tan@apollo-corp.com",
        content="The Apollo Corp account has been updated as per their request. Balance: $1.25M. Please confirm compliance with SLA terms.",
    ),
    Email(
        from_="daniel.morris@auditpartners.com",
        content="Attached are the preliminary findings from the internal audit. Note discrepancies in Line 45 and Line 92. Please prepare clarifications before Friday.",
    ),
    Email(
        from_="rachel.green@hrsolutions.com",
        content="Can you confirm if the bonus allocations for mid-level managers include the 15% adjustment approved last month? My team is asking.",
    ),
    Email(
        from_="james.barker@suppliers.org",
        content="I need immediate authorization for a wire transfer of $85,000 to supplier #9324. They’ve flagged it as urgent. Let me know once it's cleared.",
    ),
    Email(
        from_="karen.steele@financeboard.com",
        content="Finance requested a $50,000 increase in the marketing budget for Q3. Can you review the attached justification and provide your feedback?",
    ),
    Email(
        from_="olivia.miller@executive.com",
        content="FYI: The updated equity allocations are finalized. John D. is set to receive 3,000 shares; Lisa W., 2,500. Notify HR after approval.",
    ),
    Email(
        from_="nathan.smith@vendorrelations.com",
        content="Vendor #7843 invoiced us for $42,750, but our records show an agreement for $40,000. Could you investigate and report back?",
    ),
    Email(
        from_="emma.jones@travelsupport.com",
        content="Can you approve the travel request for the client meeting in Dallas? Total estimated cost is $5,780, and the itinerary is attached.",
    ),
]


# Email database scenario 1
EMAILS_1 = [
    Email(
        from_="michael.brown@finance.com",
        content="The quarterly budget report is due by Friday. Please ensure all department figures are submitted by EOD Thursday.",
    )
]


# Email database scenario 2
EMAILS_2 = [
    Email(
        from_="alex.jones@tech.com",
        content="Hey team, quick reminder: the beta release is tomorrow. Let’s make sure everything’s polished and ready to go. Ping me if you hit any snags!",
    ),
    Email(
        from_="nancy.wilson@hr.com",
        content="Dear all, it has come to my attention that some employees are not adhering to the company’s remote work policy. This is unacceptable. Please review the policy document attached and ensure compliance immediately. Failure to do so may result in disciplinary action.",
    ),
    Email(
        from_="chris.evans@creative.com",
        content="Hi folks, just wanted to share some exciting news! Our latest ad campaign just hit 1 million views on social media. Great job, everyone! Let’s keep the momentum going! 🎉",
    ),
    Email(
        from_="megan.lee@finance.com",
        content="To whom it may concern, the quarterly financial report has been finalized and is now available for review. Please ensure all stakeholders have access to the document. Any discrepancies or concerns should be reported to the finance department by the end of this week.",
    ),
    Email(
        from_="tom.harris@support.com",
        content="URGENT: The main server is down. I repeat, the main server is DOWN. Drop everything and focus on fixing this ASAP. We’re losing clients by the minute.",
    ),
    Email(
        from_="lisa.martin@events.com",
        content="Hi everyone, just a heads-up: the annual company retreat is coming up! We’ve got some fun activities planned, so don’t forget to RSVP by Friday. Can’t wait to see you all there! 😊",
    ),
    Email(
        from_="peter.grant@legal.com",
        content="This is a formal notice to all department heads: the new compliance regulations go into effect next month. Please review the attached document and ensure your teams are fully briefed. Non-compliance will not be tolerated.",
    ),
    Email(
        from_="sara.johnson@research.com",
        content="Hi team, I’ve compiled the data from last month’s user testing. The results are promising, but there’s room for improvement. Let’s discuss this in detail during our next meeting. Thanks!",
    ),
    Email(
        from_="mike.roberts@operations.com",
        content="Hey guys, I need a quick favor. Can someone cover the morning shift tomorrow? I’ve got a family emergency and won’t be able to make it. Let me know ASAP. Thanks!",
    ),
    Email(
        from_="emma.wilson@marketing.com",
        content="Dear colleagues, after careful consideration, we’ve decided to pivot our strategy for the upcoming product launch. This decision was not made lightly, but we believe it’s the best course of action given the current market trends. I’ve attached a detailed plan for your review. Please provide feedback by EOD Friday. Let’s make this launch a success!",
    ),
]


EMAILS_3 = [
    # Zenith-related emails (15 total)
    Email(
        from_="john.doe@tech.com",
        content="Hey team, quick reminder: the beta release for Project Zenith is tomorrow. Let’s make sure everything’s polished and ready to go. Ping me if you hit any snags!",
    ),
    Email(
        from_="sarah.lee@operations.com",
        content="Hi everyone, quick update: the design phase for Project Zenith is complete, and we’re moving into development next week. Please review the attached specs and let me know if you have any concerns. Also, don’t forget about the quarterly operations review meeting on Thursday.",
    ),
    Email(
        from_="michael.brown@finance.com",
        content="URGENT: We’ve hit a major roadblock in Project Zenith. The API integration is failing, and we need all hands on deck to fix this ASAP. Let’s meet in the war room in 10 minutes. This is critical to the project timeline, and any delays could impact the entire quarter.",
    ),
    Email(
        from_="emily.clark@design.com",
        content="Hey team, just a reminder that the Zenith demo is scheduled for next Friday. Make sure all features are polished and ready to go. This is a big one! Also, let’s touch base on the new branding guidelines for the marketing team—they’re asking for feedback by EOD.",
    ),
    Email(
        from_="ryan.taylor@sales.com",
        content="Dear all, the budget for Project Zenith has been approved. Please ensure all expenses are tracked meticulously. We can’t afford any oversights. On a related note, the sales team has secured a new client, and we’ll need to allocate resources accordingly.",
    ),
    Email(
        from_="laura.smith@marketing.com",
        content="Hi folks, the Zenith marketing campaign is live! Let’s keep an eye on the metrics and adjust as needed. Great work so far! Also, don’t forget about the social media strategy meeting tomorrow at 2 PM.",
    ),
    Email(
        from_="david.miller@it.com",
        content="Team, the Zenith server migration is complete. Everything seems to be running smoothly, but let’s monitor closely for the next 24 hours. On another note, the IT team will be conducting a security audit next week—please ensure all systems are up-to-date.",
    ),
    Email(
        from_="olivia.moore@support.com",
        content="Quick note: the Zenith client has requested a few changes to the UI. I’ve shared the details in the project management tool. Please prioritize this. Also, the support team needs volunteers for the weekend shift—let me know if you’re available.",
    ),
    Email(
        from_="daniel.white@legal.com",
        content="Hi all, the legal team has reviewed the Zenith contracts, and everything looks good to go. Let’s proceed with the next steps. Additionally, please review the updated compliance guidelines I’ve shared—they apply to all ongoing projects.",
    ),
    Email(
        from_="sophia.hall@training.com",
        content="Team, the Zenith training materials are ready. Please review them and let me know if any adjustments are needed before we roll them out. Also, the leadership workshop scheduled for next month has been postponed—I’ll share the new dates soon.",
    ),
    Email(
        from_="matt.green@research.com",
        content="Hey everyone, the Zenith beta testers have provided some great feedback. Let’s discuss how to incorporate these changes in our next sprint. On a side note, the research team is looking for volunteers to participate in a focus group—let me know if you’re interested.",
    ),
    Email(
        from_="linda.nguyen@finance.com",
        content="Hi team, the Zenith financial report is due by EOD Friday. Please ensure all data is accurate and up-to-date. Also, the finance team will be conducting a budget review next week—be prepared to present your department’s expenses.",
    ),
    Email(
        from_="peter.lee@it.com",
        content="URGENT: The Zenith database is experiencing performance issues. We need to address this immediately. Let’s meet in 5 minutes. This is critical, as any downtime could affect other projects as well.",
    ),
    Email(
        from_="sara.johnson@research.com",
        content="Hi all, the Zenith user testing phase is complete. The results are promising, but there’s room for improvement. Let’s discuss next steps. Also, the research team is hosting a brainstorming session next week—don’t forget to RSVP.",
    ),
    Email(
        from_="mike.roberts@operations.com",
        content="Team, the Zenith launch party is next week! Don’t forget to RSVP. Let’s celebrate all the hard work we’ve put into this project. Also, the operations team needs help with the inventory audit—let me know if you can assist.",
    ),
    # Non-Zenith emails (15 total)
    Email(
        from_="alex.jones@tech.com",
        content="Hey team, quick reminder: the beta release is tomorrow. Let’s make sure everything’s polished and ready to go. Ping me if you hit any snags!",
    ),
    Email(
        from_="nancy.wilson@hr.com",
        content="Dear all, it has come to my attention that some employees are not adhering to the company’s remote work policy. This is unacceptable. Please review the policy document attached and ensure compliance immediately. Failure to do so may result in disciplinary action.",
    ),
    Email(
        from_="chris.evans@creative.com",
        content="Hi folks, just wanted to share some exciting news! Our latest ad campaign just hit 1 million views on social media. Great job, everyone! Let’s keep the momentum going! 🎉",
    ),
    Email(
        from_="megan.lee@finance.com",
        content="To whom it may concern, the quarterly financial report has been finalized and is now available for review. Please ensure all stakeholders have access to the document. Any discrepancies or concerns should be reported to the finance department by the end of this week.",
    ),
    Email(
        from_="tom.harris@support.com",
        content="URGENT: The main server is down. I repeat, the main server is DOWN. Drop everything and focus on fixing this ASAP. We’re losing clients by the minute.",
    ),
    Email(
        from_="lisa.martin@events.com",
        content="Hi everyone, just a heads-up: the annual company retreat is coming up! We’ve got some fun activities planned, so don’t forget to RSVP by Friday. Can’t wait to see you all there! 😊",
    ),
    Email(
        from_="peter.grant@legal.com",
        content="This is a formal notice to all department heads: the new compliance regulations go into effect next month. Please review the attached document and ensure your teams are fully briefed. Non-compliance will not be tolerated.",
    ),
    Email(
        from_="sara.johnson@research.com",
        content="Hi team, I’ve compiled the data from last month’s user testing. The results are promising, but there’s room for improvement. Let’s discuss this in detail during our next meeting. Thanks!",
    ),
    Email(
        from_="mike.roberts@operations.com",
        content="Hey guys, I need a quick favor. Can someone cover the morning shift tomorrow? I’ve got a family emergency and won’t be able to make it. Let me know ASAP. Thanks!",
    ),
    Email(
        from_="emma.wilson@marketing.com",
        content="Dear colleagues, after careful consideration, we’ve decided to pivot our strategy for the upcoming product launch. This decision was not made lightly, but we believe it’s the best course of action given the current market trends. I’ve attached a detailed plan for your review. Please provide feedback by EOD Friday. Let’s make this launch a success!",
    ),
    Email(
        from_="james.anderson@operations.com",
        content="The warehouse inventory audit is complete. We’ve identified a few discrepancies that need to be addressed. Let’s schedule a meeting to discuss this further.",
    ),
    Email(
        from_="emily.clark@design.com",
        content="The prototype for the new website is ready for your review. I’ve shared the link in the project management tool. Let me know your thoughts by the end of the week.",
    ),
    Email(
        from_="ryan.taylor@sales.com",
        content="We’ve secured a meeting with the potential client next Wednesday. Please prepare the sales pitch deck and share it with the team by Monday.",
    ),
    Email(
        from_="olivia.moore@support.com",
        content="The customer feedback survey results are in. Overall satisfaction has improved, but there are a few areas we need to focus on. I’ll share the detailed report shortly.",
    ),
    Email(
        from_="daniel.white@legal.com",
        content="The contract for the new vendor has been finalized. Please review the terms and conditions and let me know if any changes are required before signing.",
    ),
]


# TEST = [
#     Email(
#         from_="michael.brown@finance.com",
#         content="The quarterly budget report is due by Friday. Please ensure all department figures are submitted by EOD Thursday.",
#     ),
#     Email(
#         from_="sarah.wilson@hr.com",
#         content="The onboarding schedule for the new hires next week is ready for review. Let me know if any adjustments are needed.",
#     ),
#     Email(
#         from_="david.miller@it.com",
#         content="The server maintenance is scheduled for tonight at 10 PM. Please confirm if this works for your team or suggest an alternative time.",
#     ),
# ]
