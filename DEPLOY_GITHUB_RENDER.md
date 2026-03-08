# GitHub + Render Deployment (FraudLens AI)

## 1) Push latest code to GitHub
```powershell
cd "C:\Users\mohit\OneDrive\Desktop\rohit\real time finacial fraud detection system"
git add .
git commit -m "Prepare deployment"
git push origin main
```

## 2) Deploy on Render (Blueprint)
1. Open Render dashboard.
2. Click **New +** -> **Blueprint**.
3. Connect GitHub and select repository: `Rohit97116/real-time-finacial-fraud-detection-system`.
4. Render will read `render.yaml` and create service `fraudlens-ai`.
5. Wait for build + deploy to complete.
6. Open generated URL.

## 3) If service already exists
- Keep **Auto-Deploy ON**.
- Every push to `main` will redeploy automatically.

## Important notes
- Deployment uses Docker with `tesseract-ocr` and `poppler-utils` for scanned PDF support.
- On free plans, filesystem is ephemeral. Uploaded files/reports/history may reset after restart/redeploy.
