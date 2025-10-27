from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
import stripe
import os
from typing import Dict, Any
from services.supabase_client import get_supabase_client

router = APIRouter()

# Initialize Stripe from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events for subscription updates
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")
        
        # Handle different event types
        if event['type'] == 'customer.subscription.created':
            await handle_subscription_created(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            await handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            await handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            await handle_payment_failed(event['data']['object'])
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def handle_subscription_created(subscription: Dict[str, Any]):
    """Handle new subscription creation"""
    try:
        customer_id = subscription['customer']
        plan_id = subscription['items']['data'][0]['price']['id']
        
        # Map Stripe price IDs to our plan names via environment variables
        # Configure these in your .env (see .env.example)
        plan_mapping: Dict[str, str] = {}
        price_pro_monthly = os.getenv("STRIPE_PRICE_PRO_MONTHLY")
        price_business_monthly = os.getenv("STRIPE_PRICE_BUSINESS_MONTHLY")
        if price_pro_monthly:
            plan_mapping[price_pro_monthly] = "pro"
        if price_business_monthly:
            plan_mapping[price_business_monthly] = "business"
        
        plan_name = plan_mapping.get(plan_id, "free")
        
        # Update user plan in Supabase
        supabase = get_supabase_client()
        supabase.table("users").update({
            "plan": plan_name,
            "stripe_customer_id": customer_id,
            "subscription_id": subscription['id']
        }).eq("stripe_customer_id", customer_id).execute()
        
    except Exception as e:
        print(f"Error handling subscription created: {e}")

async def handle_subscription_updated(subscription: Dict[str, Any]):
    """Handle subscription updates"""
    try:
        customer_id = subscription['customer']
        status = subscription['status']
        
        # Update subscription status
        supabase = get_supabase_client()
        supabase.table("users").update({
            "subscription_status": status
        }).eq("stripe_customer_id", customer_id).execute()
        
    except Exception as e:
        print(f"Error handling subscription updated: {e}")

async def handle_subscription_deleted(subscription: Dict[str, Any]):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription['customer']
        
        # Downgrade user to free plan
        supabase = get_supabase_client()
        supabase.table("users").update({
            "plan": "free",
            "subscription_status": "cancelled"
        }).eq("stripe_customer_id", customer_id).execute()
        
    except Exception as e:
        print(f"Error handling subscription deleted: {e}")

async def handle_payment_succeeded(invoice: Dict[str, Any]):
    """Handle successful payment"""
    try:
        customer_id = invoice['customer']
        
        # Update payment status
        supabase = get_supabase_client()
        supabase.table("users").update({
            "last_payment_date": invoice['created'],
            "payment_status": "succeeded"
        }).eq("stripe_customer_id", customer_id).execute()
        
    except Exception as e:
        print(f"Error handling payment succeeded: {e}")

async def handle_payment_failed(invoice: Dict[str, Any]):
    """Handle failed payment"""
    try:
        customer_id = invoice['customer']
        
        # Update payment status
        supabase = get_supabase_client()
        supabase.table("users").update({
            "payment_status": "failed"
        }).eq("stripe_customer_id", customer_id).execute()
        
    except Exception as e:
        print(f"Error handling payment failed: {e}")

@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    customer_email: str,
    success_url: str,
    cancel_url: str
):
    """
    Create Stripe checkout session for subscription
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=customer_email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'customer_email': customer_email
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout session creation failed: {str(e)}")

@router.get("/prices")
async def get_prices():
    """
    Get available subscription prices
    """
    try:
        prices = stripe.Price.list(active=True, type='recurring')
        
        return {
            "prices": [
                {
                    "id": price.id,
                    "amount": price.unit_amount,
                    "currency": price.currency,
                    "interval": price.recurring.interval,
                    "product": price.product
                }
                for price in prices.data
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {str(e)}")

