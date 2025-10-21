Param(
  [string]$CommitMessage = "Publish output"
)

$ErrorActionPreference = 'Stop'

# Resolve repo root
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "[1/4] Creating venv and installing deps"
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host "[2/4] Rendering site"
$env:OPENAI_API_KEY = $env:OPENAI_API_KEY  # expects already set; otherwise mock is used
python render.py

Write-Host "[3/4] Committing /output to gh-pages"
$branch = 'gh-pages'
if (-not (git rev-parse --verify $branch 2>$null)) {
  git checkout --orphan $branch
  git reset --hard
  git commit --allow-empty -m "Initialize gh-pages"
  git push -u origin $branch
  git checkout -
}

# subtree push of /output into gh-pages
git add output
if (-not (git diff --cached --quiet)) {
  git commit -m "$CommitMessage"
}

git subtree split --prefix output -b publish-tmp

git checkout $branch

git reset --hard

git read-tree --prefix=. -u publish-tmp

git commit -m "$CommitMessage" -a

git push origin $branch

git checkout -

git branch -D publish-tmp

Write-Host "[4/4] Done. Pages will serve from gh-pages root."