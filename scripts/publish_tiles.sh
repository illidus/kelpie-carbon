#!/bin/bash
set -e

# Kelp Carbon Tile Server - GitHub Pages Publisher
# Syncs map tiles from main branch to gh-pages for public hosting

echo "🌊 Publishing kelp carbon map tiles to GitHub Pages..."

# Configuration
REPO_URL=$(git config --get remote.origin.url)
TILES_DIR="tiles"
TEMP_DIR="temp_gh_pages"

# Check if tiles directory exists
if [ ! -d "$TILES_DIR" ]; then
    echo "❌ Error: $TILES_DIR directory not found in current branch"
    echo "Please ensure you're in the main branch with tiles/ directory"
    exit 1
fi

# Get current commit for reference
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git branch --show-current)

echo "📦 Current branch: $CURRENT_BRANCH"
echo "📦 Current commit: $CURRENT_COMMIT"
echo "📦 Tiles directory size: $(du -sh $TILES_DIR | cut -f1)"

# Clean up any existing temp directory
rm -rf "$TEMP_DIR"

# Clone the repository to a temporary directory
echo "🔄 Cloning repository to temporary directory..."
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# Check if gh-pages branch exists remotely
if git ls-remote --heads origin gh-pages | grep gh-pages > /dev/null; then
    echo "🔄 Checking out existing gh-pages branch..."
    git checkout gh-pages
else
    echo "🆕 Creating new gh-pages branch..."
    git checkout --orphan gh-pages
    git rm -rf . 2>/dev/null || true
fi

# Copy tiles from the original repository
echo "📋 Syncing tiles from main branch..."
rsync -av --delete "../$TILES_DIR/" "$TILES_DIR/"

# Create simple index.html if it doesn't exist
if [ ! -f "index.html" ]; then
    echo "📄 Creating index.html..."
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelp Carbon Tile Server</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .endpoint { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .code { background: #eee; padding: 10px; border-radius: 3px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌊 Kelp Carbon Tile Server</h1>
        <p>Map tiles for kelp biomass and carbon sequestration analysis</p>
    </div>
    
    <div class="endpoint">
        <h2>Tile Endpoint</h2>
        <div class="code">
            https://[username].github.io/[repo]/tiles/{z}/{x}/{y}.png
        </div>
        <p>Standard XYZ tile format compatible with Leaflet, OpenLayers, and other mapping libraries.</p>
    </div>
    
    <div class="endpoint">
        <h2>Leaflet Usage Example</h2>
        <div class="code">
L.tileLayer(<br>
&nbsp;&nbsp;'https://[username].github.io/[repo]/tiles/{z}/{x}/{y}.png',<br>
&nbsp;&nbsp;{ maxZoom: 14, attribution: 'Kelp Carbon Analysis' }<br>
).addTo(map);
        </div>
    </div>
    
    <div class="endpoint">
        <h2>About</h2>
        <p>This tile server hosts pre-generated map tiles for kelp forest carbon analysis. 
        The tiles show kelp biomass distribution and carbon sequestration estimates derived from 
        satellite spectral indices (FAI/NDRE) and machine learning models.</p>
        
        <p><strong>Data Sources:</strong> Sentinel-2 satellite imagery, Random Forest biomass prediction</p>
        <p><strong>Coverage:</strong> British Columbia coastal waters</p>
        <p><strong>Last Updated:</strong> <span id="lastUpdated"></span></p>
    </div>
    
    <script>
        document.getElementById('lastUpdated').textContent = new Date().toLocaleDateString();
    </script>
</body>
</html>
EOF
fi

# Create .nojekyll to prevent GitHub from processing as Jekyll site
touch .nojekyll

# Add all files and commit
echo "💾 Committing changes to gh-pages..."
git add .
git config user.name "GitHub Actions"
git config user.email "actions@github.com"

if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "🌊 Update kelp carbon tiles from main@${CURRENT_COMMIT:0:7}

- Synced tiles directory from main branch
- Updated tile server at $(date -u '+%Y-%m-%d %H:%M:%S UTC')
- Source commit: $CURRENT_COMMIT"
fi

# Push to gh-pages
echo "🚀 Pushing to gh-pages branch..."
git push origin gh-pages

# Clean up
cd ..
rm -rf "$TEMP_DIR"

echo "✅ Tiles published successfully!"
echo "📍 Tile endpoint will be available at:"
echo "   https://$(git config user.name).github.io/$(basename "$REPO_URL" .git)/tiles/{z}/{x}/{y}.png"
echo ""
echo "⏱️  Note: GitHub Pages may take a few minutes to update" 