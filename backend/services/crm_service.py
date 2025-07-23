"""
Configurable CRM Integration for NextGen Revenue Insights Assistant
Supports both real Dynamics 365 CRM and mock data based on configuration
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from msal import ConfidentialClientApplication

# Import centralized configuration and schemas
from config import get_config, is_using_real_crm
from schemas import OpportunityData, CRMDataResponse
from mock_crm_data import (
    get_mock_opportunities, get_mock_accounts, get_mock_contacts, 
    get_mock_activities, get_mock_pipeline_summary, get_mock_sales_forecast
)

# Get configuration instance
config = get_config()

# Configure logging
logging.basicConfig(level=getattr(logging, config.application.log_level))
logger = logging.getLogger(__name__)


class DynamicsCRMClient:
    """
    Asynchronous client for Microsoft Dynamics 365 CRM integration.
    Implements secure authentication and data retrieval.
    """
    
    def __init__(self):
        # Get CRM configuration from centralized config
        self.use_real_crm = config.dynamics.use_real_crm
        self.client_id = config.dynamics.client_id
        self.client_secret = config.dynamics.client_secret
        self.tenant_id = config.dynamics.tenant_id
        self.resource_url = config.dynamics.resource_url
        self.api_version = config.dynamics.api_version
        self.timeout = config.dynamics.timeout
        
        # Initialize based on configuration
        if self.use_real_crm:
            # MSAL app for authentication
            self.app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )
            
            self._access_token = None
            self._token_expires_at = None
            logger.info("Initialized real Dynamics 365 CRM client")
        else:
            logger.info("Initialized mock CRM client - using sample data")
    
    async def _get_access_token(self) -> str:
        """Get valid access token for Dynamics 365 API."""
        
        # Check if current token is still valid
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at - timedelta(minutes=5)):
            return self._access_token
        
        try:
            # Request new token
            scopes = [f"{self.resource_url}/.default"]
            result = self.app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                # Token typically expires in 1 hour
                self._token_expires_at = datetime.now() + timedelta(seconds=result.get("expires_in", 3600))
                
                logger.info("Successfully acquired Dynamics 365 access token")
                return self._access_token
            else:
                error_msg = result.get("error_description", "Unknown authentication error")
                logger.error(f"Failed to acquire token: {error_msg}")
                raise Exception(f"Authentication failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Token acquisition failed: {e}")
            raise
    
    async def _make_api_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Dynamics 365."""
        
        token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        url = f"{self.resource_url}api/data/v9.2/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully retrieved data from {endpoint}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        raise Exception(f"API request failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"API request to {endpoint} failed: {e}")
            raise
    
    async def get_opportunities(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve opportunity data from Dynamics 365 or mock data.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of opportunity records
        """
        
        # Use mock data if configured
        if not self.use_real_crm:
            logger.info("Using mock CRM data for opportunities")
            stage_filter = filters.get("stage") if filters else None
            limit = filters.get("limit", 100) if filters else 100
            return get_mock_opportunities(limit=limit, stage=stage_filter)
        
        try:
            # Build OData query for real CRM
            select_fields = [
                "opportunityid",
                "name", 
                "estimatedvalue",
                "closeprobability",
                "estimatedclosedate",
                "salesstage",
                "statecode",
                "statuscode",
                "createdon",
                "modifiedon"
            ]
            
            params = {
                "$select": ",".join(select_fields),
                "$top": 1000  # Limit results
            }
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                
                if "statecode" in filters:
                    filter_conditions.append(f"statecode eq {filters['statecode']}")
                
                if "estimatedclosedate" in filters:
                    filter_conditions.append(f"estimatedclosedate {filters['estimatedclosedate']}")
                
                if "closeprobability" in filters:
                    filter_conditions.append(f"closeprobability ge {filters['closeprobability']}")
                
                if filter_conditions:
                    params["$filter"] = " and ".join(filter_conditions)
            
            # Make API request
            response = await self._make_api_request("opportunities", params)
            
            opportunities = response.get("value", [])
            logger.info(f"Retrieved {len(opportunities)} opportunities from real CRM")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to retrieve opportunities from real CRM: {e}")
            # Fallback to mock data
            logger.warning("Falling back to mock CRM data")
            return get_mock_opportunities()
    
    async def get_accounts(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve account data from Dynamics 365 or mock data.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of account records
        """
        
        # Use mock data if configured
        if not self.use_real_crm:
            logger.info("Using mock CRM data for accounts")
            limit = filters.get("limit", 100) if filters else 100
            return get_mock_accounts(limit=limit)
        
        try:
            select_fields = [
                "accountid",
                "name",
                "revenue",
                "industrycode",
                "statecode",
                "createdon",
                "modifiedon"
            ]
            
            params = {
                "$select": ",".join(select_fields),
                "$top": 500
            }
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                
                if "statecode" in filters:
                    filter_conditions.append(f"statecode eq {filters['statecode']}")
                
                if filter_conditions:
                    params["$filter"] = " and ".join(filter_conditions)
            
            response = await self._make_api_request("accounts", params)
            
            accounts = response.get("value", [])
            logger.info(f"Retrieved {len(accounts)} accounts from real CRM")
            
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to retrieve accounts from real CRM: {e}")
            # Fallback to mock data
            logger.warning("Falling back to mock CRM data for accounts")
            return get_mock_accounts()
    
    async def get_opportunity_products(self, opportunity_id: str) -> List[Dict[str, Any]]:
        """Get products/services associated with an opportunity."""
        
        # Use mock data if configured
        if not self.use_real_crm:
            logger.info("Using mock CRM data for opportunity products")
            return []  # Mock data doesn't include detailed product info
        
        try:
            params = {
                "$filter": f"opportunityid eq {opportunity_id}",
                "$select": "opportunityproductid,productid,quantity,priceperunit,extendedamount"
            }
            
            response = await self._make_api_request("opportunityproducts", params)
            return response.get("value", [])
            
        except Exception as e:
            logger.error(f"Failed to retrieve opportunity products: {e}")
            return []
    
    async def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive pipeline summary statistics."""
        
        # Use mock data if configured
        if not self.use_real_crm:
            logger.info("Using mock CRM data for pipeline summary")
            return get_mock_pipeline_summary()
        
        try:
            # Get opportunities for pipeline analysis
            opportunities = await self.get_opportunities({"statecode": 0})
            
            # Calculate pipeline metrics
            total_opportunities = len(opportunities)
            total_value = sum(opp.get("estimatedvalue", 0) or 0 for opp in opportunities)
            weighted_value = sum(
                (opp.get("estimatedvalue", 0) or 0) * (opp.get("closeprobability", 0) or 0) / 100
                for opp in opportunities
            )
            
            # Group by stage
            stage_summary = {}
            for opp in opportunities:
                stage = opp.get("salesstage", "Unknown")
                if stage not in stage_summary:
                    stage_summary[stage] = {"count": 0, "total_value": 0}
                
                stage_summary[stage]["count"] += 1
                stage_summary[stage]["total_value"] += opp.get("estimatedvalue", 0) or 0
            
            return {
                "total_opportunities": total_opportunities,
                "total_pipeline_value": total_value,
                "weighted_pipeline_value": weighted_value,
                "stages": stage_summary,
                "avg_deal_size": total_value / total_opportunities if total_opportunities > 0 else 0,
                "generated_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate pipeline summary: {e}")
            return get_mock_pipeline_summary()
    
    async def get_sales_forecast(self, months: int = 12) -> Dict[str, Any]:
        """Generate sales forecast based on pipeline data."""
        
        # Use mock data if configured
        if not self.use_real_crm:
            logger.info("Using mock CRM data for sales forecast")
            return get_mock_sales_forecast(months)
        
        try:
            # Get opportunities with close dates
            opportunities = await self.get_opportunities({
                "statecode": 0,
                "estimatedclosedate": f"ge {datetime.now().isoformat()}"
            })
            
            # Generate forecast based on close dates and probabilities
            forecast_data = []
            current_date = datetime.now()
            
            for month in range(months):
                month_start = current_date + timedelta(days=30 * month)
                month_end = month_start + timedelta(days=30)
                
                month_opportunities = [
                    opp for opp in opportunities
                    if opp.get("estimatedclosedate") and 
                    month_start <= datetime.fromisoformat(opp["estimatedclosedate"].replace("Z", "+00:00")) <= month_end
                ]
                
                forecasted_revenue = sum(
                    (opp.get("estimatedvalue", 0) or 0) * (opp.get("closeprobability", 0) or 0) / 100
                    for opp in month_opportunities
                )
                
                potential_revenue = sum(opp.get("estimatedvalue", 0) or 0 for opp in month_opportunities)
                
                forecast_data.append({
                    "month": month_start.strftime("%Y-%m"),
                    "forecasted_revenue": forecasted_revenue,
                    "potential_revenue": potential_revenue,
                    "opportunity_count": len(month_opportunities)
                })
            
            return {
                "forecast_period_months": months,
                "forecast_data": forecast_data,
                "total_forecasted_revenue": sum(item["forecasted_revenue"] for item in forecast_data),
                "generated_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate sales forecast: {e}")
            return get_mock_sales_forecast(months)
            logger.error(f"Failed to retrieve opportunity products: {e}")
            return []
    
    async def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get high-level pipeline summary statistics."""
        
        try:
            # Get active opportunities
            active_opportunities = await self.get_opportunities({"statecode": 0})
            
            # Calculate summary statistics
            total_pipeline_value = sum(
                opp.get("estimatedvalue", 0) or 0 
                for opp in active_opportunities
            )
            
            weighted_pipeline = sum(
                (opp.get("estimatedvalue", 0) or 0) * ((opp.get("closeprobability", 0) or 0) / 100)
                for opp in active_opportunities
            )
            
            # Group by sales stage
            stage_summary = {}
            for opp in active_opportunities:
                stage = opp.get("salesstage", "Unknown")
                if stage not in stage_summary:
                    stage_summary[stage] = {"count": 0, "value": 0}
                
                stage_summary[stage]["count"] += 1
                stage_summary[stage]["value"] += opp.get("estimatedvalue", 0) or 0
            
            # Group by probability ranges
            probability_ranges = {
                "High (80-100%)": {"count": 0, "value": 0},
                "Medium (50-79%)": {"count": 0, "value": 0},
                "Low (0-49%)": {"count": 0, "value": 0}
            }
            
            for opp in active_opportunities:
                prob = opp.get("closeprobability", 0) or 0
                value = opp.get("estimatedvalue", 0) or 0
                
                if prob >= 80:
                    probability_ranges["High (80-100%)"]["count"] += 1
                    probability_ranges["High (80-100%)"]["value"] += value
                elif prob >= 50:
                    probability_ranges["Medium (50-79%)"]["count"] += 1
                    probability_ranges["Medium (50-79%)"]["value"] += value
                else:
                    probability_ranges["Low (0-49%)"]["count"] += 1
                    probability_ranges["Low (0-49%)"]["value"] += value
            
            summary = {
                "total_opportunities": len(active_opportunities),
                "total_pipeline_value": total_pipeline_value,
                "weighted_pipeline_value": weighted_pipeline,
                "stage_breakdown": stage_summary,
                "probability_breakdown": probability_ranges,
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info("Generated pipeline summary successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate pipeline summary: {e}")
            return self._get_mock_pipeline_summary()
    
    def _get_mock_opportunities(self) -> List[Dict[str, Any]]:
        """Generate mock opportunity data for development/testing."""
        
        mock_data = [
            {
                "opportunityid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "name": "Enterprise Software License - TechCorp",
                "estimatedvalue": 750000,
                "closeprobability": 85,
                "estimatedclosedate": "2025-09-15T00:00:00Z",
                "salesstage": "Proposal/Quote",
                "statecode": 0,
                "createdon": "2025-06-01T00:00:00Z"
            },
            {
                "opportunityid": "f47ac10b-58cc-4372-a567-0e02b2c3d480",
                "name": "Cloud Migration Services - InnovateCorp",
                "estimatedvalue": 450000,
                "closeprobability": 65,
                "estimatedclosedate": "2025-08-30T00:00:00Z",
                "salesstage": "Develop",
                "statecode": 0,
                "createdon": "2025-05-15T00:00:00Z"
            },
            {
                "opportunityid": "f47ac10b-58cc-4372-a567-0e02b2c3d481",
                "name": "AI Platform Implementation - DataTech",
                "estimatedvalue": 1200000,
                "closeprobability": 45,
                "estimatedclosedate": "2025-10-31T00:00:00Z",
                "salesstage": "Qualify",
                "statecode": 0,
                "createdon": "2025-07-01T00:00:00Z"
            },
            {
                "opportunityid": "f47ac10b-58cc-4372-a567-0e02b2c3d482",
                "name": "Security Audit Services - SecureBank",
                "estimatedvalue": 180000,
                "closeprobability": 90,
                "estimatedclosedate": "2025-08-15T00:00:00Z",
                "salesstage": "Close",
                "statecode": 0,
                "createdon": "2025-06-20T00:00:00Z"
            },
            {
                "opportunityid": "f47ac10b-58cc-4372-a567-0e02b2c3d483",
                "name": "Digital Transformation - RetailGiant",
                "estimatedvalue": 850000,
                "closeprobability": 70,
                "estimatedclosedate": "2025-11-30T00:00:00Z",
                "salesstage": "Develop",
                "statecode": 0,
                "createdon": "2025-04-10T00:00:00Z"
            }
        ]
        
        logger.info("Using mock opportunity data for development")
        return mock_data
    
    def _get_mock_accounts(self) -> List[Dict[str, Any]]:
        """Generate mock account data for development/testing."""
        
        mock_data = [
            {
                "accountid": "a47ac10b-58cc-4372-a567-0e02b2c3d479",
                "name": "TechCorp Solutions",
                "revenue": 50000000,
                "industrycode": "Technology",
                "statecode": 0
            },
            {
                "accountid": "a47ac10b-58cc-4372-a567-0e02b2c3d480",
                "name": "InnovateCorp",
                "revenue": 25000000,
                "industrycode": "Manufacturing",
                "statecode": 0
            },
            {
                "accountid": "a47ac10b-58cc-4372-a567-0e02b2c3d481",
                "name": "DataTech Analytics",
                "revenue": 75000000,
                "industrycode": "Financial Services",
                "statecode": 0
            }
        ]
        
        logger.info("Using mock account data for development")
        return mock_data
    
    def _get_mock_pipeline_summary(self) -> Dict[str, Any]:
        """Generate mock pipeline summary for development/testing."""
        
        return {
            "total_opportunities": 5,
            "total_pipeline_value": 3430000,
            "weighted_pipeline_value": 2315500,
            "stage_breakdown": {
                "Qualify": {"count": 1, "value": 1200000},
                "Develop": {"count": 2, "value": 1300000},
                "Proposal/Quote": {"count": 1, "value": 750000},
                "Close": {"count": 1, "value": 180000}
            },
            "probability_breakdown": {
                "High (80-100%)": {"count": 2, "value": 930000},
                "Medium (50-79%)": {"count": 2, "value": 1300000},
                "Low (0-49%)": {"count": 1, "value": 1200000}
            },
            "retrieved_at": datetime.now().isoformat()
        }


# Global CRM client instance
crm_client = None

async def get_crm_client() -> DynamicsCRMClient:
    """Get or create the global CRM client instance."""
    global crm_client
    if crm_client is None:
        crm_client = DynamicsCRMClient()
    return crm_client

async def get_pipeline_data() -> CRMDataResponse:
    """Convenience function to get complete pipeline data."""
    
    client = await get_crm_client()
    
    # Get opportunities and accounts in parallel
    opportunities_task = client.get_opportunities({"statecode": 0})
    accounts_task = client.get_accounts({"statecode": 0})
    
    opportunities, accounts = await asyncio.gather(opportunities_task, accounts_task)
    
    # Calculate total pipeline value
    total_pipeline_value = sum(
        opp.get("estimatedvalue", 0) or 0 
        for opp in opportunities
    )
    
    return CRMDataResponse(
        opportunities=[
            OpportunityData(
                opportunity_id=opp.get("opportunityid", ""),
                name=opp.get("name", ""),
                estimated_value=opp.get("estimatedvalue", 0) or 0,
                close_probability=opp.get("closeprobability", 0) or 0,
                estimated_close_date=opp.get("estimatedclosedate"),
                sales_stage=opp.get("salesstage", ""),
                account_name=opp.get("accountname", ""),
                owner=opp.get("ownerid", "")
            ) for opp in opportunities
        ],
        accounts=accounts,
        total_pipeline_value=total_pipeline_value,
        retrieved_at=datetime.now()
    )
