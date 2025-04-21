#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notification module for huizenzoeker application.
This module provides functionality for sending notifications about property changes.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from telegram import Bot, ParseMode
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class TelegramNotifier:
    """Class for sending notifications via Telegram."""
    
    def __init__(self, token: str, chat_id: Optional[str] = None):
        """
        Initialize the Telegram notifier.
        
        Args:
            token: Telegram Bot API token
            chat_id: Optional default chat ID to send messages to
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        self.logger = logging.getLogger("telegram_notifier")
    
    async def send_message_async(self, text: str, chat_id: Optional[str] = None, parse_mode: str = ParseMode.MARKDOWN) -> bool:
        """
        Send a message via Telegram asynchronously.
        
        Args:
            text: Message text
            chat_id: Chat ID to send message to (overrides default)
            parse_mode: Message parse mode (default: Markdown)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            self.logger.error("No chat ID provided")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_message(self, text: str, chat_id: Optional[str] = None, parse_mode: str = ParseMode.MARKDOWN) -> bool:
        """
        Send a message via Telegram (synchronous wrapper).
        
        Args:
            text: Message text
            chat_id: Chat ID to send message to (overrides default)
            parse_mode: Message parse mode (default: Markdown)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        return asyncio.run(self.send_message_async(text, chat_id, parse_mode))
    
    def format_property_message(self, property_data: Dict[str, Any], change_type: str = "new") -> str:
        """
        Format a property notification message.
        
        Args:
            property_data: Property data dictionary
            change_type: Type of change ("new", "updated", or "removed")
            
        Returns:
            Formatted message text
        """
        if change_type == "new":
            emoji = "🏠"
            title = "Nieuwe woning"
        elif change_type == "updated":
            emoji = "🔄"
            title = "Gewijzigde woning"
        elif change_type == "removed":
            emoji = "❌"
            title = "Verwijderde woning"
        else:
            emoji = "ℹ️"
            title = "Woning informatie"
        
        # Format basic property information
        address = property_data.get('address', 'Onbekend adres')
        city = property_data.get('city', 'Onbekende plaats')
        price = property_data.get('price', 0)
        area = property_data.get('area', 0)
        property_type = property_data.get('property_type', 'Onbekend')
        url = property_data.get('url', '')
        
        # Format price with euro symbol and thousand separators
        price_formatted = f"€{price:,}".replace(",", ".")
        
        # Build message
        message = f"{emoji} *{title}*\n\n"
        message += f"*{address}*\n"
        message += f"{city}\n\n"
        message += f"*Prijs:* {price_formatted}\n"
        message += f"*Oppervlakte:* {area} m²\n"
        message += f"*Type:* {property_type}\n"
        
        # Add changes if available
        if change_type == "updated" and 'changes' in property_data:
            message += "\n*Wijzigingen:*\n"
            for change in property_data['changes']:
                field = change['field']
                old_value = change['old_value']
                new_value = change['new_value']
                
                # Format field name in Dutch
                if field == 'price':
                    field_name = "Prijs"
                    old_value = f"€{old_value:,}".replace(",", ".")
                    new_value = f"€{new_value:,}".replace(",", ".")
                elif field == 'area':
                    field_name = "Oppervlakte"
                    old_value = f"{old_value} m²"
                    new_value = f"{new_value} m²"
                elif field == 'rooms':
                    field_name = "Kamers"
                elif field == 'property_type':
                    field_name = "Type"
                elif field == 'address':
                    field_name = "Adres"
                elif field == 'city':
                    field_name = "Plaats"
                else:
                    field_name = field
                
                message += f"- {field_name}: {old_value} → {new_value}\n"
        
        # Add URL
        if url:
            message += f"\n[Bekijk op website]({url})"
        
        return message
    
    def notify_property_changes(self, changes: Dict[str, List[Dict[str, Any]]], chat_id: Optional[str] = None) -> Dict[str, int]:
        """
        Send notifications for property changes.
        
        Args:
            changes: Dictionary with lists of new, updated, and removed properties
            chat_id: Chat ID to send messages to (overrides default)
            
        Returns:
            Dictionary with counts of sent notifications by type
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            self.logger.error("No chat ID provided")
            return {"new": 0, "updated": 0, "removed": 0}
        
        sent_counts = {"new": 0, "updated": 0, "removed": 0}
        
        # Send notifications for new properties
        for property_data in changes.get("new", []):
            message = self.format_property_message(property_data, "new")
            if self.send_message(message, target_chat_id):
                sent_counts["new"] += 1
        
        # Send notifications for updated properties
        for property_data in changes.get("updated", []):
            message = self.format_property_message(property_data, "updated")
            if self.send_message(message, target_chat_id):
                sent_counts["updated"] += 1
        
        # Send notifications for removed properties
        for property_data in changes.get("removed", []):
            message = self.format_property_message(property_data, "removed")
            if self.send_message(message, target_chat_id):
                sent_counts["removed"] += 1
        
        # Log results
        total_sent = sum(sent_counts.values())
        self.logger.info(f"Sent {total_sent} Telegram notifications: {sent_counts['new']} new, {sent_counts['updated']} updated, {sent_counts['removed']} removed")
        
        return sent_counts
    
    async def send_summary_async(self, changes: Dict[str, List[Dict[str, Any]]], chat_id: Optional[str] = None) -> bool:
        """
        Send a summary of property changes asynchronously.
        
        Args:
            changes: Dictionary with lists of new, updated, and removed properties
            chat_id: Chat ID to send message to (overrides default)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            self.logger.error("No chat ID provided")
            return False
        
        # Count changes
        new_count = len(changes.get("new", []))
        updated_count = len(changes.get("updated", []))
        removed_count = len(changes.get("removed", []))
        total_count = new_count + updated_count + removed_count
        
        if total_count == 0:
            message = "🏠 *Huizenzoeker Samenvatting*\n\nGeen wijzigingen gevonden."
        else:
            message = "🏠 *Huizenzoeker Samenvatting*\n\n"
            message += f"Totaal {total_count} wijzigingen gevonden:\n"
            message += f"- {new_count} nieuwe woningen\n"
            message += f"- {updated_count} gewijzigde woningen\n"
            message += f"- {removed_count} verwijderde woningen"
        
        try:
            await self.bot.send_message(
                chat_id=target_chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram summary: {str(e)}")
            return False
    
    def send_summary(self, changes: Dict[str, List[Dict[str, Any]]], chat_id: Optional[str] = None) -> bool:
        """
        Send a summary of property changes (synchronous wrapper).
        
        Args:
            changes: Dictionary with lists of new, updated, and removed properties
            chat_id: Chat ID to send message to (overrides default)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        return asyncio.run(self.send_summary_async(changes, chat_id))
