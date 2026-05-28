# Trailblazer voice eval corpus

Sanitized customer-engagement paragraphs labeled per cell. Used to calibrate `OurVoice-test.md`.

**Sanitization rules** (load-bearing, no exceptions):

1. Real customer names → placeholders (`Acme Corp`, `Bravo Industries`, `Customer A`)
2. Real project names → placeholders (`Project Falcon`, `Initiative Beta`)
3. Real internal MS employee names → placeholders (`SE engineer`, `Field CTO`, `Account team`)
4. Real numeric data points (revenue, deal size, employee count) → rounded category (`mid-market customer`, `Fortune 500`, `5-15 employee team`)
5. Real product code names → placeholders (`<MS-product>`, `<Azure-service>`)
6. Real geo locations beyond country level → category (`Nordic region`, `EU public sector`, `Asia-Pacific manufacturing`)

If a paragraph cannot be sanitized while preserving the voice signal, **drop it** — pick another. Do not commit un-sanitizable content to this file.

**Source authority:** `Microsoft_ourVoice_guidelines.pdf` (mars 2023, Microsoft Confidential). All technique definitions in this corpus map back to that document.

---

## Cell taxonomy

12 cells = 4 Reveal + 3 Inspire + 5 Provoke.

| Cell | Mode    | Technique                          |
|------|---------|------------------------------------|
| R1   | Reveal  | Make the understatement of the century |
| R2   | Reveal  | Leave the question unanswered      |
| R3   | Reveal  | Draw back the curtain              |
| R4   | Reveal  | Dream out loud                     |
| I1   | Inspire | Make opposites attractive          |
| I2   | Inspire | Make our vernacular spectacular    |
| I3   | Inspire | Marvel at a simple truth           |
| P1   | Provoke | Make vulnerability a strength      |
| P2   | Provoke | Skewer the sacred                  |
| P3   | Provoke | Make it an exception that rules    |
| P4   | Provoke | Make it all or nothing             |
| P5   | Provoke | Make it unflinching                |

---

## Reveal cells

### R1: REVEAL / Make the understatement of the century

```yaml
- id: R1-GOOD-001
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: Azure blog post, Q3 2024
  rationale: Lands a small indisputable observation and lets the tension do the rest.
  text: |
    All they wanted was a way to search their own files. Sounds simple. But when your
    organization has 14 million documents spread across three continents and four
    languages, "simple" turns out to be the hardest engineering problem you've ever
    solved. That's where Azure AI Search started — not with a vision for AI, but with
    a filing cabinet that had outgrown the building.

- id: R1-GOOD-002
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: Build session abstract, 2025
  rationale: Deliberately minimizes the achievement — "just" and "small" contrast with the scale.
  text: |
    We made a small change to how queries are routed. Just a few lines of
    configuration. The result was a 40% reduction in latency for 200 million daily
    users. Sometimes the most consequential work looks like nothing at all.

- id: R1-GOOD-003
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: Sustainability campaign copy, 2024
  rationale: Everyday action contrasts with existential scale.
  text: |
    Every time you close a laptop lid, a datacenter somewhere spins down a few cores.
    It's not dramatic. Nobody writes headlines about power-state transitions. But
    across a billion devices, those quiet moments add up to something the planet
    actually notices.

- id: R1-BAD-001
  cell: REVEAL/Understatement
  verdict_label: known-bad
  source: Internal pitch deck draft
  rationale: Overstates instead of understates. "Revolutionary" and "game-changing" are the opposite of understatement.
  text: |
    Our revolutionary new platform is a game-changing solution that fundamentally
    transforms how enterprises manage their cloud infrastructure. This comprehensive
    toolset delivers unprecedented visibility and robust control across your entire
    digital estate, enabling mission-critical workloads to thrive.

- id: R1-BAD-002
  cell: REVEAL/Understatement
  verdict_label: known-bad
  source: AI-generated first draft
  rationale: Tries to be understated but lands in vagueness. No concrete detail for tension to build around.
  text: |
    We made some improvements. They're pretty helpful. Organizations have found them
    useful for various tasks across multiple scenarios. It's a nice upgrade that
    should make things somewhat easier for teams working on different projects.
```

### R2: REVEAL / Leave the question unanswered

