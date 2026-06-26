# Phishing Lure Template Audit

**Scope:** all 89 lure templates (emails, SMS mockups, QR/quishing, and the credential-harvest landing page). Each was scored 1–5 for *click-worthiness* — how convincing it would be to a real employee — with concrete improvement recommendations. The education/training pages are out of scope here (they are covered by the styling work).

> Context: these are authorized security-awareness simulation templates. "More convincing" here means *realistic enough to be a fair test*, so the training measures genuine susceptibility rather than rewarding users for spotting obvious fakes.

---

## Executive summary

The set divides sharply into **two quality tiers**:

- **Strong (4–5/5):** restrained, table-based, brand-accurate emails — the Microsoft family (mfa_update, security, teams_invite, onedrive, sharepoint), Okta verification/password, Adobe Sign, DocuSign, the manufacturing B2B set (SAP Ariba, Coupa), the LATAM tax/gov set (Receita Federal, SAT), and the smishing set. These read like the real thing.
- **Weak (1–2/5):** emoji-laden, alarmist, often unbranded pages with fabricated stats and "validate your account" hooks — most of `it-security/`, plus `corporate/travel_agency` (lottery scam), `corporate/breaking_news` (structurally **broken**), `financial/skype_payment` (impersonates a **discontinued** product) and `financial/wire_transfer` / `government/crime_report` (implausible sender authority).

### Cross-cutting issues (repo-wide, high leverage)

