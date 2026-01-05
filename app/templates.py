from datetime import datetime
from app.config import settings

STYLES = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --primary: #2FA4E7;
    --secondary: #6EC6FF;
    --text: #0E1726;
    --text-light: #6B7280;
    --bg: #FFFFFF;
    --bg-sec: #F5FAFE;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.7;
    color: var(--text);
    background: linear-gradient(135deg, #0F1218 0%, #0E1726 100%);
    min-height: 100vh;
    padding: 20px;
}
.container {
    max-width: 900px;
    margin: 0 auto;
    background: var(--bg);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(15,18,24,0.4);
}
.header {
    background: linear-gradient(135deg, #2FA4E7 0%, #6EC6FF 100%);
    color: #FFFFFF;
    padding: 60px 40px;
    text-align: center;
}
.header h1 { font-size: 3em; margin-bottom: 10px; }
.header .subtitle { font-size: 1.2em; opacity: 0.95; }
.nav-container {
    background: var(--bg-sec);
    padding: 20px 40px;
    border-bottom: 1px solid #DDEAF3;
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}
.nav a {
    color: var(--primary);
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 6px;
    background: #FFFFFF;
    border: 2px solid #DDEAF3;
    transition: all 0.2s;
}
.nav a:hover,
.nav a.active {
    background: var(--primary);
    color: #FFFFFF;
    transform: translateY(-2px);
}
.content { padding: 60px 40px; }
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    margin: 40px 0;
}
.feature {
    background: var(--bg-sec);
    padding: 30px;
    border-radius: 12px;
    border: 2px solid #DDEAF3;
}
.feature-icon { font-size: 3em; margin-bottom: 15px; }
.feature h3 {
    color: var(--primary);
    margin-bottom: 10px;
}
.cta-button {
    display: inline-block;
    background: var(--primary);
    color: #FFFFFF;
    padding: 15px 40px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    margin: 20px 10px;
    transition: all 0.3s;
}
.cta-button:hover {
    background: var(--secondary);
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(47,164,231,0.45);
}
.section {
    margin-bottom: 40px;
    scroll-margin-top: 100px;
}
.section h2 {
    color: var(--primary);
    font-size: 1.8em;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 3px solid var(--primary);
}
.section h3 {
    color: var(--secondary);
    font-size: 1.3em;
    margin: 20px 0 10px;
}
.section p,
.section li {
    color: var(--text-light);
    margin-bottom: 10px;
}
.section ul { margin: 15px 0 15px 30px; }
.section a {
    color: var(--primary);
    text-decoration: none;
}
.section a:hover {
    border-bottom: 1px solid var(--primary);
}
.highlight {
    background: #EAF7FF;
    border-left: 4px solid var(--primary);
    padding: 20px;
    margin: 20px 0;
    border-radius: 4px;
}
.contact-info {
    background: var(--bg-sec);
    padding: 25px;
    border-radius: 8px;
    border-left: 4px solid var(--primary);
    margin: 20px 0;
}
.footer {
    background: var(--bg-sec);
    padding: 40px;
    text-align: center;
    border-top: 1px solid #DDEAF3;
    color: var(--text-light);
}
.footer a {
    color: var(--primary);
    text-decoration: none;
}
code {
    background: #F0F8FF;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: Monaco, monospace;
    font-size: 0.9em;
    color: var(--primary);
}
@media (max-width: 768px) {
    body { padding: 10px; }
    .header { padding: 40px 20px; }
    .header h1 { font-size: 2em; }
    .content { padding: 40px 20px; }
}
</style>
"""


def render_page(title, header_icon, header_title, content, active_page="home"):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="static/favicon.png" />
    <title>{title} - {settings.app_name}</title>
    {STYLES}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{header_icon} {header_title}</h1>
            <div class="subtitle">Your Personal AI Email Agent</div>
        </div>
        
        <div class="nav-container">
            <nav class="nav">
                <a href="/" class="{'active' if active_page == 'home' else ''}">🏠 Home</a>
                <a href="/privacy" class="{'active' if active_page == 'privacy' else ''}">🔒 Privacy</a>
                <a href="/terms" class="{'active' if active_page == 'terms' else ''}">📜 Terms</a>
            </nav>
        </div>
        
        <div class="content">{content}</div>
        
        <div class="footer">
            <p><strong>{settings.app_name}</strong></p>
            <p>📧 <a href="mailto:{settings.app_email}">{settings.app_email}</a> | 
               💬 <a href="https://t.me/{settings.app_telegram}">{settings.app_telegram}</a> | 
               🐙 <a href="{settings.app_github}">GitHub</a></p>
            <p style="margin-top: 20px;">
                <a href="/">Home</a> | <a href="/terms">Terms</a> | <a href="/privacy">Privacy</a>
            </p>
            <p style="margin-top: 20px; font-size: 0.85em; opacity: 0.7;">
                © {datetime.now().year} {settings.app_name}. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""


HOME = f"""
    <div style="text-align: center; padding: 40px 0;">
        <h2 style="font-size: 2.5em; color: var(--primary); margin-bottom: 20px;">
            Automate Your Gmail with AI
        </h2>
        <p style="font-size: 1.2em; color: var(--text-light); margin-bottom: 30px;">
            Intelligent email management powered by Claude AI and Telegram
        </p>
        <div>
            <a href="https://t.me/{settings.app_telegram}" class="cta-button">🚀 Start Using Now</a>
            <a href="{settings.app_github}" class="cta-button" style="background: #6b7280;">📖 View Docs</a>
        </div>
    </div>
    
    <div class="feature-grid">
        <div class="feature">
            <div class="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Claude AI analyzes your emails and suggests smart responses automatically</p>
        </div>
        
        <div class="feature">
            <div class="feature-icon">⚡</div>
            <h3>Auto-Reply Rules</h3>
            <p>Set custom rules and let the bot handle routine emails for you</p>
        </div>
        
        <div class="feature">
            <div class="feature-icon">🔒</div>
            <h3>Secure & Private</h3>
            <p>OAuth2 authentication, encrypted tokens, emails never stored</p>
        </div>
        
        <div class="feature">
            <div class="feature-icon">📱</div>
            <h3>Telegram Interface</h3>
            <p>Manage everything from your phone via Telegram bot</p>
        </div>
        
        <div class="feature">
            <div class="feature-icon">📝</div>
            <h3>Smart Templates</h3>
            <p>Create reusable templates with variables for personalized responses</p>
        </div>
        
        <div class="feature">
            <div class="feature-icon">📊</div>
            <h3>Audit Trail</h3>
            <p>Complete logs of all actions taken by the bot for transparency</p>
        </div>
    </div>
    
    <div style="background: var(--bg-sec); padding: 40px; border-radius: 12px; margin: 40px 0;">
        <h3 style="text-align: center; color: var(--primary); margin-bottom: 30px; font-size: 2em;">
            How It Works
        </h3>
        <div style="display: grid; gap: 25px;">
            <div style="display: flex; align-items: start; gap: 20px;">
                <div style="background: var(--primary); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;">1</div>
                <div>
                    <h4 style="color: var(--text); margin-bottom: 5px;">Connect Your Gmail</h4>
                    <p>Securely authorize {settings.app_name} to access your Gmail via OAuth2</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: start; gap: 20px;">
                <div style="background: var(--primary); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;">2</div>
                <div>
                    <h4 style="color: var(--text); margin-bottom: 5px;">Set Your Preferences</h4>
                    <p>Create templates, configure rules, and customize automation settings</p>
                </div>
            </div>
            
            <div style="display: flex; align-items: start; gap: 20px;">
                <div style="background: var(--primary); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;">3</div>
                <div>
                    <h4 style="color: var(--text); margin-bottom: 5px;">Let AI Work</h4>
                    <p>Get real-time notifications in Telegram with smart reply suggestions</p>
                </div>
            </div>
        </div>
    </div>

    <div style="text-align: center; padding: 40px 0;">
        <h3 style="color: var(--primary); margin-bottom: 20px; font-size: 2em;">
            Ready to Transform Your Email?
        </h3>
        <a href="https://t.me/{settings.app_telegram}" class="cta-button" style="font-size: 1.2em;">
            Get Started Free
        </a>
        <p style="margin-top: 15px; color: var(--text-light);">
            No credit card required • OAuth2 Secure • Free forever
        </p>
    </div>
    """

PRIVACY_POLICY = f"""
    <div class="highlight">
        <p><strong>📌 Quick Summary:</strong> We process your emails with AI but never store them. Your data is encrypted, we don't sell information, and you can delete your account anytime.</p>
    </div>
    
    <div class="section" id="intro">
        <h2>1. Introduction</h2>
        <p>Welcome to {settings.app_name}. This Privacy Policy explains how we collect, use, and protect your information when you use our Telegram bot that integrates with Gmail using AI.</p>
    </div>
    
    <div class="section" id="collection">
        <h2>2. Information We Collect</h2>
        <h3>2.1 What We Collect</h3>
        <ul>
            <li><strong>Gmail Account:</strong> Email address and basic profile</li>
            <li><strong>Telegram:</strong> User ID and username</li>
            <li><strong>Templates & Settings:</strong> Your custom configurations</li>
            <li><strong>Email Metadata:</strong> Subjects, senders, timestamps</li>
        </ul>
        <h3>2.2 What We DON'T Store</h3>
        <ul>
            <li>Your Google password</li>
            <li>Complete email messages (processed in real-time only)</li>
            <li>Email attachments</li>
            <li>Data from other Google services</li>
        </ul>
    </div>
    
    <div class="section" id="usage">
        <h2>3. How We Use Your Data</h2>
        <ul>
            <li><strong>Service Provision:</strong> Provide email management features</li>
            <li><strong>AI Processing:</strong> Analyze emails and generate responses</li>
            <li><strong>Automation:</strong> Execute your configured rules</li>
            <li><strong>Security:</strong> Detect and prevent abuse</li>
        </ul>
    </div>
    
    <div class="section" id="ai">
        <h2>4. AI & Third-Party Services</h2>
        <h3>4.1 Anthropic Claude AI</h3>
        <ul>
            <li>Email content sent via secure HTTPS</li>
            <li>Processed in real-time, not permanently stored</li>
            <li>Governed by <a href="https://www.anthropic.com/privacy" target="_blank">Anthropic's Privacy Policy</a></li>
        </ul>
        <h3>4.2 Google Gmail API</h3>
        <ul>
            <li>OAuth2 authentication (no password storage)</li>
            <li>Only <code>gmail.modify</code> scope requested</li>
            <li>Revoke access anytime in <a href="https://myaccount.google.com/permissions" target="_blank">Google Settings</a></li>
        </ul>
    </div>
    
    <div class="section" id="security">
        <h2>5. Data Security</h2>
        <ul>
            <li><strong>Encryption:</strong> TLS/SSL for data in transit, AES-256 for tokens at rest</li>
            <li><strong>Access Control:</strong> Strict authentication and authorization</li>
            <li><strong>Minimal Data:</strong> Collect only what's necessary</li>
            <li><strong>Retention:</strong> Audit logs kept for 90 days</li>
        </ul>
    </div>
    
    <div class="section" id="rights">
        <h2>6. Your Rights</h2>
        <ul>
            <li><strong>Access:</strong> Export your data with <code>/export_data</code></li>
            <li><strong>Delete:</strong> Remove account with <code>/delete_account</code></li>
            <li><strong>Revoke:</strong> Disconnect Gmail access anytime</li>
            <li><strong>GDPR/CCPA:</strong> Full compliance with privacy regulations</li>
        </ul>
    </div>
    
    <div class="section" id="contact">
        <h2>7. Contact Us</h2>
        <div class="contact-info">
            <p><strong>Privacy Questions:</strong> <a href="mailto:{settings.app_email}">{settings.app_email}</a></p>
            <p><strong>Telegram Support:</strong> <a href="https://t.me/emmanuelonyekaba">@emmanuelonyekaba</a></p>
        </div>
    </div>
    
    <p style="text-align: center; color: var(--text-light); margin-top: 40px;">
        <strong>Effective Date:</strong> January 1, 2024 | <strong>Last Updated:</strong> January 5, 2024
    </p>
    """

TERMS_OF_SERVICE = f"""
    <div class="section" id="acceptance">
        <h2>1. Acceptance of Terms</h2>
        <p>By using {settings.app_name}, you agree to these Terms of Service. If you don't agree, please don't use our service.</p>
    </div>
    
    <div class="section" id="service">
        <h2>2. Service Description</h2>
        <p>{settings.app_name} provides AI-powered email management for Gmail through a Telegram bot interface, including:</p>
        <ul>
            <li>Automated email organization and categorization</li>
            <li>AI-generated response suggestions</li>
            <li>Template-based auto-replies</li>
            <li>Custom automation rules</li>
        </ul>
    </div>
    
    <div class="section" id="accounts">
        <h2>3. User Accounts</h2>
        <h3>3.1 Requirements</h3>
        <ul>
            <li>Valid Telegram and Gmail accounts</li>
            <li>Must be 13+ years old (16+ in EU)</li>
            <li>Responsible for account security</li>
        </ul>
        <h3>3.2 Your Responsibilities</h3>
        <ul>
            <li>Maintain confidentiality of credentials</li>
            <li>Notify us of unauthorized access</li>
            <li>Use service only for lawful purposes</li>
        </ul>
    </div>
    
    <div class="section" id="use">
        <h2>4. Acceptable Use Policy</h2>
        <h3>4.1 Prohibited Activities</h3>
        <p>You agree NOT to:</p>
        <ul>
            <li>Send spam, phishing, or malicious content</li>
            <li>Violate any laws or third-party rights</li>
            <li>Harass or harm others</li>
            <li>Attempt unauthorized system access</li>
            <li>Reverse engineer the service</li>
            <li>Use for commercial purposes without permission</li>
        </ul>
    </div>
    
    <div class="section" id="gmail">
        <h2>5. Gmail Access</h2>
        <h3>5.1 Permissions Granted</h3>
        <p>By connecting Gmail, you authorize us to:</p>
        <ul>
            <li>Read email messages and metadata</li>
            <li>Send emails on your behalf</li>
            <li>Modify labels and organization</li>
            <li>Create drafts and manage threads</li>
        </ul>
        <h3>5.2 Your Responsibilities</h3>
        <ul>
            <li>Review AI-generated responses before auto-send</li>
            <li>Configure appropriate filters and rules</li>
            <li>Comply with Gmail's terms of service</li>
        </ul>
    </div>
    
    <div class="section" id="ai-limits">
        <h2>6. AI Services & Limitations</h2>
        <ul>
            <li>AI-generated content may not always be accurate</li>
            <li>Review responses before sending</li>
            <li>We're not liable for AI-generated content consequences</li>
            <li>Email categorization not guaranteed to be perfect</li>
        </ul>
    </div>
    
    <div class="section" id="termination">
        <h2>7. Termination</h2>
        <h3>7.1 By You</h3>
        <ul>
            <li>Stop using service anytime</li>
            <li>Delete account: <code>/delete_account</code></li>
            <li>Revoke Gmail access in Google Settings</li>
        </ul>
        <h3>7.2 By Us</h3>
        <p>We may terminate access if you:</p>
        <ul>
            <li>Violate these Terms</li>
            <li>Engage in fraudulent activity</li>
            <li>Pose security risks</li>
        </ul>
    </div>
    
    <div class="section" id="disclaimers">
        <h2>8. Disclaimers & Liability</h2>
        <h3>8.1 Service "As Is"</h3>
        <p>Service provided "AS IS" without warranties of any kind including merchantability, fitness for purpose, or uninterrupted service.</p>
        <h3>8.2 Limitation of Liability</h3>
        <p>We are NOT liable for:</p>
        <ul>
            <li>Indirect or consequential damages</li>
            <li>Loss of data or profits</li>
            <li>Unauthorized account access</li>
            <li>AI-generated content issues</li>
        </ul>
    </div>
    
    <div class="section" id="privacy-link">
        <h2>9. Privacy</h2>
        <p>Your use is governed by our <a href="/privacy">Privacy Policy</a>. Key points:</p>
        <ul>
            <li>We don't store your emails permanently</li>
            <li>Data is encrypted</li>
            <li>We don't sell your information</li>
            <li>Request deletion anytime</li>
        </ul>
    </div>
    
    <div class="section" id="changes">
        <h2>10. Changes to Terms</h2>
        <p>We may modify these terms. Material changes will be notified via Telegram and email. Continued use constitutes acceptance.</p>
    </div>
    
    <div class="section" id="contact-legal">
        <h2>11. Contact</h2>
        <div class="contact-info">
            <p><strong>Legal Questions:</strong> <a href="mailto:{settings.app_email}">{settings.app_email}</a></p>
            <p><strong>Support:</strong> <a href="mailto:{settings.app_email}">{settings.app_email}</a></p>
        </div>
    </div>
    
    <p style="text-align: center; color: var(--text-light); margin-top: 40px;">
        <strong>Effective Date:</strong> January 1, 2024 | <strong>Last Updated:</strong> January 5, 2024
    </p>
    """