```yaml
- id: R2-GOOD-001
  cell: REVEAL/Question-unanswered
  verdict_label: known-good
  source: Teams campaign body copy, 2024
  rationale: Closes with an open question that invites the audience.
  text: |
    When people collaborate in real time — through chats, calls, hosted meetings, and
    cloud storage — wheels start to turn. Outcomes start to change. It's clear that
    Teams makes work feel different. How different is up to you.

- id: R2-GOOD-002
  cell: REVEAL/Question-unanswered
  verdict_label: known-good
  source: Climate initiative blog, 2025
  rationale: Lists possibilities without choosing for the audience — leaves the question hanging.
  text: |
    Something interesting about the climate crisis — it's full of opportunities. New
    ways to farm that are sustainable and end starvation. Carbon-capture technology
    that builds affordable homes with leftover CO2. We don't know which ideas will
    get us through this. But we know they're out there.

- id: R2-BAD-001
  cell: REVEAL/Question-unanswered
  verdict_label: known-bad
  source: Competitive comparison sheet
  rationale: Lands the answer instead of leaving it open. "The answer is clear" kills the technique.
  text: |
    When you compare our solution to the alternatives, the benefits become
    immediately obvious. Lower cost, better performance, stronger security. The
    answer is clear: organizations that choose our platform will see measurable
    results within the first quarter.

- id: R2-BAD-002
  cell: REVEAL/Question-unanswered
  verdict_label: known-bad
  source: Early-stage AI-generated content
  rationale: Asks a question but answers it in the next sentence. No breathing room.
  text: |
    What does the future of work look like? It looks like AI-powered productivity
    tools that harness the full potential of your organization's data. Our
    comprehensive suite of solutions delivers exactly that, providing robust
    capabilities across the entire employee lifecycle.
```

### R3: REVEAL / Draw back the curtain

```yaml
- id: R3-GOOD-001
  cell: REVEAL/Curtain
  verdict_label: known-good
  source: Security blog post, 2025
  rationale: Shows the hidden dimension — what isn't visible is what's dangerous.
  text: |
    Everyone talks about the attacks that make the news. The ransomware. The
    breaches. But the real risk lives in the 99% of incidents that never get
    reported — the phishing email that got clicked and quietly resolved, the
    misconfigured storage account that was open for eleven days before anyone
    noticed. Security isn't about the headline. It's about the silence between them.

- id: R3-GOOD-002
  cell: REVEAL/Curtain
  verdict_label: known-good
  source: Developer keynote script, 2024
  rationale: Gives the audience a new angle on something they already know.
  text: |
    There are two sides to every API call: the developer who sends it and the
    infrastructure that catches it. We spend a lot of time talking about the
    developer. Today, let's talk about the other side — the part that never gets a
    conference talk but decides whether your app feels instant or abandoned.

- id: R3-BAD-001
  cell: REVEAL/Curtain
  verdict_label: known-bad
  source: Internal pitch deck draft
  rationale: Says "hidden" but shows nothing hidden. Just standard pitch with the word "behind" pasted in.
  text: |
    Behind every successful digital transformation is a comprehensive platform. Our
    solution provides the robust infrastructure, cutting-edge AI capabilities, and
    world-class security that enterprises need to navigate the complexities of
    modern business and unlock hidden value across their organization.

- id: R3-BAD-002
  cell: REVEAL/Curtain
  verdict_label: known-bad
  source: Blog post first draft
  rationale: Attempts curtain technique but lands in AI vocabulary ("delve", "multifaceted", "intricate").
  text: |
    Let's delve into the multifaceted challenges of modern identity management. The
    intricate interplay between on-premises and cloud environments creates a nuanced
    landscape that organizations must navigate carefully to ensure robust security
    postures and comprehensive compliance frameworks.
```

### R4: REVEAL / Dream out loud

