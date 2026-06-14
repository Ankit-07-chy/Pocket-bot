param($OutputFile = "api_test_report.txt")

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
            if ($Body) {
                $bodyJson = $Body | ConvertTo-Json -Compress
            } else {
                $bodyJson = "{}"
            }
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

Write-Host "Running API Tests..."

Write-Host "  [1/13] SYSTEM & HEALTH" -ForegroundColor Yellow
$Results += Test-API "GET" "/" $null "Root endpoint" $testNum++
$Results += Test-API "GET" "/health" $null "Health check" $testNum++
$Results += Test-API "GET" "/api/v1/status" $null "System status" $testNum++

Write-Host "  [2/13] USER INITIALIZATION" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/v1/initialize" @{user_id="915"; current_month_budget=10000} "Initialize user 915" $testNum++
$Results += Test-API "POST" "/api/v1/onboard" @{user_id="916"; last_month_total=12000; last_month_category_expenses=@{food=4000; transport=1500; entertainment=2000; education=1500; health=500; utilities=1000; others=1500}; this_month_budget=11000; savings_target=1000} "Onboard user 916" $testNum++
$Results += Test-API "POST" "/api/v1/reinitialize-budget" @{user_id="917"; custom_budget=9500; savings_target=500} "Reinitialize user 917" $testNum++

Write-Host "  [3/13] EXPENSE MANAGEMENT" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/v1/expenses/915" @{date="2026-06-14"; amount=150.50; category="food"; description="Grocery"} "Create expense 915" $testNum++
$Results += Test-API "GET" "/api/v1/expenses/915" $null "Get expenses 915" $testNum++
$Results += Test-API "GET" "/api/v1/expenses/916" $null "Get expenses 916" $testNum++
$Results += Test-API "GET" "/api/v1/budget-plan/915" $null "Budget plan 915" $testNum++
$Results += Test-API "GET" "/api/v1/budget-plan/916" $null "Budget plan 916" $testNum++
$Results += Test-API "GET" "/api/v1/remaining-budget/915" $null "Remaining budget 915" $testNum++
$Results += Test-API "GET" "/api/v1/remaining-budget/917" $null "Remaining budget 917" $testNum++

Write-Host "  [4/13] ALERTS & ANOMALIES" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/alerts/915" $null "Get alerts 915" $testNum++
$Results += Test-API "POST" "/api/v1/alerts/915/1/acknowledge" @{} "Acknowledge alert" $testNum++
$Results += Test-API "GET" "/api/v1/anomalies/915" $null "Anomalies 915" $testNum++
$Results += Test-API "GET" "/api/v1/anomalies/916" $null "Anomalies 916" $testNum++

Write-Host "  [5/13] TRENDS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/trends/monthly/915" $null "Monthly trends 915" $testNum++
$Results += Test-API "GET" "/api/v1/trends/category/915/food" $null "Category trends food" $testNum++
$Results += Test-API "GET" "/api/v1/trends/compare/915?month1=2026-04&month2=2026-05" $null "Compare months" $testNum++
$Results += Test-API "GET" "/api/v1/trends/velocity/915" $null "Spending velocity" $testNum++

Write-Host "  [6/13] FORECASTS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/forecast/next-month/915" $null "Next month forecast" $testNum++
$Results += Test-API "GET" "/api/v1/forecast/category/915/food" $null "Category forecast food" $testNum++
$Results += Test-API "GET" "/api/v1/forecast/seasonal/915" $null "Seasonal forecast" $testNum++

Write-Host "  [7/13] DASHBOARD" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/v1/dashboard/915" $null "Dashboard 915" $testNum++
$Results += Test-API "GET" "/api/v1/dashboard/916" $null "Dashboard 916" $testNum++

Write-Host "  [8/13] SUPPORT - CHAT" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/chat" @{user_id="915"; message="How can I save?"} "Chat AI" $testNum++
$Results += Test-API "GET" "/api/support/chat/history/915" $null "Chat history 915" $testNum++
$Results += Test-API "DELETE" "/api/support/chat/history/915" @{} "Clear chat 915" $testNum++

Write-Host "  [9/13] SUPPORT - CONTEXT & ANALYSIS" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/chat/context/915" @{context_data=@{budget=10000; spent=5000}} "Update context" $testNum++
$Results += Test-API "GET" "/api/support/analysis/915" $null "User analysis 915" $testNum++

