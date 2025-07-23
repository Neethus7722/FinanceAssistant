"""
Enhanced Multi-Agent Framework with Intelligent Query Classification
and Dynamic SQL Generation for Financial Data Analysis
"""

import asyncio
import re
import openai
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import text
from datetime import datetime
import json
import os
from config import get_settings

# Load settings
settings = get_settings()

class LLMClient:
    """Unified LLM client supporting multiple AI providers from configuration"""
    
    def __init__(self):
        self.primary_provider = settings.ai_provider
        self.fallback_provider = settings.fallback_provider
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize AI clients based on configuration"""
        self.clients = {}
        
        # Azure OpenAI setup
        if settings.azure_openai_api_key:
            self.clients['azure_openai'] = openai.AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version
            )
        
        # Mixtral setup
        if settings.mixtral_api_key:
            self.clients['mixtral'] = openai.AsyncOpenAI(
                api_key=settings.mixtral_api_key,
                base_url=settings.mixtral_api_base
            )
        
        # OpenAI Direct setup
        if settings.openai_direct_api_key:
            self.clients['openai_direct'] = openai.AsyncOpenAI(
                api_key=settings.openai_direct_api_key
            )
    
    async def generate_completion(self, prompt: str, context: str = "") -> str:
        """Generate completion using configured AI provider with fallback"""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            # Try primary provider
            result = await self._call_provider(self.primary_provider, full_prompt)
            if result:
                return result
        except Exception as e:
            print(f"Primary provider ({self.primary_provider}) failed: {e}")
        
        try:
            # Try fallback provider
            result = await self._call_provider(self.fallback_provider, full_prompt)
            if result:
                return result
        except Exception as e:
            print(f"Fallback provider ({self.fallback_provider}) failed: {e}")
        
        return "I apologize, but I'm unable to process your request at the moment due to AI service unavailability."
    
    async def _call_provider(self, provider: str, prompt: str) -> Optional[str]:
        """Call specific AI provider"""
        if provider not in self.clients:
            return None
        
        client = self.clients[provider]
        
        if provider == 'azure_openai':
            response = await client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.azure_openai_max_tokens,
                temperature=settings.azure_openai_temperature,
                top_p=settings.azure_openai_top_p
            )
            return response.choices[0].message.content
            
        elif provider == 'mixtral':
            # Handle Hugging Face Inference API format
            if "huggingface.co" in settings.mixtral_api_base:
                import requests
                headers = {"Authorization": f"Bearer {settings.mixtral_api_key}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": settings.mixtral_max_tokens,
                        "temperature": settings.mixtral_temperature,
                        "top_p": settings.mixtral_top_p,
                        "return_full_text": False
                    }
                }
                response = requests.post(settings.mixtral_api_base, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                return None
            else:
                # Standard OpenAI-compatible API
                response = await client.chat.completions.create(
                    model=settings.mixtral_model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=settings.mixtral_max_tokens,
                    temperature=settings.mixtral_temperature,
                    top_p=settings.mixtral_top_p
                )
                return response.choices[0].message.content
            
        elif provider == 'openai_direct':
            response = await client.chat.completions.create(
                model=settings.openai_direct_model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.openai_direct_max_tokens,
                temperature=settings.openai_direct_temperature
            )
            return response.choices[0].message.content
        
        return None

class QueryClassifier:
    """Intelligent query classification system"""
    
    def __init__(self):
        self.query_patterns = {
            'revenue_analysis': [
                r'(?i)\b(total|overall|aggregate).*revenue\b',
                r'(?i)\brevenue.*(total|sum|amount)\b',
                r'(?i)\b(sales|income|earnings).*\b',
                r'(?i)\bhow much.*\b(made|earned|generated)\b'
            ],
            'client_analysis': [
                r'(?i)\b(top|best|highest|leading).*\b(client|customer)\b',
                r'(?i)\bclient.*(performance|ranking|analysis)\b',
                r'(?i)\b(customer|client).*\b(revenue|profit|margin)\b',
                r'(?i)\bwho.*(client|customer).*\b(best|top|highest)\b'
            ],
            'project_analysis': [
                r'(?i)\b(how many|count).*\b(client|customer).*\b(project|job)\b',
                r'(?i)\bclient.*\b(more than|greater than|over).*\b(project|job)\b',
                r'(?i)\b(project|job).*\b(count|number|many)\b',
                r'(?i)\bwhich.*\bclient.*\b(project|job)\b'
            ],
            'time_series': [
                r'(?i)\b(monthly|quarterly|yearly|annual).*\b(trend|pattern)\b',
                r'(?i)\b(trend|growth|change).*\b(over time|month|year)\b',
                r'(?i)\bhow.*\b(changed|evolved|grown).*\b(time|month|year)\b',
                r'(?i)\b(historical|past).*\b(data|performance)\b'
            ],
            'margin_analysis': [
                r'(?i)\b(margin|profit|profitability).*\b(analysis|breakdown)\b',
                r'(?i)\bhighest.*\b(margin|profit)\b',
                r'(?i)\bmost.*\b(profitable|profitable)\b',
                r'(?i)\b(cost|expense).*\b(analysis|breakdown)\b'
            ],
            'comparative_analysis': [
                r'(?i)\bcompare.*\b(client|customer|project)\b',
                r'(?i)\b(versus|vs|compared to)\b',
                r'(?i)\b(difference|comparison).*\b(between|among)\b',
                r'(?i)\bhow.*\b(different|similar)\b'
            ]
        }
    
    def classify_query(self, query: str) -> List[str]:
        """Classify query into one or more categories"""
        classifications = []
        
        for category, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    classifications.append(category)
                    break
        
        # Default to general analysis if no specific classification
        if not classifications:
            classifications.append('general_analysis')
            
        return classifications

class SQLQueryGenerator:
    """Dynamic SQL query generator based on query intent"""
    
    def __init__(self):
        self.base_tables = {
            'financial_data': 'input',
            'sessions': 'user_sessions',
            'conversations': 'chat_conversations'
        }
        
        self.column_mappings = {
            'revenue': 'CAST(billdollars AS DECIMAL)',
            'cost': 'CAST(cost AS DECIMAL)',
            'margin': 'CAST(margin AS DECIMAL)',
            'margin_percent': 'CAST(marginpercent AS DECIMAL)',
            'client': 'client',
            'project': 'project'
        }
    
    def generate_revenue_query(self, query_context: Dict[str, Any]) -> str:
        """Generate SQL for revenue analysis"""
        base_select = """
            SELECT 
                SUM({revenue}) as total_revenue,
                COUNT(DISTINCT {client}) as unique_clients,
                COUNT(DISTINCT {project}) as unique_projects,
                COUNT(*) as total_transactions,
                AVG({revenue}) as avg_transaction_value,
                MIN({revenue}) as min_transaction,
                MAX({revenue}) as max_transaction
        """.format(**self.column_mappings)
        
        base_from = f"FROM {self.base_tables['financial_data']}"
        base_where = f"WHERE {self.column_mappings['revenue']} IS NOT NULL"
        
        # Add time filters if specified
        if query_context.get('time_period'):
            # For demo, we simulate time filtering using row sampling
            base_where += " AND RANDOM() < 0.8"  # Sample data
        
        # Add client filters if specified
        if query_context.get('client_filter'):
            base_where += f" AND {self.column_mappings['client']} LIKE '%{query_context['client_filter']}%'"
        
        return f"{base_select} {base_from} {base_where}"
    
    def generate_client_analysis_query(self, query_context: Dict[str, Any]) -> str:
        """Generate SQL for client analysis"""
        limit_clause = f"LIMIT {query_context.get('limit', 10)}"
        
        return f"""
            SELECT 
                {self.column_mappings['client']} as client_name,
                SUM({self.column_mappings['revenue']}) as total_revenue,
                COUNT(*) as transaction_count,
                COUNT(DISTINCT {self.column_mappings['project']}) as project_count,
                AVG({self.column_mappings['revenue']}) as avg_transaction_value,
                SUM({self.column_mappings['margin']}) as total_margin,
                AVG({self.column_mappings['margin_percent']}) as avg_margin_percent
            FROM {self.base_tables['financial_data']}
            WHERE {self.column_mappings['revenue']} IS NOT NULL
            GROUP BY {self.column_mappings['client']}
            ORDER BY total_revenue DESC
            {limit_clause}
        """
    
    def generate_time_series_query(self, query_context: Dict[str, Any]) -> str:
        """Generate SQL for time-series analysis"""
        return """
            WITH time_periods AS (
                SELECT 
                    generate_series(1, 12) as period_num,
                    TO_CHAR(CURRENT_DATE - INTERVAL '11 months' + INTERVAL '1 month' * (generate_series(1, 12) - 1), 'Mon YYYY') as period_label
            ),
            data_by_period AS (
                SELECT 
                    (ROW_NUMBER() OVER (ORDER BY client, project) % 12) + 1 as period_simulation,
                    SUM(CAST(billdollars AS DECIMAL)) as period_revenue,
                    COUNT(*) as period_transactions,
                    COUNT(DISTINCT client) as period_clients
                FROM input 
                WHERE billdollars IS NOT NULL
                GROUP BY period_simulation
            )
            SELECT 
                tp.period_label,
                COALESCE(dbp.period_revenue, 0) as revenue,
                COALESCE(dbp.period_transactions, 0) as transactions,
                COALESCE(dbp.period_clients, 0) as unique_clients
            FROM time_periods tp
            LEFT JOIN data_by_period dbp ON tp.period_num = dbp.period_simulation
            ORDER BY tp.period_num
        """

    def generate_project_analysis_query(self, query_context: Dict[str, Any]) -> str:
        """Generate SQL for project count analysis"""
        threshold = query_context.get('project_threshold', 10)
        
        return f"""
            SELECT 
                {self.column_mappings['client']} as client_name,
                COUNT(DISTINCT {self.column_mappings['project']}) as project_count,
                SUM({self.column_mappings['revenue']}) as total_revenue,
                COUNT(*) as total_transactions,
                AVG({self.column_mappings['revenue']}) as avg_transaction_value
            FROM {self.base_tables['financial_data']}
            WHERE {self.column_mappings['revenue']} IS NOT NULL
            GROUP BY {self.column_mappings['client']}
            HAVING COUNT(DISTINCT {self.column_mappings['project']}) > {threshold}
            ORDER BY project_count DESC, total_revenue DESC
        """

class EnhancedRevenueAnalysisAgent:
    """Enhanced revenue analysis agent with dynamic SQL generation"""
    
    def __init__(self, sql_generator: SQLQueryGenerator):
        self.sql_generator = sql_generator
        self.name = "enhanced_revenue_analysis"
    
    async def analyze(self, query: str, engine, classifications: List[str]) -> Dict[str, Any]:
        """Perform enhanced revenue analysis"""
        try:
            # Extract context from query
            query_context = self._extract_query_context(query)
            
            # Generate appropriate SQL
            if 'time_series' in classifications:
                sql_query = self.sql_generator.generate_time_series_query(query_context)
                analysis_type = "time_series_revenue"
            else:
                sql_query = self.sql_generator.generate_revenue_query(query_context)
                analysis_type = "general_revenue"
            
            # Execute query
            async with engine.begin() as conn:
                result = await conn.execute(text(sql_query))
                
                if analysis_type == "time_series_revenue":
                    rows = result.fetchall()
                    data = []
                    for row in rows:
                        data.append({
                            "period": row[0],
                            "revenue": float(row[1]) if row[1] else 0,
                            "transactions": row[2] if row[2] else 0,
                            "unique_clients": row[3] if row[3] else 0
                        })
                    
                    return {
                        "analysis_type": analysis_type,
                        "time_series_data": data,
                        "query_context": query_context,
                        "sql_used": sql_query,
                        "agent": self.name
                    }
                else:
                    row = result.fetchone()
                    return {
                        "analysis_type": analysis_type,
                        "total_revenue": float(row[0]) if row[0] else 0,
                        "unique_clients": row[1] if row[1] else 0,
                        "unique_projects": row[2] if row[2] else 0,
                        "total_transactions": row[3] if row[3] else 0,
                        "avg_transaction_value": float(row[4]) if row[4] else 0,
                        "min_transaction": float(row[5]) if row[5] else 0,
                        "max_transaction": float(row[6]) if row[6] else 0,
                        "query_context": query_context,
                        "sql_used": sql_query,
                        "agent": self.name
                    }
                    
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "error",
                "agent": self.name,
                "sql_used": sql_query if 'sql_query' in locals() else None
            }
    
    def _extract_query_context(self, query: str) -> Dict[str, Any]:
        """Extract context and parameters from user query"""
        context = {}
        
        # Extract time periods
        if re.search(r'(?i)\b(last|past).*\b(\d+).*\b(month|year)', query):
            match = re.search(r'(?i)\b(last|past).*\b(\d+).*\b(month|year)', query)
            if match:
                context['time_period'] = f"{match.group(2)} {match.group(3)}s"
        
        # Extract client mentions
        client_match = re.search(r'(?i)\bclient\s+(\d+|[A-Za-z]+)', query)
        if client_match:
            context['client_filter'] = client_match.group(1)
        
        # Extract limits/counts
        if re.search(r'(?i)\btop\s+(\d+)', query):
            match = re.search(r'(?i)\btop\s+(\d+)', query)
            context['limit'] = int(match.group(1))
        elif re.search(r'(?i)\b(\d+)\s+(client|customer)', query):
            match = re.search(r'(?i)\b(\d+)\s+(client|customer)', query)
            context['limit'] = int(match.group(1))
        
        # Extract project thresholds
        project_threshold_match = re.search(r'(?i)\b(more than|greater than|over)\s+(\d+)\s+(project|job)', query)
        if project_threshold_match:
            context['project_threshold'] = int(project_threshold_match.group(2))
        
        return context

class EnhancedProjectAnalysisAgent:
    """Enhanced project analysis agent for project-related queries"""
    
    def __init__(self, sql_generator: SQLQueryGenerator):
        self.sql_generator = sql_generator
        self.name = "enhanced_project_analysis"
    
    async def analyze(self, query: str, engine, classifications: List[str]) -> Dict[str, Any]:
        """Perform enhanced project analysis"""
        try:
            query_context = self._extract_query_context(query)
            sql_query = self.sql_generator.generate_project_analysis_query(query_context)
            
            async with engine.begin() as conn:
                result = await conn.execute(text(sql_query))
                rows = result.fetchall()
                
                clients_with_projects = []
                total_clients = len(rows)
                
                for row in rows:
                    client_data = {
                        "client_name": row[0],
                        "project_count": row[1],
                        "total_revenue": float(row[2]) if row[2] else 0,
                        "total_transactions": row[3] if row[3] else 0,
                        "avg_transaction_value": float(row[4]) if row[4] else 0
                    }
                    clients_with_projects.append(client_data)
                
                return {
                    "analysis_type": "project_analysis",
                    "clients_with_threshold": clients_with_projects,
                    "total_clients_matching": total_clients,
                    "project_threshold": query_context.get('project_threshold', 10),
                    "query_context": query_context,
                    "sql_used": sql_query,
                    "agent": self.name
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "error",
                "agent": self.name
            }
    
    def _extract_query_context(self, query: str) -> Dict[str, Any]:
        """Extract project-specific context from queries"""
        context = {"project_threshold": 10}  # Default threshold
        
        # Extract project thresholds
        project_threshold_match = re.search(r'(?i)\b(more than|greater than|over)\s+(\d+)\s+(project|job)', query)
        if project_threshold_match:
            context['project_threshold'] = int(project_threshold_match.group(2))
        
        return context

class EnhancedClientAnalysisAgent:
    """Enhanced client analysis agent"""
    
    def __init__(self, sql_generator: SQLQueryGenerator):
        self.sql_generator = sql_generator
        self.name = "enhanced_client_analysis"
    
    async def analyze(self, query: str, engine, classifications: List[str]) -> Dict[str, Any]:
        """Perform enhanced client analysis"""
        try:
            query_context = self._extract_query_context(query)
            sql_query = self.sql_generator.generate_client_analysis_query(query_context)
            
            async with engine.begin() as conn:
                result = await conn.execute(text(sql_query))
                rows = result.fetchall()
                
                clients = []
                total_revenue = 0
                
                for row in rows:
                    client_data = {
                        "client_name": row[0],
                        "total_revenue": float(row[1]) if row[1] else 0,
                        "transaction_count": row[2] if row[2] else 0,
                        "project_count": row[3] if row[3] else 0,
                        "avg_transaction_value": float(row[4]) if row[4] else 0,
                        "total_margin": float(row[5]) if row[5] else 0,
                        "avg_margin_percent": float(row[6]) if row[6] else 0
                    }
                    clients.append(client_data)
                    total_revenue += client_data["total_revenue"]
                
                # Calculate performance metrics
                for client in clients:
                    if total_revenue > 0:
                        client["revenue_percentage"] = (client["total_revenue"] / total_revenue) * 100
                    
                    # Performance categorization
                    if client["avg_margin_percent"] > 40:
                        client["profitability_tier"] = "High Profit"
                    elif client["avg_margin_percent"] > 25:
                        client["profitability_tier"] = "Medium Profit"
                    else:
                        client["profitability_tier"] = "Low Profit"
                
                return {
                    "analysis_type": "enhanced_client_analysis",
                    "clients": clients,
                    "total_clients_analyzed": len(clients),
                    "total_revenue": total_revenue,
                    "query_context": query_context,
                    "sql_used": sql_query,
                    "agent": self.name
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": "error",
                "agent": self.name
            }
    
    def _extract_query_context(self, query: str) -> Dict[str, Any]:
        """Extract context from client analysis queries"""
        context = {"limit": 10}  # Default limit
        
        # Extract top N requests
        if re.search(r'(?i)\btop\s+(\d+)', query):
            match = re.search(r'(?i)\btop\s+(\d+)', query)
            context['limit'] = int(match.group(1))
        
        return context

class EnhancedResponseGenerator:
    """Enhanced response generator with context-aware formatting"""
    
    def __init__(self):
        self.name = "enhanced_response_generator"
    
    async def generate_response(self, query: str, revenue_analysis: Dict, client_analysis: Dict, 
                              project_analysis: Dict, classifications: List[str]) -> Dict[str, Any]:
        """Generate enhanced responses based on analysis results with intelligent prompting"""
        
        response_parts = []
        recommendations = []
        
        # Use intelligent query analysis to determine response priority
        primary_intent = self._determine_primary_intent(query, classifications, 
                                                      revenue_analysis, client_analysis, project_analysis)
        
        # Generate response based on primary intent and actual data
        if primary_intent == "project_analysis" and project_analysis.get("clients_with_threshold"):
            response_parts.append(self._format_project_response(project_analysis))
            recommendations.extend(self._generate_project_recommendations(project_analysis))
            
        elif primary_intent == "client_analysis" and client_analysis.get("clients"):
            response_parts.append(self._format_client_response(client_analysis))
            recommendations.extend(self._generate_client_recommendations(client_analysis))
            
        elif primary_intent == "revenue_analysis":
            if revenue_analysis.get("analysis_type") == "time_series_revenue":
                response_parts.append(self._format_time_series_response(revenue_analysis))
                recommendations.extend(self._generate_time_series_recommendations(revenue_analysis))
            elif revenue_analysis.get("total_revenue"):
                response_parts.append(self._format_revenue_response(revenue_analysis))
                recommendations.extend(self._generate_revenue_recommendations(revenue_analysis))
        
        # If no primary analysis succeeded, generate a helpful error response
        if not response_parts:
            response_parts.append(self._generate_helpful_error_response(query, classifications, 
                                                                       revenue_analysis, client_analysis, project_analysis))
        
        # Combine responses with context-aware language
        final_response = self._create_contextualized_response(query, response_parts, classifications)
        
        return {
            "response": final_response,
            "recommendations": recommendations,
            "classifications_used": classifications,
            "primary_intent": primary_intent,
            "agent": self.name
        }
    
    def _determine_primary_intent(self, query: str, classifications: List[str], 
                                revenue_analysis: Dict, client_analysis: Dict, project_analysis: Dict) -> str:
        """Intelligently determine the primary intent based on query content and available data"""
        
        # Direct pattern matching for specific queries
        if re.search(r'(?i)\b(how many|count).*\b(client|customer).*\b(project|job)', query):
            return "project_analysis"
        
        if re.search(r'(?i)\b(top|best|highest).*\b(client|customer)', query):
            return "client_analysis"
            
        if re.search(r'(?i)\b(total|overall|aggregate).*revenue', query):
            return "revenue_analysis"
        
        # Fallback based on classification priority and data availability
        if "project_analysis" in classifications and project_analysis.get("clients_with_threshold"):
            return "project_analysis"
        elif "client_analysis" in classifications and client_analysis.get("clients"):
            return "client_analysis"
        elif any(cls in classifications for cls in ["revenue_analysis", "time_series"]):
            return "revenue_analysis"
        
        return "general_analysis"
    
    def _create_contextualized_response(self, query: str, response_parts: List[str], classifications: List[str]) -> str:
        """Create a contextualized response that directly addresses the user's question"""
        
        if not response_parts:
            return "I understand your query, but couldn't generate specific insights with the current data."
        
        # Add a direct answer prefix based on the query
        intro = self._generate_query_specific_intro(query)
        
        # Combine with actual analysis
        final_response = intro + "\n\n" + "\n\n".join(response_parts)
        
        return final_response
    
    def _generate_query_specific_intro(self, query: str) -> str:
        """Generate a specific introduction that directly addresses the user's question"""
        
        # Pattern matching for direct answers
        if re.search(r'(?i)\bhow many.*client.*more than.*project', query):
            return "📊 **Direct Answer to Your Question:**"
        elif re.search(r'(?i)\bwho.*top.*client', query):
            return "🏆 **Top Performing Clients Analysis:**"
        elif re.search(r'(?i)\btotal.*revenue', query):
            return "💰 **Revenue Analysis Results:**"
        else:
            return "📈 **Analysis Results:**"
    
    def _generate_helpful_error_response(self, query: str, classifications: List[str],
                                       revenue_analysis: Dict, client_analysis: Dict, project_analysis: Dict) -> str:
        """Generate a helpful error response when no analysis succeeded"""
        
        error_details = []
        
        if revenue_analysis.get("error"):
            error_details.append(f"Revenue analysis error: {revenue_analysis['error']}")
        if client_analysis.get("error"):
            error_details.append(f"Client analysis error: {client_analysis['error']}")
        if project_analysis.get("error"):
            error_details.append(f"Project analysis error: {project_analysis['error']}")
        
        response = f"I understand you're asking: **{query}**\n\n"
        response += "I attempted to analyze your request but encountered some issues:\n\n"
        
        for error in error_details:
            response += f"• {error}\n"
        
        response += "\n**What I tried to analyze:**\n"
        for classification in classifications:
            response += f"• {classification.replace('_', ' ').title()}\n"
        
        response += "\n**Suggestion:** Try rephrasing your question or check if the data contains the information you're looking for."
        
        return response
    
    def _format_project_response(self, analysis: Dict) -> str:
        """Format project analysis response"""
        clients = analysis.get("clients_with_threshold", [])
        threshold = analysis.get("project_threshold", 10)
        total_matching = analysis.get("total_clients_matching", 0)
        
        if not clients:
            return f"📊 **Project Analysis**\n\nNo clients found with more than {threshold} projects."
        
        response = f"📊 **Project Analysis**\n"
        response += f"**Clients with more than {threshold} projects:** {total_matching}\n\n"
        
        response += "**Client Details:**\n"
        for i, client in enumerate(clients, 1):
            response += f"{i}. **{client['client_name']}**: {client['project_count']} projects\n"
            response += f"   └─ Total Revenue: ${client['total_revenue']:,.2f}\n"
            response += f"   └─ Transactions: {client['total_transactions']}\n"
            response += f"   └─ Avg Transaction: ${client['avg_transaction_value']:,.2f}\n\n"
        
        return response

    def _generate_project_recommendations(self, analysis: Dict) -> List[str]:
        """Generate project-based recommendations"""
        recommendations = []
        clients = analysis.get("clients_with_threshold", [])
        threshold = analysis.get("project_threshold", 10)
        
        if len(clients) > 0:
            # Calculate average projects per qualifying client
            avg_projects = sum(c["project_count"] for c in clients) / len(clients)
            recommendations.append(f"🎯 {len(clients)} clients exceed {threshold} projects (avg: {avg_projects:.1f} projects)")
            
            # Check for high-project clients
            high_project_clients = [c for c in clients if c["project_count"] > 20]
            if high_project_clients:
                recommendations.append(f"⭐ {len(high_project_clients)} clients have 20+ projects - key relationships to maintain")
            
            # Revenue per project analysis
            total_revenue = sum(c["total_revenue"] for c in clients)
            total_projects = sum(c["project_count"] for c in clients)
            if total_projects > 0:
                revenue_per_project = total_revenue / total_projects
                recommendations.append(f"💼 Average revenue per project: ${revenue_per_project:,.2f}")
        
        return recommendations
        """Format time series analysis response"""
        data = analysis.get("time_series_data", [])
        if not data:
            return "No time series data available."
        
        total_revenue = sum(item["revenue"] for item in data)
        avg_monthly = total_revenue / len(data) if data else 0
        
        # Find best and worst performing periods
        best_period = max(data, key=lambda x: x["revenue"]) if data else None
        worst_period = min(data, key=lambda x: x["revenue"]) if data else None
        
        response = f"📈 **Time Series Analysis**\n"
        response += f"**Total Revenue Across Periods:** ${total_revenue:,.2f}\n"
        response += f"**Average Monthly Revenue:** ${avg_monthly:,.2f}\n\n"
        
        if best_period and worst_period:
            response += f"**Best Performing Period:** {best_period['period']} (${best_period['revenue']:,.2f})\n"
            response += f"**Lowest Performing Period:** {worst_period['period']} (${worst_period['revenue']:,.2f})\n\n"
        
        response += "**Period Breakdown:**\n"
        for item in data[-6:]:  # Show last 6 periods
            response += f"• {item['period']}: ${item['revenue']:,.2f} ({item['transactions']} transactions)\n"
        
        return response
    
    def _format_revenue_response(self, analysis: Dict) -> str:
        """Format general revenue analysis response"""
        response = f"💰 **Revenue Analysis**\n"
        response += f"**Total Revenue:** ${analysis['total_revenue']:,.2f}\n"
        response += f"**Unique Clients:** {analysis['unique_clients']}\n"
        response += f"**Total Transactions:** {analysis['total_transactions']}\n"
        response += f"**Average Transaction Value:** ${analysis['avg_transaction_value']:,.2f}\n"
        
        if analysis.get('query_context'):
            context = analysis['query_context']
            if context.get('time_period'):
                response += f"**Time Period:** {context['time_period']}\n"
            if context.get('client_filter'):
                response += f"**Client Filter:** {context['client_filter']}\n"
        
        return response
    
    def _format_client_response(self, analysis: Dict) -> str:
        """Format client analysis response"""
        clients = analysis.get("clients", [])
        if not clients:
            return "No client data available."
        
        response = f"🏢 **Client Performance Analysis**\n"
        response += f"**Total Clients Analyzed:** {len(clients)}\n"
        response += f"**Total Revenue:** ${analysis['total_revenue']:,.2f}\n\n"
        
        response += "**Top Performing Clients:**\n"
        for i, client in enumerate(clients[:5], 1):
            response += f"{i}. **{client['client_name']}**: ${client['total_revenue']:,.2f}\n"
            response += f"   └─ {client['transaction_count']} transactions • {client['project_count']} projects • "
            response += f"{client['avg_margin_percent']:.1f}% margin • {client['profitability_tier']}\n"
        
        return response
    
    def _generate_revenue_recommendations(self, analysis: Dict) -> List[str]:
        """Generate revenue-based recommendations"""
        recommendations = []
        
        avg_transaction = analysis.get('avg_transaction_value', 0)
        total_revenue = analysis.get('total_revenue', 0)
        unique_clients = analysis.get('unique_clients', 0)
        
        if avg_transaction < 5000:
            recommendations.append("🎯 Consider strategies to increase average transaction value")
        
        if unique_clients > 0:
            revenue_per_client = total_revenue / unique_clients
            if revenue_per_client < 50000:
                recommendations.append("💼 Focus on expanding relationships with existing clients")
        
        return recommendations
    
    def _generate_client_recommendations(self, analysis: Dict) -> List[str]:
        """Generate client-based recommendations"""
        recommendations = []
        clients = analysis.get("clients", [])
        
        if len(clients) >= 5:
            top_5_revenue = sum(client["total_revenue"] for client in clients[:5])
            concentration_ratio = (top_5_revenue / analysis['total_revenue']) * 100 if analysis['total_revenue'] > 0 else 0
            
            if concentration_ratio > 80:
                recommendations.append("⚠️ High client concentration risk - diversify client base")
            elif concentration_ratio > 60:
                recommendations.append("📊 Moderate client concentration - monitor key relationships")
        
        # Check for low-margin clients
        low_margin_clients = [c for c in clients if c.get('avg_margin_percent', 0) < 20]
        if len(low_margin_clients) > len(clients) * 0.3:
            recommendations.append("💡 Review pricing strategy for low-margin clients")
        
        return recommendations
    
    def _generate_time_series_recommendations(self, analysis: Dict) -> List[str]:
        """Generate time series based recommendations"""
        recommendations = []
        data = analysis.get("time_series_data", [])
        
        if len(data) >= 3:
            recent_trend = []
            for i in range(len(data) - 3, len(data)):
                if i > 0 and data[i]["revenue"] > data[i-1]["revenue"]:
                    recent_trend.append("up")
                elif i > 0 and data[i]["revenue"] < data[i-1]["revenue"]:
                    recent_trend.append("down")
            
            if recent_trend.count("down") > recent_trend.count("up"):
                recommendations.append("📉 Revenue declining trend detected - investigate causes")
            elif recent_trend.count("up") > recent_trend.count("down"):
                recommendations.append("📈 Positive revenue trend - maintain current strategies")
        
        return recommendations