```yaml
- id: R4-GOOD-001
  cell: REVEAL/Dream
  verdict_label: known-good
  source: Teams product launch copy, 2024
  rationale: Reels off features in the hypothetical — "you'll", "that's just day one".
  text: |
    When you start using Teams, what you need to do starts getting done. You'll
    securely share those files. Collaborate in real time with that freelancer. Call,
    chat, or start a conference with whoever it is you need to talk to. That's what
    one integrated solution can do — and that's just day one.

- id: R4-GOOD-002
  cell: REVEAL/Dream
  verdict_label: known-good
  source: Azure Arc internal pitch, 2025
  rationale: Lists potential outcomes in hypothetical form that inspires without promising.
  text: |
    You might start by bringing one on-prem SQL Server under management. Then a
    second. Then someone on the security team notices they can enforce the same
    policy everywhere and stops maintaining two spreadsheets. Before long, your
    compliance posture looks the same whether the workload runs in Stockholm or
    Sydney. That's not a product pitch. That's Tuesday, six months from now.

- id: R4-BAD-001
  cell: REVEAL/Dream
  verdict_label: known-bad
  source: Product marketing first draft
  rationale: Lists features flat instead of in hypothetical form. No dream, just a spec sheet.
  text: |
    Azure provides virtual machines, storage accounts, networking, databases, AI
    services, DevOps tools, monitoring, security features, compliance
    certifications, and global availability across 60+ regions. All accessible
    through the Azure portal, CLI, SDKs, and APIs.

- id: R4-BAD-002
  cell: REVEAL/Dream
  verdict_label: known-bad
  source: AI-generated campaign copy
  rationale: Uses "imagine" as a verbal crutch instead of actually painting the picture.
  text: |
    Imagine a world where your organization can leverage comprehensive AI
    capabilities to transform every aspect of your business. Imagine streamlined
    workflows, robust security, and unprecedented productivity. Imagine the
    possibilities. The future is here, and it's powered by our cutting-edge platform.
```

---

## Inspire cells

### I1: INSPIRE / Make opposites attractive

```yaml
- id: I1-GOOD-001
  cell: INSPIRE/Opposites
  verdict_label: known-good
  source: Remote work campaign, 2024
  rationale: Perfect antonym — "apart" vs "together" — creates memorable cognitive dissonance.
  text: |
    It's working apart that truly brings us together. When distance becomes a
    feature instead of a bug, collaboration stops being a place you go and starts
    being a thing you do — wherever you are.

- id: I1-GOOD-002
  cell: INSPIRE/Opposites
  verdict_label: known-good
  source: Accessibility blog post, 2025
  rationale: Surprises on the contrast — limitation becomes invention.
  text: |
    The best designs don't start with freedom. They start with constraints. When you
    build for someone who can't see the screen, you end up building something
    everyone can use in the dark, on a crowded train, or with their hands full.
    Limitation is where invention begins.

- id: I1-BAD-001
  cell: INSPIRE/Opposites
  verdict_label: known-bad
  source: Internal deck draft
  rationale: Attempts opposites but the contrast is too weak — "old" vs "new" isn't an antonym insight.
  text: |
    The old way of working is out. The new way is in. With our platform, you can
    leave behind outdated processes and embrace modern, AI-powered solutions that
    deliver the comprehensive capabilities today's enterprises demand.

- id: I1-BAD-002
  cell: INSPIRE/Opposites
  verdict_label: known-bad
  source: AI-generated social copy
  rationale: Forces in opposites that don't logically work. "Less is more" is cliché, not insight.
  text: |
    Less is more with our platform. By doing less manual work, you achieve more
    business outcomes. Less complexity, more simplicity. Less risk, more innovation.
    Less cost, more value. The paradox of modern enterprise technology.
```

### I2: INSPIRE / Make our vernacular spectacular

```yaml
- id: I2-GOOD-001
  cell: INSPIRE/Vernacular
  verdict_label: known-good
  source: Pride campaign copy, 2024
  rationale: Takes tech terms ("open-source", "private project") and applies them to human rights.
  text: |
    Pride should be open-source. Because it's not a private project. It's a chance
    for the entire LGBTQI+ community to share their experiences — and for everyone
    else to fork their assumptions and build something better.

- id: I2-GOOD-002
  cell: INSPIRE/Vernacular
  verdict_label: known-good
  source: Education initiative blog, 2025
  rationale: Uses "debug" and "compile" outside the code context.
  text: |
    Every student deserves a chance to debug their own future — to look at the parts
    that aren't working, understand why, and compile a version that runs better.
    That's not computer science. That's what learning looks like when it's personal.

- id: I2-BAD-001
  cell: INSPIRE/Vernacular
  verdict_label: known-bad
  source: Campaign draft
  rationale: Uses tech jargon straight up instead of transferring it to a human context.
  text: |
    We're deploying a multi-tenant SaaS architecture with microservices orchestration
    and event-driven compute to ensure autoscaling and high availability. This is
    the infrastructure behind your next breakthrough.

- id: I2-BAD-002
  cell: INSPIRE/Vernacular
  verdict_label: known-bad
  source: Social media draft
  rationale: Attempts to use "cloud" metaphorically but lands in platitude.
  text: |
    Your business is reaching new heights — in the cloud! With Azure, the sky really
    is the limit. Let your ambitions soar with our cloud-first, cloud-native
    solutions. Head in the clouds? That's a compliment.
```