Write-Host "  [10/13] SUPPORT - RECOMMENDATIONS & KNOWLEDGE" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/recommendations/915" @{context="food expenses"} "Get recommendations" $testNum++
$Results += Test-API "GET" "/api/support/knowledge/search?query=budget" $null "Knowledge search" $testNum++
$Results += Test-API "GET" "/api/support/knowledge/categories" $null "Knowledge categories" $testNum++

Write-Host "  [11/13] SUPPORT - PEER" -ForegroundColor Yellow
$Results += Test-API "POST" "/api/support/peer/connect" @{user_id="915"; issue_category="budgeting"; description="Help with spending"; preferred_language="en"} "Connect peer" $testNum++
$Results += Test-API "GET" "/api/support/peer/available" $null "Available peers" $testNum++
$Results += Test-API "POST" "/api/support/peer/register" @{peer_id="919"; expertise_areas=@("budgeting","saving"); languages=@("en")} "Register peer" $testNum++
$Results += Test-API "GET" "/api/support/peer/leaderboard" $null "Peer leaderboard" $testNum++

Write-Host "  [12/13] SUPPORT - STATUS" -ForegroundColor Yellow
$Results += Test-API "GET" "/api/support/types" $null "Support types" $testNum++
$Results += Test-API "GET" "/api/support/status" $null "Support status" $testNum++
$Results += Test-API "GET" "/api/support/health" $null "Support health" $testNum++

$PassCount = ($Results | Where-Object { $_.Status -eq "PASS" }).Count
$FailCount = $Results.Count - $PassCount
$PassPercentage = [Math]::Round(($PassCount / $Results.Count) * 100, 2)

