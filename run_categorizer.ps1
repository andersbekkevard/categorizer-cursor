Write-Host "Starting Norwegian Company Categorizer..." -ForegroundColor Green

# Activate virtual environment
& "myenv\Scripts\Activate.ps1"

# Set SSL verification to false for virtual desktops (uncomment if needed)
# $env:SSL_VERIFY = "false"

# Check if input file is provided
if ($args.Count -eq 0) {
    Write-Host "Usage: .\run_categorizer.ps1 input_file.csv" -ForegroundColor Red
    Write-Host "Example: .\run_categorizer.ps1 input\sample.csv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the categorizer
python categorize.py $args

# Keep window open to see results
Read-Host "Press Enter to exit" 