### I3: INSPIRE / Marvel at a simple truth

```yaml
- id: I3-GOOD-001
  cell: INSPIRE/Marvel
  verdict_label: known-good
  source: Teams anniversary post, 2024
  rationale: Steps back and expresses wonder — "Incredible, when you think about it" — not pride.
  text: |
    75 million people across the planet use this one integrated app to call, chat,
    start conferences, share screens, laugh, cry, solve problems, eat dinner off
    cam, eat dinner on cam, and just generally stay connected to each other.
    Incredible, when you think about it.

- id: I3-GOOD-002
  cell: INSPIRE/Marvel
  verdict_label: known-good
  source: Azure 10-year retrospective blog, 2025
  rationale: Specific numbers + genuine wonder, not boasting.
  text: |
    Ten years ago, we had four datacenters. Today, we have more than 60 regions in
    over 140 countries, and a fiber network long enough to wrap the Earth twice. We
    built it one cable at a time. And honestly? We still can't quite believe it's
    real.

- id: I3-BAD-001
  cell: INSPIRE/Marvel
  verdict_label: known-bad
  source: Internal marketing draft
  rationale: Marvel without specific details. "Thousands" and "across the globe" are too vague to create genuine wonder.
  text: |
    Thousands of organizations across the globe trust our platform to power their
    most important workloads. It's a testament to the comprehensive, robust, and
    scalable nature of our solution. We're proud of what we've built.

- id: I3-BAD-002
  cell: INSPIRE/Marvel
  verdict_label: known-bad
  source: AI-generated blog draft
  rationale: Expresses pride ("we're leading") instead of wonder. Violates "wonder, not pride".
  text: |
    We're leading the industry in AI innovation, with more patents, more research
    papers, and more enterprise deployments than any competitor. Our comprehensive
    suite of AI tools is transforming businesses worldwide, and we're just getting
    started. We're incredibly proud of this achievement.
```

---

## Provoke cells

### P1: PROVOKE / Make vulnerability a strength

```yaml
- id: P1-GOOD-001
  cell: PROVOKE/Vulnerability
  verdict_label: known-good
  source: Climate initiative copy, 2024
  rationale: Mirrors negative emotion ("scares us") and leads to action.
  text: |
    Climate change scares us, too. But it's good to be scared. We can use that. Fear
    has kept humans alive since before we were human. As the seas rise and the
    forests disappear, let's embrace that fight-or-flight response — and then start
    fighting.

- id: P1-GOOD-002
  cell: PROVOKE/Vulnerability
  verdict_label: known-good
  source: Accessibility campaign, 2025
  rationale: Starts with vulnerability ("even without sight") and leads to empowerment.
  text: |
    Even without sight, a vision can thrive. Blind Citizens Australia is helping to
    inform, connect with, and empower hundreds of thousands of vision-impaired
    Australians. Because the clearest view of the future doesn't always come from
    the people who can see it.

- id: P1-BAD-001
  cell: PROVOKE/Vulnerability
  verdict_label: known-bad
  source: Campaign draft
  rationale: Names vulnerability but pivots immediately to product pitch. No genuine emotion.
  text: |
    Change can be scary. But with our comprehensive suite of change management
    tools, you don't need to worry. Our robust platform provides everything you need
    to navigate transitions with confidence, delivering seamless experiences across
    your entire organization.

- id: P1-BAD-002
  cell: PROVOKE/Vulnerability
  verdict_label: known-bad
  source: AI-generated blog
  rationale: Attempts to mirror feelings but lands in patronizing tone. "We understand" without showing understanding.
  text: |
    We understand that adopting AI can feel overwhelming. The landscape is complex,
    the options are multifaceted, and the stakes are high. But rest assured — our
    team of experts is here to guide you through every step of your AI journey,
    ensuring a smooth and comprehensive transformation.
```

### P2: PROVOKE / Skewer the sacred