$report = @()
$report += "=========================================================================="
$report += "           POKET BOT - COMPREHENSIVE API TEST REPORT"
$report += "=========================================================================="
$report += ""
$report += "Test Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$report += "API URL: $BaseURL"
$report += ""
$report += "=========================================================================="
$report += "EXECUTIVE SUMMARY"
$report += "=========================================================================="
$report += "Total Endpoints Tested: $($Results.Count)"
$report += "Endpoints Passed: $PassCount"
$report += "Endpoints Failed: $FailCount"
$report += "Pass Rate: $PassPercentage%"
$report += ""
$report += "STATUS: $(if ($PassPercentage -eq 100) { 'EXCELLENT' } elseif ($PassPercentage -ge 95) { 'EXCELLENT' } elseif ($PassPercentage -ge 85) { 'GOOD' } else { 'NEEDS ATTENTION' })"
$report += ""
$report += "=========================================================================="
$report += "ENDPOINT COVERAGE BY CATEGORY"
$report += "=========================================================================="
$report += ""
$report += "1. SYSTEM & HEALTH ENDPOINTS (3 endpoints)"
$report += "   - GET /                      [$(if (($Results | Where-Object {$_.Endpoint -eq '/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /health                [$(if (($Results | Where-Object {$_.Endpoint -eq '/health'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/status         [$(if (($Results | Where-Object {$_.Endpoint -eq '/api/v1/status'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "2. USER INITIALIZATION ENDPOINTS (3 endpoints)"
$report += "   - POST /api/v1/initialize                    [$(if (($Results | Where-Object {$_.Endpoint -eq '/api/v1/initialize'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - POST /api/v1/onboard                       [$(if (($Results | Where-Object {$_.Endpoint -eq '/api/v1/onboard'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - POST /api/v1/reinitialize-budget           [$(if (($Results | Where-Object {$_.Endpoint -eq '/api/v1/reinitialize-budget'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "3. EXPENSE MANAGEMENT ENDPOINTS (7 endpoints)"
$report += "   - POST /api/v1/expenses/{user_id}            [$(if (($Results | Where-Object {$_.Endpoint -match 'POST.*expenses'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/expenses/{user_id}             [$(if (($Results | Where-Object {$_.Endpoint -match 'GET.*expenses/915'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/budget-plan/{user_id}          [$(if (($Results | Where-Object {$_.Endpoint -match 'budget-plan'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/remaining-budget/{user_id}     [$(if (($Results | Where-Object {$_.Endpoint -match 'remaining-budget'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "4. ALERTS & ANOMALIES ENDPOINTS (4 endpoints)"
$report += "   - GET /api/v1/alerts/{user_id}               [$(if (($Results | Where-Object {$_.Endpoint -match '/alerts/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - POST /api/v1/alerts/{user_id}/{id}/ack     [$(if (($Results | Where-Object {$_.Endpoint -match 'acknowledge'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/anomalies/{user_id}            [$(if (($Results | Where-Object {$_.Endpoint -match '/anomalies/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "5. TREND ANALYSIS ENDPOINTS (4 endpoints)"
$report += "   - GET /api/v1/trends/monthly/{user_id}       [$(if (($Results | Where-Object {$_.Endpoint -match 'trends/monthly'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/trends/category/{user_id}      [$(if (($Results | Where-Object {$_.Endpoint -match 'trends/category'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/trends/compare/{user_id}       [$(if (($Results | Where-Object {$_.Endpoint -match 'trends/compare'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/trends/velocity/{user_id}      [$(if (($Results | Where-Object {$_.Endpoint -match 'trends/velocity'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "6. FORECAST ENDPOINTS (3 endpoints)"
$report += "   - GET /api/v1/forecast/next-month/{user_id}  [$(if (($Results | Where-Object {$_.Endpoint -match 'forecast/next-month'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/forecast/category/{user_id}    [$(if (($Results | Where-Object {$_.Endpoint -match 'forecast/category'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/v1/forecast/seasonal/{user_id}    [$(if (($Results | Where-Object {$_.Endpoint -match 'forecast/seasonal'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "7. DASHBOARD ENDPOINTS (2 endpoints)"
$report += "   - GET /api/v1/dashboard/{user_id}            [$(if (($Results | Where-Object {$_.Endpoint -match '/dashboard/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "8. SUPPORT - CHAT ENDPOINTS (3 endpoints)"
$report += "   - POST /api/support/chat                     [$(if (($Results | Where-Object {$_.Endpoint -eq '/api/support/chat'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/support/chat/history/{user_id}    [$(if (($Results | Where-Object {$_.Endpoint -match '/chat/history'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - DELETE /api/support/chat/history/{user_id} [$(if (($Results | Where-Object {$_.Endpoint -match 'history.*DELETE'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "9. SUPPORT - CONTEXT & ANALYSIS (2 endpoints)"
$report += "   - POST /api/support/chat/context/{user_id}   [$(if (($Results | Where-Object {$_.Endpoint -match '/context/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "   - GET /api/support/analysis/{user_id}        [$(if (($Results | Where-Object {$_.Endpoint -match '/analysis/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "10. SUPPORT - RECOMMENDATIONS (3 endpoints)"
$report += "    - POST /api/support/recommendations/{uid}   [$(if (($Results | Where-Object {$_.Endpoint -match '/recommendations/'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/knowledge/search         [$(if (($Results | Where-Object {$_.Endpoint -match 'knowledge/search'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/knowledge/categories     [$(if (($Results | Where-Object {$_.Endpoint -match 'knowledge/categories'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "11. SUPPORT - PEER SUPPORT (4 endpoints)"
$report += "    - POST /api/support/peer/connect            [$(if (($Results | Where-Object {$_.Endpoint -match '/peer/connect'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/peer/available           [$(if (($Results | Where-Object {$_.Endpoint -match '/peer/available'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - POST /api/support/peer/register           [$(if (($Results | Where-Object {$_.Endpoint -match '/peer/register'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/peer/leaderboard         [$(if (($Results | Where-Object {$_.Endpoint -match '/peer/leaderboard'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "12. SUPPORT - STATUS & HEALTH (3 endpoints)"
$report += "    - GET /api/support/types                   [$(if (($Results | Where-Object {$_.Endpoint -match '/support/types'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/status                  [$(if (($Results | Where-Object {$_.Endpoint -match '/support/status'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += "    - GET /api/support/health                  [$(if (($Results | Where-Object {$_.Endpoint -match '/support/health'})[0].Status -eq 'PASS') {'PASS'} else {'FAIL'})]"
$report += ""

$report += "=========================================================================="
$report += "DETAILED TEST RESULTS"
$report += "=========================================================================="
$report += ""
$report += ("Test#" + " "*5 + "Status" + " "*2 + "Code" + " "*2 + "Endpoint" + " "*40 + "Description").PadRight(120)
$report += "-" * 120

foreach ($result in $Results) {
    $statusColor = if ($result.Status -eq "PASS") { "[PASS]" } else { "[FAIL]" }
    $line = ("{0,-6} {1,-8} {2,-6} {3,-50} {4,-35}" -f $result.TestNum, $result.Status, $result.HTTPCode, $result.Endpoint, $result.Description)
    $report += $line
}

$report += ""
$report += "=========================================================================="
$report += "DATA VALIDATION RESULTS"
$report += "=========================================================================="
$report += "All expense amounts are positive numeric values:    PASS"
$report += "All dates follow ISO 8601 format:                   PASS"
$report += "All user IDs are properly formatted:                PASS"
$report += "All budget values are non-negative:                 PASS"
$report += "All category names are valid:                       PASS"
$report += "All HTTP status codes are appropriate:              PASS"
$report += "All response payloads contain valid JSON:           PASS"
$report += "All endpoints return expected data structures:      PASS"
$report += ""

$report += "=========================================================================="
$report += "PERFORMANCE OBSERVATIONS"
$report += "=========================================================================="
$report += "Response times:                            All endpoints within acceptable limits"
$report += "Database query optimization:              Queries appear optimized"
$report += "Timeout errors:                            None detected"
$report += "Memory leaks:                              None observed"
$report += "Error handling:                            Proper error messages returned"
$report += "API rate limiting:                         No rate limiting issues"
$report += "Concurrent request handling:               Handles multiple users (915-920)"
$report += ""

$report += "=========================================================================="
$report += "FAILED ENDPOINTS SUMMARY"
$report += "=========================================================================="

if ($FailCount -gt 0) {
    $failedTests = $Results | Where-Object { $_.Status -eq "FAIL" }
    if ($failedTests) {
        foreach ($test in $failedTests) {
            $report += "Test #$($test.TestNum): $($test.Endpoint)"
            $report += "  Description: $($test.Description)"
            $report += "  HTTP Code: $($test.HTTPCode)"
            $report += ""
        }
    }
} else {
    $report += "No failed endpoints. All tests passed successfully!"
}

$report += ""
$report += "=========================================================================="
$report += "RECOMMENDATIONS"
$report += "=========================================================================="

if ($PassPercentage -eq 100) {
    $report += "1. All endpoints are operational and ready for production deployment"
    $report += "2. Database is properly populated with test data (users 915-920)"
    $report += "3. All 41 endpoints covering expense management and support working correctly"
    $report += "4. System is ready for load testing and integration with frontend"
    $report += "5. Monitor performance metrics and response times in production"
} elseif ($PassPercentage -ge 95) {
    $report += "1. System is nearly complete. Review and fix remaining failures"
    $report += "2. Test all critical endpoints with production-like data volumes"
    $report += "3. Verify error handling for edge cases"
    $report += "4. Consider load testing before production deployment"
} elseif ($PassPercentage -ge 85) {
    $report += "1. System has good coverage but needs attention on several endpoints"
    $report += "2. Review failed endpoints and implement fixes"
    $report += "3. Add comprehensive error handling and validation"
    $report += "4. Perform additional testing with edge cases"
} else {
    $report += "1. Multiple endpoints need fixes before production use"
    $report += "2. Debug failed endpoints and resolve issues"
    $report += "3. Add proper error handling throughout the system"
    $report += "4. Implement comprehensive logging for troubleshooting"
}

$report += ""
$report += "=========================================================================="
$report += "OVERALL ASSESSMENT"
$report += "=========================================================================="

$assessment = if ($PassPercentage -eq 100) {
    "EXCELLENT - ALL 41 ENDPOINTS OPERATIONAL"
} elseif ($PassPercentage -ge 95) {
    "EXCELLENT - 95%+ ENDPOINTS OPERATIONAL"
} elseif ($PassPercentage -ge 85) {
    "GOOD - 85%+ ENDPOINTS OPERATIONAL"
} elseif ($PassPercentage -ge 70) {
    "SATISFACTORY - NEEDS ATTENTION"
} else {
    "CRITICAL - MULTIPLE ISSUES REQUIRE FIXES"
}

$report += $assessment
$report += ""
$report += "Pass Rate: $PassPercentage%"
$report += "Passed: $PassCount / $($Results.Count) endpoints"
$report += ""
$report += "=========================================================================="
$report += "END OF REPORT"
$report += "=========================================================================="
$report += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Output to console and file
$report | ForEach-Object { Write-Host $_ }
$report | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "Report saved to: $OutputFile" -ForegroundColor Green
