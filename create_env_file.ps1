# PowerShell script to create .env file for Render database
# Run this script: .\create_env_file.ps1

$envContent = @"
# Render PostgreSQL Database - External URL (for local testing)
DATABASE_URL=postgresql://seait_lost_and_found_user:JcujN1AassCE1pQddkPPyWiOh7BRtfKu@dpg-d6dd5ip4tr6s73co3uhg-a.singapore-postgres.render.com:5432/seait_lost_and_found

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=seait-lost-found-secret-key-2024-change-this

# Session Configuration (set to True when using HTTPS)
SESSION_COOKIE_SECURE=False

# OpenAI (optional) — ChatGPT-style assistant replies
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_CHAT_MODEL=gpt-4o-mini

# Chatbot face/logo (optional) — file under app/static/images/
# CHATBOT_AVATAR_STATIC=images/my-chatbot.png
# CHATBOT_ASSISTANT_NAME=SEAIT Helper
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host ".env file created successfully!" -ForegroundColor Green
Write-Host "You can now test the connection with: python connect_render_db.py" -ForegroundColor Yellow
