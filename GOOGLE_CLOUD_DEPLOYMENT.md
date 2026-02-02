# Google Cloud Deployment Guide

## Project Info
- **Project ID**: restaurant-ordering-app-2
- **Project Number**: 29492958482

## Step-by-Step Deployment

### Step 1: Install Google Cloud SDK
```bash
brew install --cask google-cloud-sdk
```

### Step 2: Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project restaurant-ordering-app-2
```

### Step 3: Enable Required APIs
```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable vpcaccess.googleapis.com
```

### Step 4: Create Cloud SQL Instance (PostgreSQL)
```bash
gcloud sql instances create restaurant-db \
  --database-version=POSTGRES_12 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --storage-type=PD_SSD
```

### Step 5: Create Database and User
```bash
# Create the database
gcloud sql databases create restaurant_app --instance=restaurant-db

# Create a user
gcloud sql users create postgres --instance=restaurant-db --password
```
When prompted, enter a strong password and **remember it**.

### Step 6: Create VPC Connector (for secure connection)
```bash
gcloud compute networks vpc-access connectors create restaurant-connector \
  --region=us-central1 \
  --subnet=default
```

### Step 7: Initialize Database
```bash
# First, allow local access temporarily
gcloud sql instances patch restaurant-db --allow-no-password

# Run initialization script locally
python database/initialize.py

# Or from your local machine with the public IP
```

### Step 8: Update app.yaml
Edit `app.yaml` and replace `[PASSWORD]` with your actual PostgreSQL password from Step 5.

### Step 9: Deploy to Google App Engine
```bash
gcloud app deploy
```

The deployment will take a few minutes. Once complete, your app will be available at:
```
https://restaurant-ordering-app-2.appspot.com
```

## Environment Variables Setup

Before deployment, set secure environment variables:

```bash
# Set SECRET_KEY securely
gcloud app deploy --set-env-vars SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

## Verify Deployment
```bash
# Check deployment status
gcloud app describe

# View logs
gcloud app logs read --limit=50

# Open in browser
gcloud app browse
```

## Troubleshooting

### Database Connection Issues
```bash
# Check Cloud SQL instance status
gcloud sql instances describe restaurant-db

# List instances
gcloud sql instances list
```

### View Application Logs
```bash
gcloud app logs read --limit=100 --follow
```

### Redeploy
```bash
gcloud app deploy --version=v2
```

## Cost Optimization

- Cloud SQL: db-f1-micro is free tier eligible (~$15/month)
- App Engine: Standard environment is free tier eligible
- VPC Connector: ~$10/month

## Production Recommendations

1. **Set a strong SECRET_KEY** (use a secure random string)
2. **Use Environment Variables** for sensitive data
3. **Enable Firewall Rules** for database access
4. **Setup Monitoring** via Google Cloud Console
5. **Enable Cloud SQL Backup** for disaster recovery

## Cleanup (if needed)
```bash
# Delete the deployment
gcloud app versions delete [VERSION_ID]

# Delete Cloud SQL instance
gcloud sql instances delete restaurant-db
```

## Next Steps
1. Run the deployment commands above in order
2. Test the application at the appspot.com URL
3. Monitor logs for any errors
4. Setup custom domain (optional)
