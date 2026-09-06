# AgriTwin AI — Reproducible PowerShell Setup & Soup Fine-Tuning Script
# Execution Guide for Windows PowerShell

$ErrorActionPreference = "Stop"

Write-Host "=== AgriTwin AI · Soup CLI Environment Setup & Training Workflow ===" -ForegroundColor Green

# 1. Environment Navigation & VirtualEnv Activation
Write-Host "`n[Step 1] Checking Virtual Environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "Creating python virtual environment (.venv)..."
    python -m venv .venv
}

Write-Host "Activating .venv..."
& .venv\Scripts\Activate.ps1

# 2. Dependency Verification & Installation
Write-Host "`n[Step 2] Upgrading pip and installing Soup CLI & Training dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install "soup-cli[train]" torch transformers peft datasets trl

# 3. Environment & GPU Pre-flight Doctor Check
Write-Host "`n[Step 3] Running Soup Doctor & GPU Pre-flight Check..." -ForegroundColor Yellow
python -m soup_cli env check
python -m soup_cli doctor

# 4. Dataset Generation & Quality Validation
Write-Host "`n[Step 4] Generating SFT Datasets from Real Agronomic Data..." -ForegroundColor Yellow
python ai/training/build_dataset.py

Write-Host "`n[Step 5] Validating Datasets with Quality & Hallucination Guard..." -ForegroundColor Yellow
python ai/training/validate_dataset.py

# 5. Model Training Execution
Write-Host "`n[Step 6] Executing Soup SFT Fine-Tuning Pipeline..." -ForegroundColor Yellow
python -m soup_cli train --config ai/soup/soup.yaml

# 6. Evaluation Suite Execution
Write-Host "`n[Step 7] Running Evaluation & Factuality Benchmark Suite..." -ForegroundColor Yellow
python ai/soup/evaluate.py

Write-Host "`n✅ AgriTwin AI Soup Fine-Tuning Workflow Finished Successfully!" -ForegroundColor Green
