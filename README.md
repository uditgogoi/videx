# VIDEX — Text to Video App

Generate real AI videos from text prompts using the WAN 2.1 model via Replicate.

---

## 🚀 Deploy to Render (Free)

### Step 1 — Get a Replicate API Key
1. Go to [replicate.com](https://replicate.com) and sign up (free credits included)
2. Go to **Account → API Tokens**
3. Click **Create Token** and copy it (starts with `r8_...`)

### Step 2 — Push to GitHub
1. Create a new repo at [github.com/new](https://github.com/new) (name it `videx`)
2. Run these commands in your terminal:

```bash
cd videx
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/videx.git
git push -u origin main
```

### Step 3 — Deploy on Render
1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New → Web Service**
3. Connect your GitHub account and select the `videx` repo
4. Fill in:
   - **Name:** videx
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click **Add Environment Variable**:
   - Key: `REPLICATE_API_KEY`
   - Value: *(paste your Replicate token)*
6. Click **Create Web Service**

Render will build and deploy your app. In ~2 minutes you'll get a live URL like:
`https://videx.onrender.com`

---

## 💻 Run Locally

```bash
pip install -r requirements.txt
export REPLICATE_API_KEY=r8_your_token_here
python app.py
```

Then open: http://localhost:5000

---

## 💰 Cost
- Each 480p video costs ~$0.20 from your Replicate credits
- New accounts get ~$5 free credits = ~25 free videos
- 720p costs more and takes longer (~2.5 min)

## 📝 Tips for Best Prompts
- Add camera movement: "slow dolly zoom", "overhead crane shot", "panning left"
- Add lighting: "golden hour", "neon lit", "dramatic shadows"
- Be specific about subjects and actions
