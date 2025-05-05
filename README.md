🎭 Gmail Alias Generator
Welcome to your new secret weapon for unlimited signups, privacy, and inbox control!
Gmail Alias Generator lets you instantly create thousands of unique Gmail addresses that all land in your real inbox-no hacks, no data collection, no strings attached.

🚀 Pro Tips for Maximum Benefit
Unlimited Free Trials: Use a different alias for every signup-get as many free trials as you want, everywhere.

Organize Like a Pro: Paste your aliases into Google Keep, Todoist, or any checklist app. Each alias becomes a tickable item. Stay organized, stay ahead!

Alias Intelligence: Add website names or notes next to each alias in your checklist so you always know where you used them.

Spam Buster: If an alias gets spammed, you’ll know exactly who sold you out. Block or filter that alias in Gmail with a click.

One-Click Unsubscribe: Set up Gmail filters to auto-archive, label, or delete emails sent to a specific alias.

Password Simplicity: Use the same password for all aliases (or not-your call). Pair with a password manager for true mastery.

Zero Data Collection: Your aliases are wiped from the server the moment you leave. No logs, no tracking, no analytics. Your privacy is the default setting.

🖼️ Features
Generate up to 5,000 Gmail aliases at once-instantly

Export your list as TXT or Excel (XLSX) with one click

Copy all aliases to your clipboard instantly

Shuffle the background with Unsplash/Picsum for a fresh look every time

Frosted glass, modern UI for readability and style

No persistent storage-database is cleared when you leave

100% open source, privacy-first, and fun to use

⚡ Quick Start (Local)
Clone this repo:

bash
git clone https://github.com/mihir0209/gmail-alias-generator.git
cd gmail-alias-generator
Install dependencies:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Run the app:

bash
python app.py
Open http://localhost:5000 in your browser.

🌐 Deploy on Render (Recommended)
Push your project to GitHub.

Create a new Web Service on Render.

Set Build Command:
pip install -r requirements.txt

Set Start Command:
gunicorn app:app

Environment:

Python 3.10+

No persistent database needed

Click Deploy!
Your app will be live at https://your-app.onrender.com. (for me, your-app is reusegmaiil)

🛠️ Project Structure
text
gmail-alias-generator/
├── app.py
├── models.py
├── requirements.txt
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── utils/
│   └── alias_generator.py
✨ How It Works
Enter your Gmail address and the number of aliases you want.

Click "Generate Aliases"-your aliases appear instantly.

Copy all aliases or export as TXT/XLSX.

Shuffle the background for a fresh look.

Aliases are deleted from the server automatically when you leave.

🔒 Privacy & Data Policy
No data is stored between sessions.

All aliases are deleted from the database as soon as you close or reload the page.

No analytics, no tracking, no ads.

Open source and always will be.

💡 Advanced Usage
Gmail Filters:
Instantly organize or auto-delete emails to specific aliases.

Forwarding:
Use aliases as forwarding addresses for other accounts.

Security:
Use unique passwords for each alias for maximum protection (or keep it simple-your choice).

📋 Example: Using in Google Keep or Todoist
Generate your aliases.

Click "Copy All".

In Google Keep or Todoist, create a new checklist.

Paste your aliases-each will become a separate checkbox.

Add notes for each alias as needed.

🤝 Contributing
Pull requests and issues are welcome!
Help make this tool even more useful for everyone.

📄 License
MIT License

Enjoy your new superpower for free trials, privacy, and inbox control.
No rights reserved.