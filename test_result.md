#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "TrendScout - Testing P3: Product Outcome Learning System. Track launched products, update metrics, auto-label outcomes, view stats and insights."

backend:
  - task: "Track Product Outcome API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "POST /api/outcomes/track - creates a new outcome record for a product. Tested via curl - works correctly."

  - task: "Get My Outcomes API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "GET /api/outcomes/my - returns all tracked outcomes with summary stats. Supports ?status= filter."

  - task: "Update Outcome Metrics API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "PUT /api/outcomes/{id} - updates revenue, orders, ad_spend, days_active. Auto-computes ROI."

  - task: "Auto-Label Outcomes API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "POST /api/outcomes/auto-label - classifies pending outcomes based on metrics thresholds."

  - task: "Outcome Stats API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "GET /api/outcomes/stats - returns aggregated stats, avg scores, best categories, learning insights."

frontend:
  - task: "Outcomes Page with Summary Stats"
    implemented: true
    working: true
    file: "frontend/src/pages/OutcomesPage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "Full outcomes page with summary cards, score comparison, tracked products list with tabs, update form, auto-label button. Screenshot verified."

  - task: "Outcomes Nav Link in Dashboard Layout"
    implemented: true
    working: true
    file: "frontend/src/components/layouts/DashboardLayout.jsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "Added Outcomes nav item with Target icon between My Stores and Saved Products."

  - task: "Launch Wizard Outcome Tracking Integration"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/ProductLaunchWizard.jsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added trackOutcome() call on launch success. Added 'Track Outcomes' button in Step 5."

metadata:
  created_by: "main_agent"
  version: "3.0"
  test_sequence: 30
  run_ui: true

test_plan:
  current_focus:
    - "Track Product Outcome API"
    - "Get My Outcomes API"
    - "Update Outcome Metrics API"
    - "Auto-Label Outcomes API"
    - "Outcome Stats API"
    - "Outcomes Page with Summary Stats"
    - "Launch Wizard Outcome Tracking Integration"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "P3 Product Outcome Learning System implemented. All 5 backend endpoints tested via curl and working. Frontend OutcomesPage created with summary stats, score comparison cards, insights section, tracked products list with tabs (All/Pending/Success/Moderate/Failed), inline edit form for metrics, and auto-label button. Route /outcomes added. Nav link added in DashboardLayout. Launch Wizard now tracks outcomes on successful launch and shows 'Track Outcomes' button. Test data: 2 outcomes already exist (1 success, 1 moderate). Test credentials: email=testref@test.com, password=Test1234!"