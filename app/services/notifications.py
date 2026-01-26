"""Notification service for order events"""
import os
from datetime import datetime


def get_log_file():
    """Get the notification log file path."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, 'notifications.log')


def log_notification(message):
    """
    Log a notification to file.
    
    Args:
        message (str): Notification message to log
    """
    try:
        log_file = get_log_file()
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(log_file, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging notification: {e}")


def notify_order_confirmation(order, user):
    """
    Send order confirmation notification.
    
    Args:
        order: Order object
        user: User object
    """
    message = (
        f"ORDER_CREATED | Order #{order.id} confirmed for {user.email} | "
        f"Total: ${order.total_price:.2f} | Status: {order.status.value}"
    )
    log_notification(message)


def notify_status_change(order, old_status, new_status):
    """
    Send order status change notification.
    
    Args:
        order: Order object
        old_status: Previous status
        new_status: New status
    """
    message = (
        f"ORDER_STATUS_UPDATED | Order #{order.id} | "
        f"{old_status.value.upper()} → {new_status.value.upper()}"
    )
    log_notification(message)


def notify_order_delivery(order, user):
    """
    Send order delivered notification.
    
    Args:
        order: Order object
        user: User object
    """
    message = (
        f"ORDER_DELIVERED | Order #{order.id} delivered to {user.email} | "
        f"Total: ${order.total_price:.2f}"
    )
    log_notification(message)
