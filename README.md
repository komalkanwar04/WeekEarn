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