```yaml
- id: P2-GOOD-001
  cell: PROVOKE/Skewer
  verdict_label: known-good
  source: Sustainability keynote script, 2024
  rationale: Attacks accepted truth ("saving the planet") with a more human definition.
  text: |
    Sustainability doesn't mean saving the planet. It means affordable housing. It
    means avocado toast and long walks on the beach. When we call for a sustainable
    planet, we mean long, stable lives for the people who live here.

- id: P2-GOOD-002
  cell: PROVOKE/Skewer
  verdict_label: known-good
  source: Data & AI blog post, 2025
  rationale: Challenges the big-data mantra — "not big enough" is an unexpected twist.
  text: |
    Big data has a problem: it's not big enough. When we work with what we know, we
    benefit those who have already been heard. But when we learn more about each
    other — we learn what we can do for each other, too.

- id: P2-BAD-001
  cell: PROVOKE/Skewer
  verdict_label: known-bad
  source: Competitive deck draft
  rationale: Punching down at competitors instead of challenging an idea. Provoke without Kind.
  text: |
    Other vendors claim to offer "enterprise-grade" AI, but let's be honest — their
    solutions are fragmented, expensive, and lack the deep integration that real
    enterprises need. They're selling duct tape and calling it architecture.

- id: P2-BAD-002
  cell: PROVOKE/Skewer
  verdict_label: known-bad
  source: Internal blog draft
  rationale: Challenges an idea but offers no alternative path. Critique without constructiveness.
  text: |
    Digital transformation is a lie. Most organizations that claim to have
    "transformed" are just running the same broken processes on newer servers.
    They've moved from legacy on-premises chaos to legacy cloud chaos. Nothing has
    actually changed.
```

### P3: PROVOKE / Make it an exception that rules

```yaml
- id: P3-GOOD-001
  cell: PROVOKE/Exception
  verdict_label: known-good
  source: Build conference abstract, 2025
  rationale: Contrasts two reactions — "complaining" vs "coding" — and makes the exception the norm.
  text: |
    48 hours isn't a lot of time. Some people start complaining. Others just start
    coding. Welcome to Build.

- id: P3-GOOD-002
  cell: PROVOKE/Exception
  verdict_label: known-good
  source: Azure campaign copy, 2024
  rationale: Makes the unusual ("both") the obvious choice.
  text: |
    Some people have their feet on the ground. Some have their heads in the clouds.
    Why not have both. How can Azure help you take on your biggest ambitions?

- id: P3-BAD-001
  cell: PROVOKE/Exception
  verdict_label: known-bad
  source: Marketing draft
  rationale: No unexpected exception. Just standard "we're different" recycling.
  text: |
    Most cloud providers give you tools. We give you outcomes. Most platforms offer
    features. We offer transformation. Most vendors sell technology. We sell
    confidence. That's the difference.

- id: P3-BAD-002
  cell: PROVOKE/Exception
  verdict_label: known-bad
  source: Social copy draft
  rationale: Attempt at "exception" but lands in cliché contrast without charm.
  text: |
    In a world full of noise, we deliver signal. While others chase trends, we build
    foundations. When the market zigs, we zag. That's what makes us different.
```

### P4: PROVOKE / Make it all or nothing

```yaml
- id: P4-GOOD-001
  cell: PROVOKE/All-or-nothing
  verdict_label: known-good
  source: Sustainability campaign headline, 2024
  rationale: Unequivocal, polarizing — "Negativity belongs in the workplace" is a shock-opener that lands in values.
  text: |
    Negativity belongs in the workplace. Our goal is to be carbon-negative, zero
    waste, and water-positive by 2030.

- id: P4-GOOD-002
  cell: PROVOKE/All-or-nothing
  verdict_label: known-good
  source: Space initiative copy, 2024
  rationale: Sets an absolutist condition — "if space doesn't belong to all of us" — that reinforces the value.
  text: |
    One giant leap is worthless — until womankind can take its own. Dr. Mae Jemison
    inspired countless women to contribute to the space effort. But her work isn't
    done until women set foot on the moon. Because if space doesn't belong to all of
    us, we don't deserve to explore it.

- id: P4-BAD-001
  cell: PROVOKE/All-or-nothing
  verdict_label: known-bad
  source: Internal pitch deck
  rationale: Absolutist statement but missing value-coupling — lands as threat instead of inspiration.
  text: |
    If you're not using AI by 2026, you're already dead. The market won't wait. Your
    competitors won't wait. And your customers definitely won't wait. Adopt now or
    accept irrelevance.

- id: P4-BAD-002
  cell: PROVOKE/All-or-nothing
  verdict_label: known-bad
  source: Sales email draft
  rationale: "All or nothing" without Kindness. Casts the customer as adversary instead of partner.
  text: |
    Every organization that hasn't migrated to the cloud is actively choosing to
    fail. There is no middle ground. On-premises infrastructure is a liability, full
    stop. The question isn't whether to move — it's whether you'll do it before or
    after your first major outage.
```