1. **Stale / past-dated content.** Pervasive `© 2024` footers, `_2024.pdf` filenames, and **hardcoded deadlines now in the past** (Feb 2025, Jan 2025). A past-dated "act within 48 hours" is an instant tell. → Move to relative/`{{.Date}}`-driven dates and refresh copyright years.
2. **Emoji & manufactured urgency.** 🚨⚠️🔒⏰ in subjects/headers, red "URGENT/CRITICAL" bars, countdown timers, pulsing animations. Real transactional mail almost never uses these. → Strip emoji; replace alarm bars with plain "Action required" labels.
3. **Text wordmarks instead of real logos.** Nearly every branded template uses styled text (or an emoji) where the genuine logo belongs (Microsoft four-square, DocuSign, Okta, AWS, Amazon, SAP, Instagram, LinkedIn). → Embed real logos as inline SVG/base64.
4. **`"validate your account" / log-in CTAs** on routine-maintenance pretexts** (storage quota, server migration, system update). The most recognizable phishing tell. → Reframe CTAs to device-side or benign actions.
5. **Placeholder identities & domains left in.** `company.com`, `yourcompany.com`, `(555)` numbers, all-zero CNPJ, "A colleague", "Internal user", "Admin Portal", and self-referential senders (Google Drive shows the recipient as the file-sharer). → Tokenize sender/domain; name plausible people.
6. **`{{.Email | slice}}`-derived IDs.** Employee/case/key numbers built by slicing the email render as obvious garbage. → Use clean fabricated reference formats.
7. **Thin variable usage.** `{{.From}}`, `{{.TrackingURL}}`, and `{{.FirstName}}`+`{{.LastName}}` together are essentially unused. → Low-effort personalization win.
8. **Email-client robustness.** Several strong templates use `display:flex`/`grid` that breaks in Outlook (okta_verification, servicenow_ticket, microsoft_mfa_update). → Convert to table layout.

### Priority actions

| Priority | Item | Why |
|---|---|---|
| **P0 – fix now** | `corporate/breaking_news.html` | CSS is truncated and dumped as literal text after `</html>`; shows "CHART PLACEHOLDER". Non-deliverable. |
| **P0 – fix now** | `financial/skype_payment.html` | Impersonates Skype, retired by Microsoft in 2025. Premise is dead. |
| **P0 – quick win** | Repo-wide date/year refresh + emoji strip | Removes the most common tells in one sweep. |
| **P1** | `it-security/*` overhaul (email_size_limit, system_update, webmail_upgrade, mailbox_compromised, dropbox_share) | Lowest-fidelity group; emoji + alarmism + "validate account". |
| **P1** | Reconsider `government/crime_report.html` & `corporate/travel_agency.html` | Police-impersonation-with-secrecy and lottery-win are both unconvincing and ethically/legally fraught even for training. |
| **P2** | Embed real logos across the strong templates | Biggest fidelity gain for already-good lures. |
| **P2** | Brand-matched landing pages | `credential-harvest.html` is generic and matches none of the emails, breaking the click-through illusion. |

---

## Group 1 — ai-tools, cloud-services, collaboration, corporate, e-signature, entertainment

### ai-tools/chatgpt_account_suspended.html — 4/5
- **Strengths:** Clean on-brand OpenAI dark/minimal styling, plausible billing-failure pretext, no emoji.
- **Weaknesses:** CSS-drawn "O" ring approximates the logo; consumer ChatGPT Plus pretext has low relevance for corporate targets; "permanently deleted in 24h" overcooked; dead `#` help link.
- **Top fixes:** Re-angle to ChatGPT Enterprise/Team billing-admin; soften to dunning language ("lose access to saved chats after grace period"); embed real ChatGPT mark + invoice/reference number.

### ai-tools/copilot_license_suspended.html — 5/5
- **Strengths:** Highly relevant enterprise pretext (M365 Copilot, anomalous sign-in), authentic Segoe palette and four-square logo, mature copy with "don't share credentials".
- **Weaknesses:** ✨ emoji as the Copilot icon; "permanent revocation in 48h" mildly aggressive; `© 2025` stale; no incident/reference ID.
- **Top fixes:** Replace ✨ with inline SVG Copilot logo; add Incident/Reference row; refresh year.

### cloud-services/dropbox_share.html — 3/5
- **Strengths:** Relevant "colleague shared files for tomorrow's deadline" pretext (curiosity + time pressure); good avatar-initial use.
- **Weaknesses:** 📁 emoji logo + heavy body emoji; hardcoded placeholder sender; avatar initial derives from the *recipient*; `© 2024` / `Q4_2024` stale; "The Dropbox Team" voice inconsistent with a personal share.
- **Top fixes:** Real Dropbox glyph, strip emoji; distinct tokenized sender + correct avatar; refresh dates; drop the team sign-off.

### cloud-services/google_drive.html — 3/5
- **Strengths:** Accurate Google multicolor wordmark; "CONFIDENTIAL Q4 budget" curiosity hook.
- **Weaknesses:** "Shared by: {{.Email}}" shows the *recipient's own* address (logic tell); 📁 emoji; implausible "New to Google Drive?" block; "The Google Drive Team" sign-off; `© 2024`.
- **Top fixes:** Distinct fabricated sharer; remove the "new to Drive" block + emoji; mirror real Drive layout (thumbnail card, Open button).

### collaboration/slack_notification.html — 4/5
- **Strengths:** Real inline SVG Slack hashmark, authentic aubergine palette, believable DM preview.
- **Weaknesses:** SVG only has 2 of 4 colored quadrants (clipped); email-level "verify your Slack credentials" is unrealistic; "Your Company Workspace" placeholder.
- **Top fixes:** Complete the 4-color SVG; move the credential ask into the quoted DM only; tokenize workspace name.

### collaboration/teams_alert.html — 4/5
- **Strengths:** Clean Teams purple, decent SVG, clever "approve guest access / auto-approves at 5PM" authority+urgency hook.
- **Weaknesses:** Auto-approve claim isn't how Teams works; one ⚠️; generic "external-vendor@partner.com".
- **Top fixes:** Named vendor + request ID; remove emoji; reword to "will be escalated to your admin".

### collaboration/zoom_meeting.html — 3/5
- **Strengths:** Correct Zoom blue + wordmark; realistic cloud-recording pretext.
- **Weaknesses:** Host shown as the recipient yet body says "if you didn't host this…"; fabricated "storage 94% full, must download"; 📹⚠️ emoji; no meeting ID/date.
- **Top fixes:** Fix host logic; drop the storage pressure; real logo + meeting ID/date.

### corporate/breaking_news.html — 1/5  ⚠️ BROKEN
- **Weaknesses:** `<style>` block is truncated in `<head>` and the rest of the CSS is dumped as literal text after `</html>` — renders unstyled with raw CSS visible. "CHART PLACEHOLDER" shown. Impersonates "Business Insider" emailing a compliance assessment; fabricated penalty stats; `© 2024`.
- **Top fixes:** Repair the stylesheet (move into `<head>`, delete trailing dump); remove CHART PLACEHOLDER; reframe as an internal Compliance/Legal memo; replace invented stats.

### corporate/performance_review.html — 4/5
- **Strengths:** Sober internal-HR tone, universally relevant annual self-assessment pretext, correctly dated `© 2026`.
- **Weaknesses:** Header accent is Slack aubergine (#4a154b); generic "HR Talents & Development Team"; only `{{.FirstName}}`; deadline "Friday" not dated.
- **Top fixes:** Add `{{.LastName}}` + review ID + dated deadline; neutral corporate accent; single named HR contact.

### corporate/travel_agency.html — 1/5
- **Weaknesses:** Textbook "you've won $8,500" lottery scam; emoji + animations + fake countdown + fake testimonials; recipient never entered; `© 2024`.
- **Top fixes:** Abandon the lottery premise; if travel-themed, reframe as a mundane itinerary/expense confirmation; strip all emoji/animation/countdown.

### e-signature/adobe_sign.html — 5/5
- **Strengths:** Excellent fidelity — correct Adobe red, "Adobe Acrobat Sign" naming, numbered signing steps, realistic HR pretext, good variable use.
- **Weaknesses:** One ⏰ emoji; "yourcompany.com" placeholder; no agreement/transaction ID.
- **Top fixes:** Replace ⏰; tokenize sender domain; add Agreement/Transaction ID + Acrobat lockup.

### e-signature/docusign_signature.html — 5/5
- **Strengths:** Very authentic — "Please DocuSign this document" subject, yellow header, PDF doc card, "do not share this unique link" boilerplate, `{{.LastName}}` in filename.
- **Weaknesses:** Approximate wordmark (no real logo); "legal@yourcompany.com" placeholder; `_2024.pdf`; no envelope/security code.
- **Top fixes:** Add envelope ID/security code; refresh filename year; tokenize domain; real logo.

### entertainment/spotify_account.html — 2/5
- **Strengths:** Clean Spotify green + wordmark, Stockholm footer.
- **Weaknesses:** **CSS bug** `border-left: 4px solid: #ff9800;` (stray colon); consumer pretext on a work inbox; generic scare-list; `© 2024`.
- **Top fixes:** Fix the CSS typo; one specific login event; real circle logo; reposition as a receipt/family-plan curiosity hook.

### entertainment/starbucks_gift.html — 2/5
- **Strengths:** Correct Starbucks green + HQ footer, mild reward hook.
- **Weaknesses:** Weak work relevance; awkward suspend-vs-reward hybrid; text wordmark; invented stat rows that can't be personalized; `© 2024`.
- **Top fixes:** Pick one hook (reward redemption); real siren logo; drop fabricated stats.

---

## Group 2 — delivery-shipping, financial, government, healthcare, hospitality

### delivery-shipping/dhl_package.html — 2/5
- **Strengths:** Correct DHL red on CTA, real tagline, good variable use.
- **Weaknesses:** Logo is a 1×1 transparent PNG placeholder (renders broken); copy mixes DHL with USPS jargon ("bill of lading", "Label Number"); no tracking number; no footer.
- **Top fixes:** Real DHL wordmark; rewrite to DHL conventions (Waybill/Tracking #, "DHL Express Worldwide"); customs hook + real footer.

### delivery-shipping/holiday_package_delivery.html — 3.5/5
- **Strengths:** Clean, restrained; realistic small customs duty ($1.50); no emoji.
- **Weaknesses:** Generic "Global Express Courier" (low recognition); mixes "pay duty" + "verify address"; inconsistent timeframes.
- **Top fixes:** Decide generic-vs-real-carrier; single consistent deadline; carrier-correct tracking ID + address block.

### delivery-shipping/package_pickup.html — 2/5
- **Strengths:** Plausible workplace mailroom pretext; `{{.Email}}` as username.
- **Weaknesses:** 📦📋 emoji; brand confusion (FedEx vs "Package Pickup Service" + fake domain); heavy credential ask; `© 2024`.
- **Top fixes:** Remove emoji; resolve to one brand; soften to "verify delivery preferences"; refresh year.

### financial/skype_payment.html — 1.5/5  ⚠️ OBSOLETE PREMISE
- **Weaknesses:** Skype was retired (May 2025) — pretext is dead. Countdown timer, emoji, gift-card payment, fake "+1-800-SKYPE-HELP", `© 2024`, `href="#"` placeholders.
- **Top fixes:** Repurpose to a live Microsoft service (M365/Teams billing); remove timer/emoji/gift-card; single realistic ask.

### financial/wire_transfer.html — 1.5/5
- **Weaknesses:** "Federal Reserve Wire Network" contacting an individual (implausible); "Amount: [CONFIDENTIAL]" reads as an unfilled placeholder; signer "Vincent Crabbe" (fictional character); odd `{{.Date}}-{{.Email}}` reference.
- **Top fixes:** Re-target to the user's bank / a fraud-dept sender; concrete amount; neutral officer name + real reference format + letterhead.

### government/better_business.html — 2.5/5
- **Strengths:** Strong B2B reputational-fear pretext; substantive complaint narrative.
- **Weaknesses:** Emoji + giant red "C-" rating + countdown; logical contradiction (most SMBs aren't BBB-accredited); "Dear Business Owner" despite `{{.FirstName}}`; `© 2024`; overstated authority.
- **Top fixes:** Strip emoji/rating-downgrade theatrics; personalize greeting; single concrete ask + real BBB footer.

### government/crime_report.html — 1/5  ⚠️ RECONSIDER
- **Weaknesses:** Police impersonation with "do not discuss this case with anyone" (textbook scam script, ethically fraught); implausible (PD emailing a citizen at 2:47 AM); 🚨👮 + pulsing animation; asks for additional PII.
- **Top fixes:** Reconsider this pretext entirely; if kept, remove animation/emoji + the secrecy line and reframe as a generic identity-monitoring alert without a PII request.

### government/fdic_survey.html — 1.5/5
- **Weaknesses:** False premise (FDIC doesn't survey consumers); coercive "may affect your deposit insurance"; text "FDIC" seal placeholder; "Dear Bank Customer" despite `{{.FirstName}}`; `© 2024`.
- **Top fixes:** Re-anchor to the user's bank citing FDIC, or an FDIC fraud-awareness notice; personalize; add the real seal.

### government/irs_tax_refund.html — 3/5
- **Strengths:** Restrained Treasury-blue layout, plausible CP-244D reference, no emoji, current 2026 footer.
- **Weaknesses:** Vague "Recent Filing Period"/"Current Cycle" read as unfilled fields; IRS uses mail not email; "claim or forfeit" slightly off; only `{{.FirstName}}`.
- **Top fixes:** Concrete values via `{{.Date}}`; reframe as "view refund status"; add notice number + masked SSN.

### healthcare/hipaa_compliance_alert.html — 4/5
- **Strengths:** Highly relevant internal-compliance pretext (annual HIPAA recert), clean/plain, credible consequence + contact.
- **Weaknesses:** Generic "@healthcare.org"; `© 2024`; placeholder address; hardcoded ageing dates.
- **Top fixes:** Parameterize sender/domain to target org + `{{.From}}`; dynamic dates; refresh year.

### healthcare/insurance_verification.html — 3.5/5
- **Strengths:** Believable annual-verification pretext; calm tone; reasonable 10-day window.
- **Weaknesses:** Generic "HealthCare Insurance Group"; `HC-{{.Email | slice 0 8}}` policy number; over-asks for photo ID/proof of address; `© 2024`.
- **Top fixes:** Brand to a likely insurer or add a logo; clean policy-number format; defer ID asks to the landing page.

### healthcare/patient_portal_security.html — 4/5
- **Strengths:** Classic effective "unrecognized login" pretext; realistic details (3:42 AM, masked Tor-range IP); restrained, single CTA.
- **Weaknesses:** Generic "MyHealth Patient Portal"; "permanent suspension in 24h" aggressive; `© 2024`.
- **Top fixes:** Match the target's real portal (e.g. MyChart); soften to "temporary lock until verified"; refresh year.

### hospitality/booking_reservation_hold.html — 4/5
- **Strengths:** Excellent table-based build; accurate Booking.com color + real Amsterdam legal footer; concise "payment on hold" pretext, no emoji.
- **Weaknesses:** Text wordmark only; no reservation specifics (dates/property/confirmation #).
- **Top fixes:** Add a reservation summary block; add the logo; realistic booking reference.

### hospitality/hotel_reservation_confirm.html — 3/5
- **Strengths:** Clean layout, concrete reservation details, reasonable 48h hook.
- **Weaknesses:** Generic invented "Grand Hotel & Resorts" (unsolicited booking the user never made is suspicious); `GH{{.Email | slice 0 8}}`; ageing 2025 dates; `© 2024`.
- **Top fixes:** Tie to a real chain or corporate-travel context; clean reference; dynamic near-future dates.

### hospitality/marriott_bonvoy_points.html — 4/5
- **Strengths:** Strong real-brand impersonation (Marriott Bonvoy navy + real HQ); genuinely plausible "points expire after inactivity" mechanic; low-pressure loss-aversion hook, no emoji.
- **Weaknesses:** Text wordmark; unpersonalized points/months; "7 days from today" is relative text, not a date.
- **Top fixes:** Add the Bonvoy logo; concrete expiration date; membership number field.

---

## Group 3 — hr-payroll, identity, itsm, legal, landing

### hr-payroll/benefits_enrollment.html — 3/5
- **Strengths:** Plausible HR pretext, familiar benefits list, clean layout.
- **Weaknesses:** Aggressive double-urgency ("lose coverage for the entire year"); hardcoded "January 31, 2025" stale; `company.com`/`(555)`; `© 2024`; no real portal brand.
- **Top fixes:** Relative/injected deadline + synced year; calmer single reminder; real benefits domain; brand to Workday/ADP/bswift.

### hr-payroll/open_enrollment_reminder.html — 4/5
- **Strengths:** Professional measured tone, realistic info-table, "do not reply" boilerplate, 2026 footer. Most polished HR lure.
- **Weaknesses:** ⚠️ in alert title; deadline "Friday 5 PM EST" not dated; generic "HR Benefits Center"; no `{{.LastName}}`.
- **Top fixes:** Remove emoji; dated deadline + full name; brand to real provider.

### hr-payroll/payroll_direct_deposit.html — 4/5
- **Strengths:** High-bite direct-deposit verification pretext; calm "audit/compliance" framing.
- **Weaknesses:** `EMP-{{.Email | slice 0 6}}` nonsensical ID; `company.com`/ext placeholders; `© 2024`.
- **Top fixes:** Drop slice-derived ID; realistic contact details; frame as "review" rather than "update banking".

### hr-payroll/year_end_bonus.html — 4/5
- **Strengths:** Strong curiosity+greed hook; polished "CONFIDENTIAL — INTERNAL ONLY" framing.
- **Weaknesses:** 🔒 emoji; bait-and-switch to "verify banking" is heavy-handed; no actual amount/date; generic "Corporate Payroll Services".
- **Top fixes:** Remove emoji (use a styled "Confidential" tag); soften/defer the banking ask; real payroll system name.

### identity/duo_reenroll.html — 4/5
- **Strengths:** Clean Duo green, concise MFA re-enrollment, table layout, tasteful (no emoji).
- **Weaknesses:** Text wordmark; generic stick; no dated deadline; mixed sender identity (Duo vs internal IT).
- **Top fixes:** Embed Duo glyph; pick one voice; concrete dated deadline.

### identity/okta_password_expiry.html — 4/5
- **Strengths:** Accurate Okta blue + real corporate footer; closely mirrors genuine Okta mail; "expires today" is strong.
- **Weaknesses:** Text wordmark; real Okta mail comes from the org tenant ("company.okta.com"); only `{{.FirstName}}`.
- **Top fixes:** Add Okta logo; reference the org tenant/portal; include the account/email line.

### identity/okta_verification.html — 5/5
- **Strengths:** Highly convincing "new sign-in detected" with detailed table (time/device/IP/apps), strong "This wasn't me" CTA, live `{{.Date}}`. Best identity lure.
- **Weaknesses:** "Kyiv, Ukraine" + Tor IP slightly theatrical; ⚠️ emoji; `display:flex` may break in Outlook; text wordmark.
- **Top fixes:** Less stereotyped (templatized) location; table-based layout; remove emoji; add logo.

### itsm/jira_service_desk.html — 4/5
- **Strengths:** Authentic Jira blue, correct "Jira Service Management" + Atlassian footer, realistic ticket ID, clean.
- **Weaknesses:** "Reporter: Internal user" vague; no logo; low urgency; `{{.LastName}}` unused.
- **Top fixes:** Name a plausible reporter; add the logo; add a comment snippet/timestamp.

### itsm/servicenow_approval.html — 4/5
- **Strengths:** Correct ServiceNow navy, realistic RITM number, automation-flavored tone.
- **Weaknesses:** "Requested for: a member of your team" vague; text wordmark; `{{.LastName}}` unused; no item/date.
- **Top fixes:** Named requester + item description/date; embed logo.

### itsm/servicenow_ticket.html — 3/5
- **Strengths:** Detailed change-request layout (ticket grid, priority, SLA), authority+curiosity ("Emergency Production Access").
- **Weaknesses:** Over-urgent "⚡ SLA BREACH IN 2 HOURS" + emoji; implausible "auto-grant on no response"; `grid/flex` breaks in Outlook; mis-targeted to general staff; both Approve/Reject go to same `{{.URL}}`.
- **Top fixes:** Remove SLA bar/emoji + auto-grant line; table layout; reserve for IT/ops recipients.

### legal/case_document_sharing.html — 2/5
- **Strengths:** Polished law-firm styling, attorney-client-privilege framing.
- **Weaknesses:** Mis-targets employees (no personal legal matter); `Case #2024-{{.Email | slice 0 6}}` garbage number; fictitious firm/address/`555`/`2024`.
- **Top fixes:** Re-target (DocuSign from "outside counsel" re: employment/NDA) or scope to legal/exec; clean reference; realistic firm details.

### legal/docusign_nda.html — 4/5
- **Strengths:** Recognizable DocuSign red, "Powered by DocuSign" + real footer; NDA signature is a common low-suspicion event.
- **Weaknesses:** Text wordmark; "Sent by: Legal Department" generic; no envelope/security code.
- **Top fixes:** Logo + yellow CTA; named sender + envelope/security code; reference company name.

### legal/legal_hold_notice.html — 4/5
- **Strengths:** Authoritative "Office of the General Counsel" + legal-hold preservation language + mandatory acknowledgement. Sober.
- **Weaknesses:** No matter/reference number or date; vague "a matter involving the company"; plain header; `{{.LastName}}` unused.
- **Top fixes:** Matter name/number + issuing attorney signature; brand to the recipient's company; add a "respond by" date.

### landing-pages/credential-harvest.html — 2/5
- **Strengths:** Clean focused login form; pre-fills `{{.Email}}`; responsive.
- **Weaknesses:** Generic "Company Portal" matches none of the email lures (breaks the illusion); asks email+username+password together (unusual); `© 2024` + dummy `#` links; generic scare copy; dead no-op script.
- **Top fixes:** Create brand-matched landing variants (Okta/DocuSign/ServiceNow) with matching logos; realistic field set; real name/year/links.

---

## Group 4 — it-security, microsoft, technology

### it-security/dropbox_share.html — 2/5
- **Weaknesses:** 📁 emoji logo + body emoji; "Shared by: team@company.com" implausible; no filename/footer; "The Dropbox Team" voice.
- **Top fixes:** Real glyph + strip emoji; realistic named sharer + file; authentic footer + `{{.From}}` sender.

### it-security/email_issues.html — 3/5
- **Strengths:** Plausible internal-IT migration-follow-up pretext, good personalization.
- **Weaknesses:** 🔧🔒 emoji; "Validate Email Account" credential tell; no sender/ticket/date; unbranded.
- **Top fixes:** Remove emoji + rename CTA ("Open mailbox"); add ticket ref + named sender + date; add a logo band.

### it-security/email_size_limit.html — 2/5
- **Strengths:** Detailed quota dashboard adds technical realism.
- **Weaknesses:** Red "URGENT" + ⚠️🚨📧📊🔧⏰ + ALL-CAPS; "Validate Email Account" tell; `ESM-{{.Date}}-{{.Email}}` embeds the address; dated 5 GB quota; `company.com`.
- **Top fixes:** Strip banner/emoji; CTA → "Manage mailbox storage"; numeric reference ID; realistic quota (49.5/50 GB).

### it-security/mailbox_compromised.html — 2/5
- **Weaknesses:** 🔐⚠️🛡️📚 + purple gradient resembling no real provider; clashing header colors; all three links → same `{{.URL}}`; generic team; pushy footer.
- **Top fixes:** Remove emoji + fix colors; only the primary action → `{{.URL}}`; add concrete sign-in detail + real provider footer.

### it-security/system_update.html — 2/5
- **Weaknesses:** Conflates Windows branding (🪟) with internal IT; emoji + red "CRITICAL"; "23 critical patches / disconnection imminent" alarmist; fabricated `update.microsoft.com/corporate`; "LOG IN to your corporate account" tell; `MSU-{{.Date}}-{{.Email}}` ID.
- **Top fixes:** One identity (internal IT) + drop Windows branding/emoji; reduce drama; CTA → device-side ("Open Software Center").

### it-security/webmail_upgrade.html — 2/5
- **Strengths:** Polished feature-grid layout; benefit (not fear) hook.
- **Weaknesses:** Gradient resembles no brand; 🎉🛡️📊🚀🔒⚡📱🔄🚨 everywhere; absurd 250MB→500MB; meta-irony (phishing-warning email asking you to log in); promo-scam phrasing; unbranded.
- **Top fixes:** Cut length + emoji; believable storage numbers; CTA → "Review upgrade details" + branding.

### microsoft/microsoft365_password_expiry.html — 4/5
- **Strengths:** Table-based, email-safe, authentic M365 blue + Redmond footer, no emoji.
- **Weaknesses:** Text wordmark; "expires today" aggressive; no `{{.From}}`; "The Microsoft 365 Team" vs org/Azure AD.
- **Top fixes:** Add four-color logo; "expires in 3 days" + date; frame sender as org IT/Azure AD.

### microsoft/microsoft_mfa_update.html — 4/5
- **Strengths:** Excellent Fluent/Segoe styling, restrained alert, structured rows, topical MFA pretext, no emoji.
- **Weaknesses:** Text wordmark; "within 48 hours" not dated; no privacy link/sender; `display:flex` Outlook risk.
- **Top fixes:** Logo + privacy footer link; dated deadline via `{{.Date}}`; table-based header.

### microsoft/microsoft_security.html — 4/5
- **Strengths:** Believable "unusual sign-in" with location/device/time, correct colors + Redmond footer + privacy reference.
- **Weaknesses:** 📍🛡️ emoji; Privacy Statement is dead `#`; text wordmark.
- **Top fixes:** Remove emoji + add logo; real privacy URL; add "If this wasn't you" secondary action.

### microsoft/microsoft_teams_invite.html — 4/5
- **Strengths:** Strong Teams fidelity (purple, avatar bubble, chat preview), realistic missed-message pretext, emoji-free.
- **Weaknesses:** Generic "Project Manager (via Teams)" sender; text wordmark; dead privacy link; no timestamp.
- **Top fixes:** Realistic colleague name (matching avatar initials); logo + "sent X min ago"; fix dead link.

### microsoft/onedrive_file_share.html — 4/5
- **Strengths:** Faithful OneDrive styling, realistic file card, excellent curiosity lure ("Q3 Budget and Compensation Reviews").
- **Weaknesses:** "Admin Portal (via OneDrive)" sharer implausible; 📊 as the file icon; text wordmark; dead privacy link.
- **Top fixes:** Named Finance/HR sharer; real Excel icon + OneDrive logo; trim the on-the-nose description.

### microsoft/sharepoint_document_share.html — 4/5
- **Strengths:** Clean Outlook-safe table layout, correct SharePoint blue, realistic "Q3 Budget — Final.xlsx", org-access wording, no emoji.
- **Weaknesses:** No logo; "A colleague" not named; no thumbnail/metadata; generic tenant context.
- **Top fixes:** Name the sharer + Excel icon; add logo + "modified today" metadata; `{{.From}}`-aligned sender.

### technology/api_key_expiration.html — 3/5 (higher for developers)
- **Strengths:** Convincing dev aesthetic (VS Code theme, syntax-colored code, curl example, 401); non-alarmist 7-day expiry; emoji-free.
- **Weaknesses:** Generic "Developer Platform API"; `sk_live_{{.Email | slice 0 16}}` recognizable as fake; hardcoded 2024/2025 dates now stale; `© 2024`; narrow audience.
- **Top fixes:** Impersonate a real provider (Stripe/GitHub/SendGrid) or brand internally; `{{.Date}}`-relative expiry + year; masked key (`sk_live_…last4`).

### technology/aws_account_verification.html — 4/5
- **Strengths:** Authentic AWS navy + real Seattle footer, terse professional copy, believable billing-verification, table layout, no emoji.
- **Weaknesses:** Text header (no smile logo); no account ID/deadline/case number; owner/admin-targeted; generic sender.
- **Top fixes:** AWS logo + masked account ID + case number; dated deadline via `{{.Date}}`; AWS-billing sender framing.

---

## Group 5 — quishing, manufacturing, retail, utilities

> **Quishing note:** every QR in this set is a non-scannable static SVG **placeholder** that encodes nothing, and two files ship visible `DEPLOYMENT NOTE` HTML comments (with `qrencode` instructions) in source. The QR scan path is non-functional until real QR codes encoding `{{.URL}}` are generated.

### quishing/docusign_qr.html — 4/5
- **Strengths:** Clean DocuSign-styled NDA pretext, doc table, `{{.URL}}` desktop fallback.
- **Weaknesses:** Text wordmark + wrong accent (real DocuSign is yellow `#FFB81C`, not `#0056b3`); 📝 emoji; placeholder QR; generic "Corporate Legal Team".
- **Top fixes:** Real logo + correct colors; QR that encodes `{{.URL}}`; named sender + envelope ID.

### quishing/microsoft_mfa_qr.html — 4/5
- **Strengths:** Strong Microsoft/Segoe treatment, plausible IT MFA-reenrollment with numbered steps.
- **Weaknesses:** 🔒 emoji; real Authenticator QRs are shown in-portal not emailed; placeholder QR; generic IT signature.
- **Top fixes:** Drop emoji; believable internal IT sender; functional QR; consider co-branding as org IT.

### quishing/parking_toll_qr.html — 3/5
- **Strengths:** Topical (toll-scam surge), realistic $12.50 + `{{.Email}}` reference + `{{.Date}}`.
- **Weaknesses:** Consumer lure, weak work relevance; ⚠️ + ALL-CAPS yellow-on-black header (cartoonish); vague invented "State DoT"; over-threatening for $12.50.
- **Top fixes:** Real tolling authority (E-ZPass/SunPass/FasTrak) + branding; remove emoji + tone down threats; functional QR + plate/notice number.

### quishing/qr_code_mfa.html — 3/5
- **Strengths:** Polished generic-IT styling, EOB deadline, instructions, `{{.URL}}` fallback.
- **Weaknesses:** Visible `DEPLOYMENT NOTE` comment in source; ⚠️⏰ emoji; overlaps microsoft_mfa_qr but less brand-specific; generic sender.
- **Top fixes:** Strip the comment; functional QR; remove emoji + specific helpdesk identity.

### quishing/qr_code_wifi.html — 3/5
- **Strengths:** Novel low-suspicion WiFi-onboarding pretext; clean Facilities/IT styling, SSID/WPA3 detail.
- **Weaknesses:** Visible `DEPLOYMENT NOTE` comment; 📶 emoji; technically incoherent (real WiFi QRs encode `WIFI:` creds, not a URL); `helpdesk@company.com` placeholder.
- **Top fixes:** Remove comment + functional QR; templatize the domain; drop emoji.

### quishing/secure_document_qr.html — 4/5
- **Strengths:** Strong curiosity hook ("Performance_Reviews_and_Q3_Adjustments.pdf"); clean secure-portal look with metadata/expiry/fallback.
- **Weaknesses:** "Requires mobile device verification" is a contrived QR justification; 📄 emoji; unbranded "Secure File Transfer"; placeholder QR.
- **Top fixes:** Brand as a known product (ShareFile/Egnyte/SharePoint); functional QR + named HR sender; soften the device-verification reason.

### manufacturing/coupa_supplier_banking.html — 4/5
- **Strengths:** Tight professional Coupa-styled email; banking-reverification-before-payment-run is exactly how real vendor-fraud/BEC reads; correct HQ; no tells.
- **Weaknesses:** Text wordmark (generic blue, not Coupa orange); no PO/invoice/profile ref or cutoff date; generic signer.
- **Top fixes:** Coupa logo + color; supplier-profile ID + cutoff date; named AP contact.

### manufacturing/sap_ariba_po.html — 4/5
- **Strengths:** Very realistic SAP Ariba PO-review; correct Walldorf address + plausible 10-digit PO + SAP blue; strong B2B targeting.
- **Weaknesses:** "Supplier: Registered vendor" placeholder; text wordmark; no date/amount/line items.
- **Top fixes:** Realistic supplier name; SAP Ariba logo; PO amount/date.

### manufacturing/supplier_portal_update.html — 3/5
- **Strengths:** Detailed compliance pretext with vendor ID, `{{.Company}}`, ACH-banking ask (the real goal), hold-status consequence.
- **Weaknesses:** "Manufacturing Corp"/`manufacturing.com`/`© 2024` placeholders; hardcoded "February 15, 2025" deadline now in the past; `(555)`.
- **Top fixes:** Spoof the target's real name/domain; relative/future deadline; believable phone.

### retail/amazon_order_problem.html — 3/5
- **Strengths:** Universally relevant "payment problem, order on hold", correct Amazon navy + Seattle footer, no emoji.
- **Weaknesses:** Text wordmark (no smile logo); no order number/item/date/amount; consumer relevance.
- **Top fixes:** Logo + order reference/date/item; Amazon's yellow button + order-details block.

### retail/costco_membership_renewal.html — 3/5
- **Strengths:** Plausible auto-renewal-declined pretext, correct Costco blue + Issaquah footer, restrained.
- **Weaknesses:** Text wordmark; no membership number/amount/date; consumer relevance.
- **Top fixes:** Logo + membership/amount/date block; name the tier (Gold Star/Executive).

### retail/loyalty_rewards_expiring.html — 2/5
- **Weaknesses:** Fully generic "Retail Rewards"/`retail.com`/`© 2024`; hardcoded "February 28, 2025" past date; spammy "Don't Lose Your Rewards Points!" + `555`; low-value reward ($24.50).
- **Top fixes:** Rebrand to a real program (Starbucks/airline/Best Buy); near-future relative expiry; tone down to genuine program voice.

### utilities/autopay_failed.html — 3/5
- **Strengths:** Universally believable "autopay declined, update billing", clean styling, restrained, no tells.
- **Weaknesses:** Generic "Your Energy Provider"; no account number/amount/date; consumer relevance.
- **Top fixes:** Real regional utility name/logo; account number + amount/due-date.

### utilities/power_outage_credit.html — 3/5
- **Strengths:** Less common curiosity/greed "service credit owed" angle; detailed account block + claim steps.
- **Weaknesses:** "City Power & Light"/`citypower.com`/`© 2024`/`555`; hardcoded "January 15, 2025" + "claim within 30 days" expired; literal "your service address on file" placeholder text.
- **Top fixes:** Fix the literal placeholder (variable or remove); rebrand + recent/relative dates; believable phone.

### utilities/service_disconnection_notice.html — 4/5
- **Strengths:** High-urgency "final disconnection notice" (one of the most effective utility lures); dry bureaucratic tone + "if you already paid, disregard" realism; no emoji.
- **Weaknesses:** Generic "Your Utility Provider"; no account number/amount/disconnection date.
- **Top fixes:** Real utility brand; specific past-due amount + account number + disconnection date.

---

## Group 6 — smishing, social-media, latam-portuguese, latam-spanish

> **Smishing note:** all five are solid (4/5). Shared weaknesses: raw `{{.URL}}` shown as link text instead of a realistic lookalike short link, generic spoofed domains in plaintext, and emoji in subjects. Real smishing uses short codes + shorteners.

### smishing/bank_alert_sms.html — 4/5
- **Strengths:** Classic high-conversion Chase fraud-alert ($847 Amazon charge), correct real Chase fraud number, believable iMessage mockup.
- **Weaknesses:** Spoofed domain `chase-secure-notifications.com` verbatim; mixed corporate-email framing; raw `{{.URL}}`; 🚨 subject.
- **Top fixes:** Lookalike short link; drop emoji; numeric short-code sender.

### smishing/it_helpdesk_sms.html — 4/5
- **Strengths:** Strong internal-IT password-change pretext, uses `{{.Email}}` in body.
- **Weaknesses:** `company-support-tickets.com` generic; orgs rarely text AD alerts; raw `{{.URL}}`; ⚙️ subject.
- **Top fixes:** Target org's real domain pattern; short-code + short link; add a ticket number.

### smishing/mfa_verification_sms.html — 4/5
- **Strengths:** Timely MFA-device-change scenario, authentic masked phone.
- **Weaknesses:** Russian `+7 (911)` reads cartoonish; `company-access-portal.com`; unnatural "MSG:" prefix; raw `{{.URL}}`.
- **Top fixes:** Domestic-looking masked number; lead with service name ("Okta:"); branded short link.

### smishing/package_delivery_sms.html — 4/5
- **Strengths:** Extremely common high-click USPS failed-delivery, realistic 22-digit tracking + correct USPS phone + 24h urgency.
- **Weaknesses:** `delivery-alerts.net` generic; raw `{{.URL}}`; 📦 subject.
- **Top fixes:** `usps.com`-style lookalike short link; frame purely as SMS; remove emoji.

### smishing/payroll_hr_sms.html — 4/5
- **Strengths:** High-yield direct-deposit-change pretext, concise with clear stakes.
- **Weaknesses:** `company-hr-portal.com`; narrative inconsistency (SMS "modified" vs email "require validation"); raw `{{.URL}}`; 📊 subject.
- **Top fixes:** Align the narrative; name a real payroll system (Workday/ADP); short link + drop emoji.

### social-media/instagram_login_alert.html — 4/5
- **Strengths:** Faithful Instagram new-login email, correct magenta + Meta/Menlo Park footer, restrained, no emoji.
- **Weaknesses:** Text wordmark (no gradient logo); vague device/location; no timestamp.
- **Top fixes:** Inline SVG/gradient wordmark; concrete timestamp + city; "This wasn't me" framing.

### social-media/linkedin_inmail.html — 4/5
- **Strengths:** Clean on-brand InMail (#0a66c2 + Sunnyvale), recruiter-opportunity curiosity hook, low on tells.
- **Weaknesses:** "The LinkedIn Team" not a named recruiter; no sender avatar/title; text wordmark.
- **Top fixes:** Named sender + title/company; avatar + "InMail" badge; "in" logo mark.

### social-media/linkedin_reminder.html — 2/5
- **Weaknesses:** Wrong brand color (#0077b5 old blue); 📬📨📊📧 emoji-laden headers; awkward "in LinkedIn / Professional Network" wordmark; `© 2024`; unsubscribe links to `{{.URL}}`; marketing tone unlike real LinkedIn.
- **Top fixes:** Remove emoji + marketing stat boxes; fix color to #0a66c2 + year; unsubscribe → innocuous anchor; proper logo.

### latam-portuguese/helpdesk_ti.html — 4/5
- **Strengths:** Native PT-BR; convincing ServiceDesk ticket layout (ticket # via `{{.RId}}`, priority/status, ramal), credible semester password-renewal pretext.
- **Weaknesses:** Generic "TI ServiceDesk" (no real tool/logo); no sender address; generic extension.
- **Top fixes:** Brand to a real ITSM tool + logo; add a "De:" sender; reference the company dynamically.

### latam-portuguese/microsoft365_corporativo.html — 4/5
- **Strengths:** Strong M365 fidelity + correct footer; fluent PT-BR; blocked-login table with BRT timestamp; "Microsoft nunca solicita sua senha" reassurance.
- **Weaknesses:** "Moscou, Rússia" stereotyped; text wordmark; displayed fallback URL is a real MS domain while the button goes to `{{.URL}}` (hover mismatch).
- **Top fixes:** Less clichéd location; four-square logo; lookalike fallback URL matching the link intent.

### latam-portuguese/notificacao_bancaria.html — 3/5
- **Strengths:** Native PT-BR; professional bank-security layout (São Paulo IP, device, status), Brazilian footer (CNPJ, Av. Paulista, 0800), 2h urgency.
- **Weaknesses:** Generic "BANCO CORPORATIVO" (not a real bank); all-zero CNPJ/`0800 000 0000` placeholders.
- **Top fixes:** Impersonate a real Brazilian bank (Itaú/Bradesco/Caixa) + logo; realistic CNPJ; masked account/agency.

### latam-portuguese/onboarding_rh.html — 4/5
- **Strengths:** Excellent native PT-BR; clever onboarding-checklist pretext for new hires (low suspicion), done/pending items driving the click, "Etapa 3 de 4" progress framing.
- **Weaknesses:** Generic "Empresa S.A."; `rh@empresa.com.br` placeholder; no sender header.
- **Top fixes:** Inject real company name/logo; org's true HR domain; name the HR system (Gupy/Senior).

### latam-portuguese/receita_federal.html — 5/5
- **Strengths:** Highly convincing Receita Federal/gov.br impersonation — correct green/yellow palette, "Ministério da Fazenda", gov.br bar, malha-fina pretext with NF number, legally-toned disclaimer (multa 75% + SELIC), real phone 146. Native, formal, bureaucratic PT-BR.
- **Weaknesses:** No displayed gov.br-lookalike URL; odd CPF/email pairing in one row; no brasão/logo.
- **Top fixes:** Add the RF brasão; separate + mask CPF; show a gov.br-lookalike link near the CTA.

### latam-spanish/helpdesk_ti.html — 3/5
- **Strengths:** Native Spanish, concise scheduled-revalidation pretext + "menos de un minuto" friction-reducer.
- **Weaknesses:** Very plain "Soporte de TI" (no logo/ticket detail); no deadline/ticket/sender; thinner than the PT version.
- **Top fixes:** Add ticket # (`{{.RId}}`) + priority + deadline; brand + logo; spoofed "De:" sender.

### latam-spanish/microsoft365_corporativo.html — 4/5
- **Strengths:** Faithful M365 look + correct footer; fluent neutral Spanish; names Teams/OneDrive; no emoji.
- **Weaknesses:** Text wordmark; less detail than PT version (no event table/IP); no displayed sender/fallback URL.
- **Top fixes:** Add a blocked-login detail table; four-square logo; lookalike fallback URL.

### latam-spanish/notificacion_bancaria.html — 3/5
- **Strengths:** Native Spanish, clean brief security-notice tone, "no comparta sus credenciales" realism.
- **Weaknesses:** Generic "Notificación de Seguridad" (no bank/logo/country branding); vague pretext, no specifics/timer; no footer.
- **Top fixes:** Impersonate a real bank (BBVA/Santander/Banorte) + logo; detail table + deadline; localized footer.

### latam-spanish/sat_notificacion.html — 4/5
- **Strengths:** Strong Mexican SAT impersonation — correct guinda color (#691c32), proper SAT naming, authentic RFC + e.firma references; native formal Spanish.
- **Weaknesses:** Thinner than receita_federal (no notice number/deadline/table/logo); generic CTA to raw `{{.URL}}`; no footer.
- **Top fixes:** Add requerimiento/oficio number (`{{.RId}}`) + deadline + detail table; SAT logo + sat.gob.mx-lookalike link; footer with MarcaSAT contact.

> **LATAM translation quality:** high across the board. Both the PT-BR and Spanish files read as native, idiomatic, and register-appropriate (bureaucratic for tax/bank, corporate for IT/HR) with no machine-translation artifacts. The PT-BR set uses authentic local conventions (ramal, malha fina, CNPJ, e-CAC, gov.br, SELIC); the Spanish SAT mail correctly uses RFC/e.firma. The Spanish files are weaker on *content depth*, not language.
