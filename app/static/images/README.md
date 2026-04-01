# Images Directory

## Logo
Place your SEAIT logo file here:
- **File name:** `seait-logo.png`
- **Recommended size:** 200x200px or larger (will be scaled down)
- **Format:** PNG with transparent background preferred

## Team Members
Place team member photos in the `team/` directory:
- **File names:** `member1.jpg`, `member2.jpg`, `member3.jpg`, etc.
- **Recommended size:** 300x300px or larger (will be displayed as 120x120px circles)
- **Format:** JPG or PNG
- **Aspect ratio:** Square (1:1) works best

### Current Team Members (update in login.html):
1. `member1.jpg` - Team Member 1 (Developer)
2. `member2.jpg` - Team Member 2 (Designer)
3. `member3.jpg` - Team Member 3 (Manager)
4. `member4.jpg` - Team Member 4 (Analyst)
5. `member5.jpg` - Team Member 5 (Specialist)

To add more team members:
1. Add the image file to `team/` directory
2. Update the team grid in `app/templates/auth/login.html`

## Chatbot avatar (floating assistant)

- **Default:** `chatbot-mascot.svg` (bundled cute mascot).
- **Your face or logo:** Add e.g. `my-assistant.png` (square, **256×256** or larger works well) under this folder.
- Set environment variable: `CHATBOT_AVATAR_STATIC=images/my-assistant.png`
- Optional display name: `CHATBOT_ASSISTANT_NAME=Your Name`

For **OpenAI**-powered replies, set `OPENAI_API_KEY` on the server (never commit it to git). See your platform’s environment variable settings (e.g. Render → Environment).
