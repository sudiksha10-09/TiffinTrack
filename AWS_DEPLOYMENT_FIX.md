# AWS Deployment Fix - Static Images Not Loading

## Problem Identified ✅

**Issue**: Plan images showing broken on AWS but working locally

**Root Cause**: `.gitignore` was excluding `static/uploads/` directory, so dish images were never pushed to GitHub and therefore not deployed to AWS.

---

## What Was Wrong

### .gitignore Configuration (BEFORE)
```gitignore
# Uploads
uploads/
static/uploads/
```

This excluded ALL files in `static/uploads/` including the sample dish images needed for the app to work.

### .gitignore Configuration (AFTER - FIXED)
```gitignore
# Uploads (exclude user uploads but keep sample images)
# uploads/
# static/uploads/

# Note: Commented out to allow sample dish images to be committed
# In production, use S3 or similar for user uploads
```

---

## Files That Were Missing on AWS

```
static/uploads/dishes/
├── 20260201_132227_veg_thali.jpg
├── 20260201_132504_diet_bowl.jpg
├── 20260201_132843_chicken_combo_meal.jpg
├── 20260201_140842_veg_thali.jpg
├── 20260201_140905_chicken_combo_meal.jpg
└── 20260201_140931_diet_bowl.jpg
```

---

## Verification Checklist ✅

### 1. Template Image Paths (CORRECT)
All templates use proper Flask `url_for()`:
```html
<img src="{{ url_for('static', filename='uploads/dishes/' + plan.image_filename) }}" 
     alt="{{ plan.name }}">
```

✅ No hardcoded paths found
✅ All using `url_for('static', ...)`

### 2. Static Directory Structure (CORRECT)
```
TiffinTrack/
├── static/
│   ├── css/
│   │   └── professional.css
│   ├── images/
│   │   ├── logo.svg
│   │   ├── favicon.svg
│   │   ├── veg-thali.jpg
│   │   ├── diet-bowl.jpg
│   │   └── chicken-combo.jpg
│   ├── favicon/
│   │   └── (favicon files)
│   └── uploads/
│       └── dishes/
│           └── (6 dish images) ✅ NOW INCLUDED
```

### 3. File Permissions (CHECK ON AWS)
After deployment, verify:
```bash
ls -la ~/TiffinTrack/static/uploads/dishes/
```

Should show:
- 6 .jpg files
- Readable permissions (644 or similar)

---

## AWS Deployment Steps

### Step 1: Pull Latest Code
```bash
cd ~/TiffinTrack
git fetch origin
git reset --hard origin/main
```

### Step 2: Verify Images Exist
```bash
ls static/uploads/dishes/
```

Expected output:
```
20260201_132227_veg_thali.jpg
20260201_132504_diet_bowl.jpg
20260201_132843_chicken_combo_meal.jpg
20260201_140842_veg_thali.jpg
20260201_140905_chicken_combo_meal.jpg
20260201_140931_diet_bowl.jpg
```

### Step 3: Check Nginx Configuration
```bash
sudo nano /etc/nginx/sites-enabled/default
```

Ensure this block exists:
```nginx
location /static {
    alias /home/ubuntu/TiffinTrack/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### Step 4: Test Nginx Config
```bash
sudo nginx -t
```

Should output:
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 5: Restart Services
```bash
sudo systemctl restart tiffintrack
sudo systemctl reload nginx
```

### Step 6: Verify Services Running
```bash
sudo systemctl status tiffintrack
sudo systemctl status nginx
```

Both should show `active (running)` in green.

---

## Testing After Deployment

### 1. Direct Image Access Test
Open browser and try:
```
http://your-domain.com/static/uploads/dishes/20260201_132227_veg_thali.jpg
```

✅ Should display the image
❌ If 404: Images not deployed or Nginx config wrong
❌ If 403: Permission issue

### 2. Plans Page Test
Navigate to:
```
http://your-domain.com/plans
```

✅ All plan cards should show images
❌ If broken: Check browser console for exact error

### 3. Browser Console Check
Press F12 → Console tab

Look for errors like:
- `404 Not Found` → Images missing
- `403 Forbidden` → Permission issue
- `net::ERR_NAME_NOT_RESOLVED` → DNS/domain issue

---

## Common Issues & Solutions

### Issue 1: Images Still Not Loading After Pull
**Cause**: Git didn't pull because local changes exist

**Fix**:
```bash
cd ~/TiffinTrack
git stash
git pull origin main
git stash pop
```

### Issue 2: Permission Denied
**Cause**: Wrong file permissions

**Fix**:
```bash
chmod 644 ~/TiffinTrack/static/uploads/dishes/*.jpg
chmod 755 ~/TiffinTrack/static/uploads/dishes/
```

### Issue 3: Nginx 404 on /static
**Cause**: Nginx not configured to serve static files

**Fix**:
```bash
sudo nano /etc/nginx/sites-enabled/default
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/ubuntu/TiffinTrack/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Issue 4: Case Sensitivity (Linux vs Windows)
**Cause**: Filename case mismatch

**Check**:
```bash
# List actual filenames
ls static/uploads/dishes/

# Check database
sqlite3 instance/tiffintrack.db "SELECT image_filename FROM plans;"
```

Filenames must match EXACTLY (case-sensitive on Linux).

---

## Database Image Filename Check

If images still don't load, verify database has correct filenames:

```bash
# On AWS
cd ~/TiffinTrack
python3 << EOF
from app import app, db, Plan
with app.app_context():
    plans = Plan.query.all()
    for plan in plans:
        print(f"{plan.name}: {plan.image_filename}")
EOF
```

Expected output:
```
Veg Thali: 20260201_132227_veg_thali.jpg
Non-Veg Thali: 20260201_132843_chicken_combo_meal.jpg
Diet Special: 20260201_132504_diet_bowl.jpg
```

If filenames are wrong, update them:
```python
from app import app, db, Plan
with app.app_context():
    plan = Plan.query.filter_by(name="Veg Thali").first()
    plan.image_filename = "20260201_132227_veg_thali.jpg"
    db.session.commit()
```

---

## Prevention for Future

### For Development
Keep sample images in Git for demo purposes.

### For Production
1. Use S3 or similar cloud storage for user uploads
2. Update `.gitignore` to exclude user uploads but keep samples
3. Use environment variables for storage paths

### Recommended .gitignore
```gitignore
# Exclude user uploads but keep sample images
static/uploads/*
!static/uploads/dishes/
!static/uploads/dishes/*.jpg
```

---

## Quick Debug Commands

### Check if images exist
```bash
ls -lh ~/TiffinTrack/static/uploads/dishes/
```

### Check Nginx is serving static files
```bash
curl -I http://localhost/static/uploads/dishes/20260201_132227_veg_thali.jpg
```

Should return `200 OK`

### Check Flask app logs
```bash
sudo journalctl -u tiffintrack -n 50 --no-pager
```

### Check Nginx logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## Summary

**Problem**: `.gitignore` excluded `static/uploads/` → images never deployed
**Solution**: Updated `.gitignore` to allow sample images → committed images → deployed

**Files Changed**:
- `.gitignore` - Commented out `static/uploads/` exclusion
- Added 6 dish images to Git

**Deployment Required**:
1. `git pull` on AWS
2. Verify images exist
3. Restart services
4. Test in browser

---

**Status**: ✅ FIXED - Images now included in repository and will deploy to AWS
