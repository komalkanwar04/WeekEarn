# WeekEarn 🚀

A Python-based web platform connecting college students with local companies for exclusive Saturday and Sunday weekend jobs. It features a transparent first-come, first-serve application process, interactive job maps, and built-in instant chat messaging between applicants and employers.

## Features
- **Student Dashboard:** Filter weekend jobs by city, view salary info, and instantly secure roles via FCFS (First-Come, First-Serve).
- **Company Dashboard:** Add jobs with exact Google Map locations, track hired applicants, and view remaining open spots.
- **Built-In Chat & Notifications:** Real-time messaging between students and companies, with dynamic status alerts.
- **Public URL Sharing:** Pre-configured with Ngrok to instantly host the local app on the internet and share links with anyone.

## Running Locally

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Run the Server**
```bash
python app.py
```

3. **View App**
- Local: http://127.0.0.1:5050
- Internet: Check the terminal for your generated `https://...ngrok-free.app` link.

---

## Deploying to the Internet (Free)

The easiest way to host this application permanently is using [Render](https://render.com/).

### Steps to Deploy:
1. Push this code to a GitHub repository.
2. Go to **Render** and create a free account.
3. Click "New +" and select **Web Service**.
4. Connect your GitHub account and select this repository.
5. In the Render settings:
   - **Language:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (or it will automatically use the `Procfile` included).
6. Click **Create Web Service**. 

Once the build finishes (takes ~2 minutes), Render will provide you a permanent link to your app (e.g., `https://weekearn.onrender.com`) which you can share directly!

> **Note:** On free cloud tiers, the SQLite database (`weekearn.db`) resets itself when the server sleeps due to inactivity. If you want permanent data storage, you will later need to update the application to use a PostgreSQL database hosted on Render or Supabase.
