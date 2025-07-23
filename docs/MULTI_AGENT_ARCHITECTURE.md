# Multi-Agent Framework Architecture Documentation

## How the Multi-Agent Framework Works

### 1. Query Processing Pipeline

```
User Query → Query Analysis → Agent Selection → SQL Generation → Data Retrieval → Response Generation
```

### 2. Current Framework Components

#### A. Multi-Agent Pipeline Orchestrator
- Receives user query
- Runs agents in sequence
- Combines results for final response

#### B. Specialized Agents

1. **Revenue Analysis Agent**
   - Detects revenue-related queries
   - Generates SQL for revenue metrics
   - Provides financial insights

2. **Client Analysis Agent**
   - Processes client-related queries
   - Creates SQL for client performance
   - Analyzes customer data

3. **Response Generation Agent**
   - Synthesizes analysis results
   - Creates natural language response
   - Provides business recommendations

### 3. Query Classification Logic

The system uses keyword-based detection:

```python
# Revenue queries
if "total" in query_lower and "revenue" in query_lower:
    # Execute total revenue SQL
    
elif "monthly" in query_lower or "trend" in query_lower:
    # Execute time-series SQL
    
# Client queries  
elif "top" in query_lower and ("client" in query_lower or "customer" in query_lower):
    # Execute top clients SQL
    
elif "performance" in query_lower:
    # Execute client performance SQL
```

### 4. Dynamic SQL Generation

Each agent contains multiple SQL templates that are selected based on query content:

```python
# Example: Revenue Analysis Agent SQL Selection
if "total" in query_lower and "revenue" in query_lower:
    sql = """
        SELECT 
            SUM(CAST(billdollars AS DECIMAL)) as total_revenue,
            COUNT(DISTINCT client) as client_count,
            COUNT(*) as total_records
        FROM input 
        WHERE billdollars IS NOT NULL
    """
elif "monthly" in query_lower:
    sql = """
        WITH monthly_data AS (...)
        SELECT month, revenue FROM monthly_data
    """
```

### 5. Current Limitations & Enhancement Opportunities

#### Current State:
- ✅ Basic keyword detection
- ✅ Static SQL templates
- ✅ Sequential agent execution
- ✅ Database-driven responses

#### Needs Enhancement:
- 🔄 More intelligent query classification
- 🔄 Dynamic SQL query generation
- 🔄 Context-aware agent selection
- 🔄 Natural language to SQL conversion
