# RAFIN PAN CARD SERVICE — Demo Retailer Portal

বাংলায় তৈরি একটি starter Flask project: Retailer Registration, Login, Admin Approval, Retailer ID এবং Admin Panel।

## গুরুত্বপূর্ণ
- এটি একটি **ডেমো/স্টার্টার প্রজেক্ট**, আসল PAN application/API বা payment integration নয়।
- বাস্তব গ্রাহকের PAN, Aadhaar, OTP, ব্যাংক তথ্য বা নথি এখানে সংগ্রহ করবেন না।
- Admin password ও SECRET_KEY deploy করার আগে environment variables থেকে সেট করুন।
- SQLite ডেটাবেস কিছু hosting-এ redeploy/restart হলে স্থায়ী নাও থাকতে পারে। বাস্তব ব্যবহারে persistent database লাগবে।
- Production-এর আগে HTTPS, rate limiting, CSRF protection, audit log, backups, privacy policy এবং security review যোগ করুন।

## লোকাল Windows 10-এ চালানো
1. Python 3.10+ ইনস্টল আছে কিনা দেখুন।
2. Command Prompt-এ এই ফোল্ডারে যান।
3. চালান:
   ```bat
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   set ADMIN_USERNAME=admin
   set ADMIN_PASSWORD=Use-A-Strong-Unique-Password
   set SECRET_KEY=replace-with-a-long-random-secret
   py app.py
   ```
4. ব্রাউজারে খুলুন `http://127.0.0.1:5000`

## GitHub-এ আপলোড
1. GitHub-এ নতুন **Private** repository তৈরি করুন, যেমন `rafin-pan-retailer`.
2. ZIP extract করে ফাইলগুলি repository-তে upload করুন (ZIP ফাইলটিকে একা upload করবেন না)।
3. `retailer.db`, `.env`, password বা secret কখনো upload করবেন না।

## Render-এ test deploy
- New → Web Service → GitHub repository connect করুন।
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables: `SECRET_KEY` (লম্বা random secret), `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- SQLite data persistence নিশ্চিত না করে এটিকে production service হিসেবে ব্যবহার করবেন না।

## Routes
- `/` Home
- `/register` Retailer registration
- `/login` Retailer login
- `/admin` Admin login
- `/admin/dashboard` Admin panel (login-এর পরে)