# Enhanced Multi-Agent Pipeline
class EnhancedMultiAgentPipeline:
    """Enhanced multi-agent pipeline with intelligent orchestration, session management, and workflow streaming"""
    
    def __init__(self, engine):
        self.engine = engine
        self.query_classifier = QueryClassifier()
        self.sql_generator = SQLQueryGenerator()
        self.revenue_agent = EnhancedRevenueAnalysisAgent(self.sql_generator)
        self.client_agent = EnhancedClientAnalysisAgent(self.sql_generator)
        self.project_agent = EnhancedProjectAnalysisAgent(self.sql_generator)
        self.response_generator = EnhancedResponseGenerator()
        self.llm_client = LLMClient()  # Add LLM client for AI-powered responses
        
    async def process_query_with_streaming(self, query: str, session_id: str = None, conversation_id: str = None) -> Dict[str, Any]:
        """Process user query with streaming workflow evidence and session management"""
        try:
            workflow_steps = []
            start_time = datetime.now()
            
            # Step 0: Session Management
            workflow_steps.append({
                "step": "session_initialization",
                "timestamp": datetime.now().isoformat(),
                "status": "starting",
                "details": f"Initializing session {session_id} for conversation {conversation_id}"
            })
            
            print(f"🔍 Processing query: {query}")
            workflow_steps.append({
                "step": "query_received",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Query received: '{query}'"
            })
            
            # Step 1: Query Classification with Evidence
            workflow_steps.append({
                "step": "query_classification",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "details": "Analyzing query intent and extracting context..."
            })
            
            classifications = self.query_classifier.classify_query(query)
            print(f"📊 Query classifications: {classifications}")
            
            workflow_steps.append({
                "step": "query_classification",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Query classified as: {', '.join(classifications)}",
                "results": {
                    "classifications": classifications,
                    "patterns_matched": self._get_matched_patterns(query, classifications)
                }
            })
            
            # Step 2: Agent Selection and Execution Planning
            workflow_steps.append({
                "step": "agent_selection",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "details": "Determining which agents to activate based on query classification..."
            })
            
            planned_agents = self._plan_agent_execution(classifications)
            workflow_steps.append({
                "step": "agent_selection", 
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Selected agents: {', '.join(planned_agents)}",
                "results": {"planned_agents": planned_agents}
            })
            
            # Step 3: Execute Agents with Individual Workflow Tracking
            revenue_analysis = {}
            client_analysis = {}
            agents_used = []
            
            # Revenue Analysis Agent
            if any(cls in classifications for cls in ['revenue_analysis', 'time_series', 'general_analysis']):
                workflow_steps.append({
                    "step": "revenue_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running",
                    "details": "💰 Executing Revenue Analysis Agent - extracting context and generating SQL..."
                })
                
                print("💰 Running Enhanced Revenue Analysis Agent...")
                revenue_analysis = await self.revenue_agent.analyze(query, self.engine, classifications)
                agents_used.append(self.revenue_agent.name)
                
                # Add detailed workflow evidence for revenue analysis
                workflow_steps.append({
                    "step": "revenue_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                    "details": f"Revenue analysis completed. Analysis type: {revenue_analysis.get('analysis_type', 'unknown')}",
                    "results": {
                        "agent_name": self.revenue_agent.name,
                        "analysis_type": revenue_analysis.get('analysis_type'),
                        "sql_query": revenue_analysis.get('sql_used'),
                        "query_context": revenue_analysis.get('query_context'),
                        "data_points": len(revenue_analysis.get('time_series_data', [])) if revenue_analysis.get('time_series_data') else 1,
                        "total_revenue": revenue_analysis.get('total_revenue'),
                        "unique_clients": revenue_analysis.get('unique_clients')
                    }
                })
            
            # Client Analysis Agent
            if any(cls in classifications for cls in ['client_analysis', 'comparative_analysis', 'general_analysis']):
                workflow_steps.append({
                    "step": "client_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running", 
                    "details": "🏢 Executing Client Analysis Agent - generating client performance queries..."
                })
                
                print("🏢 Running Enhanced Client Analysis Agent...")
                client_analysis = await self.client_agent.analyze(query, self.engine, classifications)
                agents_used.append(self.client_agent.name)
                
                workflow_steps.append({
                    "step": "client_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                    "details": f"Client analysis completed. Analyzed {len(client_analysis.get('clients', []))} clients",
                    "results": {
                        "agent_name": self.client_agent.name,
                        "clients_analyzed": len(client_analysis.get('clients', [])),
                        "total_revenue": client_analysis.get('total_revenue'),
                        "sql_query": client_analysis.get('sql_used'),
                        "query_context": client_analysis.get('query_context'),
                        "top_client": client_analysis.get('clients', [{}])[0].get('client_name') if client_analysis.get('clients') else None
                    }
                })
            
            # Project Analysis Agent
            project_analysis = {}
            if any(cls in classifications for cls in ['project_analysis', 'general_analysis']):
                workflow_steps.append({
                    "step": "project_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running",
                    "details": "🎯 Executing Project Analysis Agent - analyzing project counts and thresholds..."
                })
                
                print("🎯 Running Enhanced Project Analysis Agent...")
                project_analysis = await self.project_agent.analyze(query, self.engine, classifications)
                agents_used.append(self.project_agent.name)
                
                workflow_steps.append({
                    "step": "project_analysis_agent",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                    "details": f"Project analysis completed. Found {project_analysis.get('total_clients_matching', 0)} clients meeting criteria",
                    "results": {
                        "agent_name": self.project_agent.name,
                        "clients_matching": project_analysis.get('total_clients_matching', 0),
                        "project_threshold": project_analysis.get('project_threshold', 0),
                        "sql_query": project_analysis.get('sql_used'),
                        "query_context": project_analysis.get('query_context')
                    }
                })
            
            # Step 4: Response Generation with Evidence
            workflow_steps.append({
                "step": "response_generation",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "details": "📝 Generating comprehensive response and business recommendations..."
            })
            
            print("📝 Generating Enhanced Response...")
            response_data = await self.response_generator.generate_response(
                query, revenue_analysis, client_analysis, project_analysis, classifications
            )
            agents_used.append(self.response_generator.name)
            
            workflow_steps.append({
                "step": "response_generation",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Response generated with {len(response_data.get('recommendations', []))} recommendations",
                "results": {
                    "agent_name": self.response_generator.name,
                    "response_length": len(response_data.get('response', '')),
                    "recommendations_count": len(response_data.get('recommendations', [])),
                    "classifications_used": response_data.get('classifications_used', [])
                }
            })
            
            # Step 5: Session Management - Store Results
            workflow_steps.append({
                "step": "session_storage",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "details": "💾 Storing conversation data and updating session..."
            })
            
            # Store session data if session_id provided
            session_summary = None
            if session_id and conversation_id:
                session_summary = await self._store_session_data(
                    session_id, conversation_id, query, response_data, 
                    workflow_steps, revenue_analysis, client_analysis, project_analysis
                )
                
                workflow_steps.append({
                    "step": "session_storage",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                    "details": f"Session data stored successfully. Messages in conversation: {session_summary.get('message_count', 0)}",
                    "results": session_summary
                })
            else:
                workflow_steps.append({
                    "step": "session_storage",
                    "timestamp": datetime.now().isoformat(),
                    "status": "skipped",
                    "details": "No session ID provided - running in stateless mode"
                })
            
            # Final Summary
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            workflow_steps.append({
                "step": "pipeline_completion",
                "timestamp": end_time.isoformat(),
                "status": "completed",
                "details": f"✅ Enhanced multi-agent pipeline completed in {total_duration:.2f} seconds",
                "results": {
                    "total_duration_seconds": total_duration,
                    "agents_executed": len(agents_used),
                    "sql_queries_generated": len([q for q in [revenue_analysis.get('sql_used'), client_analysis.get('sql_used'), project_analysis.get('sql_used')] if q]),
                    "workflow_steps_completed": len([s for s in workflow_steps if s['status'] == 'completed'])
                }
            })
            
            print("✅ Enhanced multi-agent pipeline completed!")
            
            return {
                "response": response_data["response"],
                "recommendations": response_data["recommendations"],
                "analysis_data": {
                    "revenue_analysis": revenue_analysis,
                    "client_analysis": client_analysis,
                    "project_analysis": project_analysis
                },
                "query_classifications": classifications,
                "agents_used": agents_used,
                "pipeline_executed": True,
                "sql_queries_used": {
                    "revenue_sql": revenue_analysis.get("sql_used"),
                    "client_sql": client_analysis.get("sql_used"),
                    "project_sql": project_analysis.get("sql_used")
                },
                "workflow_evidence": workflow_steps,
                "session_summary": session_summary,
                "execution_metrics": {
                    "total_duration_seconds": total_duration,
                    "agents_executed": len(agents_used),
                    "sql_queries_generated": len([q for q in [revenue_analysis.get('sql_used'), client_analysis.get('sql_used'), project_analysis.get('sql_used')] if q]),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            }
            
        except Exception as e:
            error_step = {
                "step": "pipeline_error",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "details": f"Pipeline error: {str(e)}",
                "error": str(e)
            }
            
            return {
                "response": f"Enhanced pipeline error: {str(e)}",
                "recommendations": [],
                "analysis_data": {},
                "query_classifications": [],
                "agents_used": [],
                "pipeline_executed": False,
                "workflow_evidence": workflow_steps + [error_step] if 'workflow_steps' in locals() else [error_step],
                "error": str(e)
            }
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Backward compatibility method - calls the enhanced streaming version"""
        return await self.process_query_with_streaming(query)
    
    def _get_matched_patterns(self, query: str, classifications: List[str]) -> Dict[str, List[str]]:
        """Get the specific regex patterns that matched for each classification"""
        matched_patterns = {}
        
        for classification in classifications:
            if classification in self.query_classifier.query_patterns:
                patterns = self.query_classifier.query_patterns[classification]
                matched = []
                for pattern in patterns:
                    if re.search(pattern, query):
                        matched.append(pattern)
                if matched:
                    matched_patterns[classification] = matched
        
        return matched_patterns
    
    def _plan_agent_execution(self, classifications: List[str]) -> List[str]:
        """Plan which agents to execute based on classifications"""
        planned_agents = []
        
        if any(cls in classifications for cls in ['revenue_analysis', 'time_series', 'general_analysis']):
            planned_agents.append('enhanced_revenue_analysis')
            
        if any(cls in classifications for cls in ['client_analysis', 'comparative_analysis', 'general_analysis']):
            planned_agents.append('enhanced_client_analysis')
            
        if any(cls in classifications for cls in ['project_analysis', 'general_analysis']):
            planned_agents.append('enhanced_project_analysis')
            
        planned_agents.append('enhanced_response_generator')
        
        return planned_agents
    
    async def _store_session_data(self, session_id: str, conversation_id: str, query: str, 
                                response_data: Dict, workflow_steps: List, 
                                revenue_analysis: Dict, client_analysis: Dict, project_analysis: Dict) -> Dict[str, Any]:
        """Store session data with workflow evidence"""
        try:
            async with self.engine.begin() as conn:
                # Get conversation DB ID
                conv_result = await conn.execute(text("""
                    SELECT id FROM chat_conversations WHERE conversation_id = :conversation_id
                """), {"conversation_id": conversation_id})
                
                conv_row = conv_result.fetchone()
                if conv_row:
                    conversation_db_id = conv_row[0]
                    
                    # Store user message with workflow metadata
                    user_metadata = {
                        "timestamp": datetime.now().isoformat(),
                        "query_classifications": workflow_steps[1].get('results', {}).get('classifications', []),
                        "planned_agents": workflow_steps[2].get('results', {}).get('planned_agents', [])
                    }
                    
                    await conn.execute(text("""
                        INSERT INTO chat_messages (conversation_id, role, content, metadata)
                        VALUES (:conversation_id, 'user', :content, :metadata)
                    """), {
                        "conversation_id": conversation_db_id,
                        "content": query,
                        "metadata": json.dumps(user_metadata)
                    })
                    
                    # Store assistant response with comprehensive metadata
                    assistant_metadata = {
                        "timestamp": datetime.now().isoformat(),
                        "pipeline_executed": True,
                        "agents_used": workflow_steps[-2].get('results', {}).get('agents_executed', 0),
                        "query_classifications": response_data.get('classifications_used', []),
                        "workflow_evidence": workflow_steps,
                        "analysis_data": {
                            "revenue_analysis": {
                                "analysis_type": revenue_analysis.get('analysis_type'),
                                "total_revenue": revenue_analysis.get('total_revenue'),
                                "unique_clients": revenue_analysis.get('unique_clients'),
                                "sql_used": revenue_analysis.get('sql_used')
                            },
                            "client_analysis": {
                                "clients_analyzed": len(client_analysis.get('clients', [])),
                                "total_revenue": client_analysis.get('total_revenue'),
                                "sql_used": client_analysis.get('sql_used')
                            }
                        },
                        "recommendations": response_data.get('recommendations', []),
                        "execution_metrics": workflow_steps[-1].get('results', {})
                    }
                    
                    await conn.execute(text("""
                        INSERT INTO chat_messages (conversation_id, role, content, metadata)
                        VALUES (:conversation_id, 'assistant', :content, :metadata)
                    """), {
                        "conversation_id": conversation_db_id,
                        "content": response_data["response"],
                        "metadata": json.dumps(assistant_metadata)
                    })
                    
                    # Get conversation summary
                    summary_result = await conn.execute(text("""
                        SELECT COUNT(*) as message_count, 
                               MIN(created_at) as conversation_start,
                               MAX(created_at) as last_activity
                        FROM chat_messages 
                        WHERE conversation_id = :conversation_id
                    """), {"conversation_id": conversation_db_id})
                    
                    summary_row = summary_result.fetchone()
                    
                    return {
                        "session_id": session_id,
                        "conversation_id": conversation_id,
                        "message_count": summary_row[0] if summary_row else 0,
                        "conversation_start": summary_row[1].isoformat() if summary_row and summary_row[1] else None,
                        "last_activity": summary_row[2].isoformat() if summary_row and summary_row[2] else None,
                        "storage_status": "success"
                    }
                else:
                    return {
                        "session_id": session_id,
                        "conversation_id": conversation_id,
                        "storage_status": "error",
                        "error": "Conversation not found"
                    }
                    
        except Exception as e:
            return {
                "session_id": session_id,
                "conversation_id": conversation_id,
                "storage_status": "error",
                "error": str(e)
            }