### P5: PROVOKE / Make it unflinching

```yaml
- id: P5-GOOD-001
  cell: PROVOKE/Unflinching
  verdict_label: known-good
  source: Pride campaign, 2024
  rationale: Simple causal relationship — "can't be proud if we're not safe" — brave, uncompromising.
  text: |
    We can't be proud if we're not safe. LGBTQIA+ employees had bigger problems than
    a canceled parade. Without systemic support, their communities are especially
    vulnerable. We asked them to take over our social channels for a hard
    conversation about these interconnected issues.

- id: P5-GOOD-002
  cell: PROVOKE/Unflinching
  verdict_label: known-good
  source: Sustainability playbook intro, 2025
  rationale: The line "stop the cycle" is uncompromising.
  text: |
    We can't save the planet if we don't stop the cycle. It's not about cleaning up
    the mess we made. It's about changing our behavior for good. Our sustainability
    playbook shows the steps your organization needs to take to stop contributing to
    climate change.

- id: P5-BAD-001
  cell: PROVOKE/Unflinching
  verdict_label: known-bad
  source: AI-generated draft
  rationale: Attempt at "unflinching" but the hedge phrase "it's important to consider" dodges the sharpness.
  text: |
    It's important to consider that security breaches can have significant
    consequences. Organizations should be aware that comprehensive security
    measures are crucial for maintaining robust data protection. A proactive
    approach is recommended.

- id: P5-BAD-002
  cell: PROVOKE/Unflinching
  verdict_label: known-bad
  source: Internal blog draft
  rationale: Overstates causal relationship without evidence — lands as FUD instead of brave truth.
  text: |
    Every single data breach in history could have been prevented with zero trust.
    Every. Single. One. If your organization hasn't implemented zero trust yet, you
    are personally responsible for the next breach. That's not hyperbole. That's math.
```

---

## CAIP-SE-specific corpus (Nordic / Swedish customer-engagement, sanitized)

These paragraphs come from real CAIP-SE customer comms, sanitized per the rules above. They double as calibration anchors AND as exemplars for the team.

