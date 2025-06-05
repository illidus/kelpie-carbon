# Kelp Carbon Tile Server - GitHub Pages Publisher (PowerShell)
# Syncs map tiles from main branch to gh-pages for public hosting

Write-Host "🌊 Publishing kelp carbon map tiles to GitHub Pages..." -ForegroundColor Cyan

# Configuration
$REPO_URL = git config --get remote.origin.url
$TILES_DIR = "tiles"
$TEMP_DIR = "temp_gh_pages"

# Check if tiles directory exists
if (-not (Test-Path $TILES_DIR)) {
    Write-Host "❌ Error: $TILES_DIR directory not found in current branch" -ForegroundColor Red
    Write-Host "Please ensure you're in the main branch with tiles/ directory"
    exit 1
}

# Get current commit for reference
$CURRENT_COMMIT = git rev-parse HEAD
$CURRENT_BRANCH = git branch --show-current

Write-Host "📦 Current branch: $CURRENT_BRANCH" -ForegroundColor Green
Write-Host "📦 Current commit: $CURRENT_COMMIT" -ForegroundColor Green

# Get tiles directory size
$tilesSize = (Get-ChildItem $TILES_DIR -Recurse | Measure-Object -Property Length -Sum).Sum
$tilesSizeMB = [math]::Round($tilesSize / 1MB, 2)
Write-Host "📦 Tiles directory size: ${tilesSizeMB}MB" -ForegroundColor Green

# Clean up any existing temp directory
if (Test-Path $TEMP_DIR) {
    Remove-Item $TEMP_DIR -Recurse -Force
}

# Clone the repository to a temporary directory
Write-Host "🔄 Cloning repository to temporary directory..." -ForegroundColor Yellow
git clone $REPO_URL $TEMP_DIR
Set-Location $TEMP_DIR

# Check if gh-pages branch exists remotely
$ghPagesExists = git ls-remote --heads origin gh-pages
if ($ghPagesExists) {
    Write-Host "🔄 Checking out existing gh-pages branch..." -ForegroundColor Yellow
    git checkout gh-pages
} else {
    Write-Host "🆕 Creating new gh-pages branch..." -ForegroundColor Yellow
    git checkout --orphan gh-pages
    git rm -rf . 2>$null
}

# Copy tiles from the original repository
Write-Host "📋 Syncing tiles from main branch..." -ForegroundColor Yellow
if (Test-Path $TILES_DIR) {
    Remove-Item $TILES_DIR -Recurse -Force
}
Copy-Item "..\$TILES_DIR" . -Recurse

# Create simple index.html if it doesn't exist
if (-not (Test-Path "index.html")) {
    Write-Host "📄 Creating index.html..." -ForegroundColor Yellow
    
    $indexContent = @"
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
            https://illidus.github.io/kelpie-carbon/tiles/{z}/{x}/{y}.png
        </div>
        <p>Standard XYZ tile format compatible with Leaflet, OpenLayers, and other mapping libraries.</p>
    </div>
    
    <div class="endpoint">
        <h2>Leaflet Usage Example</h2>
        <div class="code">
L.tileLayer(<br>
&nbsp;&nbsp;'https://illidus.github.io/kelpie-carbon/tiles/{z}/{x}/{y}.png',<br>
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
"@
    
    $indexContent | Out-File -FilePath "index.html" -Encoding UTF8
}

# Create .nojekyll to prevent GitHub from processing as Jekyll site
"" | Out-File -FilePath ".nojekyll" -Encoding UTF8

# Add all files and commit
Write-Host "💾 Committing changes to gh-pages..." -ForegroundColor Yellow
git add .
git config user.name "GitHub Actions"
git config user.email "actions@github.com"

git diff --staged --quiet
if ($LASTEXITCODE -ne 0) {
    $commitMessage = "🌊 Update kelp carbon tiles from main@$($CURRENT_COMMIT.Substring(0,7))`n`n- Synced tiles directory from main branch`n- Updated tile server at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')`n- Source commit: $CURRENT_COMMIT"
    git commit -m $commitMessage
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Blue
}

# Push to gh-pages
Write-Host "🚀 Pushing to gh-pages branch..." -ForegroundColor Yellow
git push origin gh-pages

# Clean up
Set-Location ..
Remove-Item $TEMP_DIR -Recurse -Force

Write-Host "✅ Tiles published successfully!" -ForegroundColor Green
Write-Host "📍 Tile endpoint will be available at:" -ForegroundColor Green
Write-Host "   https://illidus.github.io/kelpie-carbon/tiles/{z}/{x}/{y}.png"
Write-Host ""
Write-Host "⏱️  Note: GitHub Pages may take a few minutes to update" -ForegroundColor Yellow 