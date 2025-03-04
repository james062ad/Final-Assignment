# Deployment Guide

## Prerequisites
- Python 3.8+
- Node.js 14+
- GitHub Desktop
- Render account
- Vercel account

## Version Control Setup (GitHub Desktop)
1. Open GitHub Desktop
2. Clone the repository:
   - Click "File" → "Clone Repository"
   - Select the repository from the list or use URL
   - Choose local path
   - Click "Clone"

3. Managing changes:
   - Changes will appear in GitHub Desktop automatically
   - Group related changes into commits
   - Write clear commit messages
   - Push changes using the "Push origin" button

## Local Development Setup

### Backend Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

4. Run Flask development server:
   ```bash
   flask run
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

## Deployment Steps

### Backend Deployment (Render)
1. Commit and push your changes using GitHub Desktop
2. Create new Web Service on Render
3. Connect your GitHub repository:
   - Select the repository from the list
   - Authorize Render if needed
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Set environment variables in Render dashboard
6. Deploy the service

### Frontend Deployment (Vercel)
1. Ensure all changes are committed and pushed using GitHub Desktop
2. Create new project on Vercel
3. Import your repository:
   - Select the repository from the list
   - Authorize Vercel if needed
4. Configure build settings:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
5. Set environment variables
6. Deploy the project

## Development Workflow with GitHub Desktop
1. **Starting Work**
   - Open GitHub Desktop
   - Fetch latest changes
   - Create new branch for features/fixes

2. **Making Changes**
   - Edit files locally
   - Changes appear automatically in GitHub Desktop
   - Group related changes into commits
   - Write descriptive commit messages

3. **Pushing Changes**
   - Review changes in GitHub Desktop
   - Push to origin using "Push origin" button
   - Create Pull Request if needed

4. **Updating Local Version**
   - Use "Fetch origin" to get latest changes
   - Resolve any conflicts if they appear
   - Keep local version in sync with remote

## Post-Deployment Verification
1. Test API endpoints
2. Verify frontend connectivity
3. Check model predictions
4. Validate visualization generation
5. Test error handling

## Troubleshooting
- Check logs in Render dashboard
- Verify environment variables
- Ensure all dependencies are installed
- Check CORS configuration
- Validate API endpoints
- Review GitHub Desktop history for recent changes

## Maintenance
- Monitor server resources
- Check error logs regularly
- Update dependencies as needed
- Backup model artifacts
- Keep repository synchronized using GitHub Desktop 