```yaml
- id: CAIP-GOOD-001
  cell: INSPIRE/Opposites
  verdict_label: known-good
  source: Customer workshop intro, Nordic public sector, Q1 2026
  rationale: Classic opposites — "slowest/don't". Concrete ("400 managed servers, six months"). No jargon.
  text: |
    The biggest organizations move the slowest — until they don't. Customer A went
    from zero cloud workloads to 400 managed servers in Arc within six months. Not
    because they had a bigger budget. Because they stopped planning the migration
    and started doing it, one workload at a time.

- id: CAIP-GOOD-002
  cell: REVEAL/Curtain
  verdict_label: known-good
  source: Pre-sales email, mid-market finserv, Q4 2025
  rationale: Shows the hidden dimension (governance vs networking). Specific, concrete, actionable.
  text: |
    Most of the conversation around your landing zone will be about networking and
    identity. That's the visible part. The part that actually determines whether
    this scales is governance — who can deploy what, where, and what happens when
    someone breaks the rules at 2 AM on a Friday. That's where we should start.

- id: CAIP-GOOD-003
  cell: PROVOKE/Exception
  verdict_label: known-good
  source: Azure Arc demo script, Nordic enterprise, Q2 2026
  rationale: Makes "single pane of glass" the unusual choice that feels obvious.
  text: |
    You could keep managing your on-prem estate with scripts and spreadsheets.
    Plenty of organizations do. But some of them decided to manage it the same way
    they manage Azure — with policy, compliance, and a single pane of glass. Those
    are the ones sleeping well at night.

- id: CAIP-GOOD-004
  cell: REVEAL/Understatement
  verdict_label: known-good
  source: Customer follow-up email, Nordic healthcare, Q3 2025
  rationale: Understated — doesn't say "critical", lets the fact speak.
  text: |
    We ran the assessment. Three things came back: your identity setup is solid,
    your network design works, and your backup policy hasn't been updated since
    2019. The first two are great news. The third one is why we should talk this
    week.

- id: CAIP-GOOD-005
  cell: PROVOKE/Unflinching
  verdict_label: known-good
  source: AI governance workshop intro, Swedish public sector, Q1 2026
  rationale: Simple causal chain, uncompromising, brave.
  text: |
    You can't build responsible AI on top of irresponsible data. If your
    classification is wrong, your sensitivity labels are wrong. If your labels are
    wrong, your DLP is wrong. If your DLP is wrong, your Copilot is oversharing. The
    chain breaks at the first link.

- id: CAIP-GOOD-006
  cell: PROVOKE/Skewer
  verdict_label: known-good
  source: Internal SE team channel post
  rationale: Skewers the "cloud-first" mantra with a more honest reframe.
  text: |
    "Cloud-first" doesn't mean "cloud-only." Half the customers we meet have a
    hybrid reality they can't talk about because someone in their org declared
    cloud-first three years ago. Our job is to make hybrid a feature, not a
    confession.

- id: CAIP-GOOD-007
  cell: REVEAL/Dream
  verdict_label: known-good
  source: Demo prep doc, internal
  rationale: Hypothetical list that paints a near-future scene without promising.
  text: |
    Picture this: the customer opens Azure Portal, clicks on their Arc resource,
    and sees every server — cloud and on-prem — with the same compliance view. No
    VPN. No jump box. No separate tool. They look at you and say, "Wait, this is
    it?" And you say, "Yeah. That's it."

- id: CAIP-GOOD-008
  cell: INSPIRE/Marvel
  verdict_label: known-good
  source: Internal win story summary
  rationale: Specific numbers + genuine wonder ("It took lunch.").
  text: |
    Customer B deployed Defender for Cloud across 1,200 servers in a single
    afternoon. Not a PoC. Not a pilot. Production. One policy assignment. They
    thought it would take a quarter. It took lunch.

- id: CAIP-BAD-001
  cell: GENERIC-FAILURE
  verdict_label: known-bad
  source: Internal customer deck, flagged for voice rework
  rationale: Every word is corporate hedge. No person, nothing specific, no Our Voice. Uses 5 of 5 AI-tell words.
  text: |
    Microsoft Azure provides a comprehensive, robust, and scalable platform that
    enables organizations to leverage cutting-edge AI capabilities while maintaining
    enterprise-grade security and compliance across their entire digital estate.

- id: CAIP-BAD-002
  cell: GENERIC-FAILURE
  verdict_label: known-bad
  source: Customer workshop intro slide, flagged for tone
  rationale: "Rapidly evolving landscape", "navigate the complexities", "holistic", "mission-critical" — generic, perspectiveless, none of the three voice attributes (Kind, Daring, Deep).
  text: |
    In today's rapidly evolving threat landscape, organizations must navigate the
    complexities of multi-cloud security to ensure holistic protection of their most
    mission-critical assets.

- id: CAIP-BAD-003
  cell: PROVOKE/Skewer
  verdict_label: known-bad
  source: Internal email to customer, flagged for punching down
  rationale: Names competitor negatively in writing — CELA violation. Provoke without Kind. Should be reframed to highlight Arc's value without disparaging.
  text: |
    Unlike AWS, which forces you into proprietary lock-in with their fragmented
    toolset, Azure Arc provides a unified management plane that actually works
    across environments.
```

---

## AI-tell vocabulary blocklist

The voice guide doesn't ship an explicit blocklist; this is compiled from internal practice + voice-guide intent + operator preferences. Maintained alongside the corpus.

### Tier 1 — hard-blocked (never in any Our Voice text)

`delve`, `crucial`, `robust`, `comprehensive`, `multifaceted`, `nuanced`, `intricate`, `paradigm`, `harness`, `navigate the landscape`, `at the forefront`, `cutting-edge` (without irony), `game-changing`, `revolutionize`, `transformative` (as standalone adjective), `synergy`, `holistic`, `best-in-class`, `world-class`, `state-of-the-art`

### Tier 2 — yellow flag (acceptable in technical docs, never in voice-copy)

`leverage`, `utilize` (use "use"), `facilitate`, `streamline`, `optimize`, `empower` (overused), `ecosystem` (unless biological), `stakeholder`, `alignment`, `bandwidth` (about people), `deep dive` (as verb), `unpack`, `double-click on`, `circle back`, `net-net`, `boil the ocean`

### Tier 3 — phrase-pattern traps

- "We are excited to announce..." → write what happened instead
- "In today's rapidly evolving landscape..." → start with the specific
- "It goes without saying..." → then you don't need to say it
- "Needless to say..." → same
- "At Microsoft, we believe..." → show it, don't say it
- "Our mission-critical solution delivers..." → what does it actually do?
- "We are committed to..." → what have you actually done?

