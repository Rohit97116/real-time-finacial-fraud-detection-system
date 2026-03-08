# GitHub + Render Deployment (FraudLens AI)

## 1) Create Git repo and push to GitHub
```powershell
cd "C:\Users\mohit\OneDrive\Desktop\rohit\fraud_detection_system"
git init
git add .
git commit -m "Initial deploy-ready commit"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

## 2) Deploy on Render
1. Login to Render.
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub account and select this repository.
4. Render will detect `render.yaml` and create web service.
5. Wait for build and deploy to finish.
6. Open the generated URL (e.g. `https://fraudlens-ai.onrender.com`).

## Notes
- This deployment uses Docker and includes `tesseract-ocr` + `poppler-utils` for scanned-PDF support.
- On free plans, filesystem is ephemeral. Uploaded files/reports/history may reset after restart/redeploy.
