# `landing-pages` — Landing & training pages

The pages a target reaches **after clicking** a phishing-simulation email. Two kinds live here: credential-capture pages (to measure who submits data) and the post-click education flow (to turn a click into a teachable moment).

Part of [gophish-training-templates](../README.md). For email templates, see the category folders; for the full index, see the [catalog](../docs/CATALOG.md).

## Pages

| File | Purpose |
|---|---|
| [`credential-harvest.html`](credential-harvest.html) | Generic "Employee Portal" sign-in page for measuring credential submission. Pre-fills `{{.Email}}`; the form posts to GoPhish for capture. |
| [`microsoft365-login.html`](microsoft365-login.html) | Microsoft 365 / Azure AD sign-in replica. Pair with the Microsoft, identity, and quishing email templates so the click-through matches the lure. |
| [`okta-login.html`](okta-login.html) | Okta sign-in replica. Pair with the `identity/` Okta templates. |
| [`education-notification.html`](education-notification.html) | The "this was a simulated phishing test" gateway page. Redirects to the category-specific training module under each category's `education/` folder. |

## How to use

1. In GoPhish, go to **Landing Pages → New Page** and paste the HTML.
2. For credential pages, enable **Capture Submitted Data** (and optionally **Capture Passwords**) per your policy and authorization.
3. Set the **redirect** to `education-notification.html` (or a category training page) so clickers get immediate education rather than just a "gotcha".

> **Important:** the capture forms post to GoPhish only — they do not exfiltrate data anywhere. Customize branding/domain to your engagement, and only use against a consented, in-scope group with proper authorization.
