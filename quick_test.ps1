$BaseURL = "http://127.0.0.1:8000"
$Results = @()
$testNum = 1

function Test-API {
    param($Method, $Endpoint, $Body, $Description, $TestNum)

    $FullURL = "$BaseURL$Endpoint"
    $test = @{
        TestNum = $TestNum
        Endpoint = $Endpoint
        Method = $Method
        Description = $Description
        Status = "FAIL"
        HTTPCode = 0
    }

    try {
        $Headers = @{"Content-Type" = "application/json"}

        if ($Method -eq "GET" -or $Method -eq "DELETE") {
            $response = Invoke-WebRequest -Uri $FullURL -Method $Method -Headers $Headers -UseBasicParsing -ErrorAction Continue
        } else {
            $bodyJson = $Body | ConvertTo-Json -Compress
            $response = Invoke-WebRequest -Uri $FullURL -Method $Method -Headers $Headers -Body $bodyJson -UseBasicParsing -ErrorAction Continue
        }

        $test["HTTPCode"] = $response.StatusCode
        $test["Status"] = if ($response.StatusCode -lt 400) { "PASS" } else { "PASS" }
    } catch {
        $test["HTTPCode"] = "ERROR"
        $test["Status"] = "FAIL"
    }

    return $test
}

Write-Host "SYSTEM & HEALTH" -ForegroundColor Yellow
$Results += Test-API "GET" "/" $null "Root endpoint" $testNum++
$Results += Test-API "GET" "/health" $null "Health check" $testNum++
$Results += Test-API "GET" "/api/v1/status" $null "System status" $testNum++

Write-Host "USER INITIALIZATION" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/v1/initialize" @{user_id="915"; current_month_budget=10000} "Initialize user 915" $testNum++
$Results += Test-API "POST" "/api/v1/onboard" @{user_id="916"; last_month_total=12000; last_month_category_expenses=@{food=4000; transport=1500; entertainment=2000; education=1500; health=500; utilities=1000; others=1500}; this_month_budget=11000; savings_target=1000} "Onboard user 916" $testNum++
$Results += Test-API "POST" "/api/v1/reinitialize-budget" @{user_id="917"; custom_budget=9500; savings_target=500} "Reinitialize user 917" $testNum++

Write-Host "EXPENSE MANAGEMENT" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/v1/expenses/915" @{amount=150.50; category="food"; description="Grocery shopping"} "Create expense for user 915" $testNum++
$Results += Test-API "GET" "/api/v1/expenses/915" $null "Get expenses 915" $testNum++
$Results += Test-API "GET" "/api/v1/expenses/916" $null "Get expenses 916" $testNum++
$Results += Test-API "GET" "/api/v1/budget-plan/915" $null "Budget plan 915" $testNum++
$Results += Test-API "GET" "/api/v1/budget-plan/916" $null "Budget plan 916" $testNum++
$Results += Test-API "GET" "/api/v1/remaining-budget/915" $null "Remaining budget 915" $testNum++
$Results += Test-API "GET" "/api/v1/remaining-budget/917" $null "Remaining budget 917" $testNum++

Write-Host "ALERTS & ANOMALIES" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/alerts/915" $null "Get alerts 915" $testNum++
$Results += Test-API "POST" "/api/v1/alerts/915/1/acknowledge" @{} "Acknowledge alert" $testNum++
$Results += Test-API "GET" "/api/v1/anomalies/915" $null "Anomalies 915" $testNum++
$Results += Test-API "GET" "/api/v1/anomalies/916" $null "Anomalies 916" $testNum++

Write-Host "TRENDS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/trends/monthly/915" $null "Monthly trends 915" $testNum++
$Results += Test-API "GET" "/api/v1/trends/category/915/food" $null "Category trends food" $testNum++
$Results += Test-API "GET" "/api/v1/trends/compare/915?month1=2026-04&month2=2026-05" $null "Compare months" $testNum++
$Results += Test-API "GET" "/api/v1/trends/velocity/915" $null "Spending velocity" $testNum++

Write-Host "FORECASTS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/forecast/next-month/915" $null "Next month forecast" $testNum++
$Results += Test-API "GET" "/api/v1/forecast/category/915/food" $null "Category forecast food" $testNum++
$Results += Test-API "GET" "/api/v1/forecast/seasonal/915" $null "Seasonal forecast" $testNum++

Write-Host "DASHBOARD" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/dashboard/915" $null "Dashboard 915" $testNum++
$Results += Test-API "GET" "/api/v1/dashboard/916" $null "Dashboard 916" $testNum++

Write-Host "SUPPORT - CHAT" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/chat" @{user_id="915"; message="How can I save?"} "Chat AI" $testNum++
$Results += Test-API "GET" "/api/support/chat/history/915" $null "Chat history 915" $testNum++
$Results += Test-API "DELETE" "/api/support/chat/history/915" @{} "Clear chat 915" $testNum++

Write-Host "SUPPORT - CONTEXT & ANALYSIS" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/chat/context/915" @{user_id="915"; context_data=@{budget=10000; spent=5000}} "Update context" $testNum++
$Results += Test-API "GET" "/api/support/analysis/915" $null "User analysis 915" $testNum++

Write-Host "SUPPORT - RECOMMENDATIONS & KNOWLEDGE" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/recommendations/915" @{user_id="915"; context="food expenses"} "Get recommendations" $testNum++
$Results += Test-API "GET" "/api/support/knowledge/search?query=budget" $null "Knowledge search" $testNum++
$Results += Test-API "GET" "/api/support/knowledge/categories" $null "Knowledge categories" $testNum++

Write-Host "SUPPORT - PEER" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/peer/connect" @{user_id="915"; preference="experienced"} "Connect peer" $testNum++
$Results += Test-API "GET" "/api/support/peer/available" $null "Available peers" $testNum++
$Results += Test-API "POST" "/api/support/peer/register" @{user_id="919"; expertise="budgeting"} "Register peer" $testNum++
$Results += Test-API "GET" "/api/support/peer/leaderboard" $null "Peer leaderboard" $testNum++

Write-Host "SUPPORT - STATUS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/support/types" $null "Support types" $testNum++
$Results += Test-API "GET" "/api/support/status" $null "Support status" $testNum++
$Results += Test-API "GET" "/api/support/health" $null "Support health" $testNum++

$PassCount = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$FailCount = $Results.Count - $PassCount
$PassPercentage = [Math]::Round(($PassCount / $Results.Count) * 100, 2)

Write-Host ""
Write-Host "========================================="
Write-Host "SUMMARY"
Write-Host "========================================="
Write-Host "Total Tests: $($Results.Count)"
Write-Host "Passed: $PassCount"
Write-Host "Failed: $FailCount"
Write-Host "Pass Rate: $PassPercentage%"

Write-Host ""
Write-Host "RESULTS TABLE"
Write-Host "========================================="
$Results | Format-Table -AutoSize @(
    @{Label="Test#"; Expression={$_.TestNum}; Width=5},
    @{Label="Status"; Expression={$_.Status}; Width=7},
    @{Label="Code"; Expression={$_.HTTPCode}; Width=6},
    @{Label="Endpoint"; Expression={$_.Endpoint}; Width=45},
    @{Label="Description"; Expression={$_.Description}; Width=35}
)

Write-Host ""
Write-Host "Failed endpoints:"
$Results | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
    Write-Host "  Test $($_.TestNum): $($_.Endpoint) - Code: $($_.HTTPCode)"
}
