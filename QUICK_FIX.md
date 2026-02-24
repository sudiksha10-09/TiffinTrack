# Quick Fix for Plan Description Error

## The Error
```
value too long for type character varying(255)
```

## The Fix (30 seconds)

### On AWS Server:

```bash
# 1. Connect to your server
ssh ubuntu@your-server-ip

# 2. Go to project directory
cd ~/TiffinTrack

# 3. Run this ONE command
echo "ALTER TABLE plans ALTER COLUMN description TYPE TEXT;" | psql "$(grep DATABASE_URL .env | cut -d '=' -f2-)"

# 4. Restart app
sudo systemctl restart tiffintrack

# 5. Done! ✅
```

### Or Use the Script:

```bash
cd ~/TiffinTrack
chmod +x fix_description.sh
./fix_description.sh
sudo systemctl restart tiffintrack
```

### Or Use Neon Dashboard:

1. Go to https://console.neon.tech
2. Open SQL Editor
3. Paste: `ALTER TABLE plans ALTER COLUMN description TYPE TEXT;`
4. Click Run
5. Restart app: `sudo systemctl restart tiffintrack`

## Verify It Worked

```bash
# Check the logs
sudo journalctl -u tiffintrack -n 20 --no-pager

# Should see no errors when adding plans
```

## Now Try Again

1. Go to Admin → Manage Plans
2. Click "Add New Plan"
3. Write a LONG description (as long as you want!)
4. Upload image
5. Click "Create Plan"
6. Success! ✅

---

That's it! Your plan creation should work now.