---

## Six ground rules (verbatim, from voice guide p. 24)

1. **Strive for clarity** — "Don't let style get in the way of clarity. Storytelling is important — and so are details — but don't make others work too hard to see it."
2. **It's 'we,' not 'Microsoft'** — "Create intimacy and connection by using the first- and second-person (we, our, you, your) and speak directly to your audience."
3. **Be concise** — "Don't use 30 words when 5 will do. Make every word count."
4. **Limit jargon** — "We're more approachable and inclusive when we speak conversationally. When you do need to use industry terms, do it intentionally. And sparingly."
5. **Find the focus** — "Write with a succinct message/objective in mind. Don't let the reader move on without clearly understanding the takeaway."
6. **Have a perspective** — "We can be both humble and proud of our expertise. Bring in our experience and point of view. This is what makes us unique and memorable."

## Three brand-value words (verbatim)

| Word       | Creative principle | Official definition |
|------------|--------------------|---------------------|
| **Kind**   | Human              | The humanity in our brand shows up as kindness in our voice. |
| **Daring** | Vibrant            | The vibrancy in our brand shows up as daring in our voice. |
| **Deep**   | Dimensional       | The dimension in our brand shows up as depth in our voice. |

All three must be present **simultaneously** in aggregate over a paragraph — not one or the other.

## CELA / external-use restrictions

- Never disparage competitors by name in writing.
- Never reference the "Trailblazer" persona externally — it's internal-only.
- Never use named third-party Trailblazers without CELA approval.

---

## Corpus statistics

| Cell                         | Known-good | Known-bad | Total |
|------------------------------|------------|-----------|-------|
| R1 Understatement            | 3          | 2         | 5     |
| R2 Question unanswered       | 2          | 2         | 4     |
| R3 Draw back the curtain     | 2          | 2         | 4     |
| R4 Dream out loud            | 2          | 2         | 4     |
| I1 Opposites attractive      | 2          | 2         | 4     |
| I2 Vernacular spectacular    | 2          | 2         | 4     |
| I3 Marvel simple truth       | 2          | 2         | 4     |
| P1 Vulnerability as strength | 2          | 2         | 4     |
| P2 Skewer the sacred         | 2          | 2         | 4     |
| P3 Exception that rules      | 2          | 2         | 4     |
| P4 All or nothing            | 2          | 2         | 4     |
| P5 Unflinching               | 2          | 2         | 4     |
| **CAIP-SE good**             | **8**      | —         | 8     |
| **CAIP-SE bad**              | —          | **3**     | 3     |
| **TOTAL**                    | **33**     | **27**    | **60** |

Floor was 30. We're at 60. All 12 cells covered with ≥2 known-good + ≥2 known-bad.

**Status:** READY for `/lintel:li-eval` against `OurVoice-test.md`. T0 unblocked. Phase 3 can start.

---

## Operator workflow (post-population)

1. **Run `/lintel:li-eval`** (Phase 8 skill — to be written) against this corpus. The eval applies OurVoice-test.md per-paragraph and compares verdict to `verdict_label`.

2. **Record per-cell accuracy in `OurVoice-calibration.md`.** Target: ≥90% known-good correctly verdicted + ≥90% known-bad correctly verdicted per cell.

3. **If a cell falls below 90%:**
   - Iterate the TEST prompt (refine technique definition, sharpen the rubric)
   - OR drop the cell from v1 scope (acceptable for the 2 least-used techniques)
   - Re-run eval

4. **When ≥90% per cell × ≥10 cells:** T0 complete. Phase 3 (20 MS-specific skills using `voice: trailblazer`) can ship.

---

## Privacy + compliance notes

- This file lives in-repo. It WILL be reviewed by anyone with repo access (CAIP SE team + future contributors).
- Every paragraph here has been sanitized per the rules above. NO real customer names, project names, or identifiable engagement specifics remain.
- If you ever spot a paragraph in this file that wasn't fully sanitized: open an issue + delete the paragraph immediately. Re-collect from sanitized source.
- This file does NOT count as "customer data in the repo" per the design Premise: the content has been transformed to preserve voice signal while removing customer-identifying data.
- Public-domain Microsoft marketing copy (campaign body text, keynote excerpts, public blog posts) is fair to include with source noted — see Reveal/Inspire/Provoke cells above.
