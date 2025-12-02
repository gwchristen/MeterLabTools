"""
OOR (Out of Range) Serial Parser
Handles parsing of OOR serial entries with ranges, singles, and combinations
"""

from typing import List, Tuple, Optional
import re


class OORParser:
    """Parse and calculate quantities from OOR serial entries"""
    
    def __init__(self):
        self.entries: List[Tuple[int, int]] = []  # List of (start, end) tuples
        self.total_qty = 0
    
    def parse(self, oor_text: str) -> bool:
        """
        Parse OOR serial text into individual entries
        
        Supports formats:
        - Ranges: "1000-1010" (11 items)
        - Singles: "1050" (1 item)
        - Combinations: "1000-1010, 1050, 2000-2005" (18 items)
        
        Args:
            oor_text: The OOR serial text to parse
            
        Returns:
            True if parsing succeeded, False otherwise
        """
        self.entries = []
        self.total_qty = 0
        
        if not oor_text or not oor_text.strip():
            return True
        
        # Split by comma or semicolon
        parts = re.split(r'[,;]', oor_text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if it's a range (e.g., "1000-1010")
            if '-' in part:
                try:
                    range_parts = part.split('-')
                    if len(range_parts) != 2:
                        return False
                    
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                    
                    if start > end:
                        return False
                    
                    self.entries.append((start, end))
                    self.total_qty += (end - start + 1)
                    
                except ValueError:
                    return False
            else:
                # Single number
                try:
                    num = int(part.strip())
                    self.entries.append((num, num))
                    self.total_qty += 1
                except ValueError:
                    return False
        
        return True
    
    def calculate_qty_from_range(self, beg_ser: str, end_ser: str) -> int:
        """
        Calculate quantity from beginning and ending serial numbers
        
        Args:
            beg_ser: Beginning serial number
            end_ser: Ending serial number
            
        Returns:
            Quantity (difference + 1), or 0 if invalid
        """
        try:
            # Extract numeric parts
            beg_num = int(re.sub(r'\D', '', beg_ser)) if beg_ser else 0
            end_num = int(re.sub(r'\D', '', end_ser)) if end_ser else 0
            
            if beg_num > 0 and end_num >= beg_num:
                return end_num - beg_num + 1
        except (ValueError, AttributeError):
            pass
        
        return 0
    
    def get_total_qty(self) -> int:
        """Get total quantity from parsed entries"""
        return self.total_qty
    
    def format_display(self, max_length: int = 50) -> str:
        """
        Format OOR entries for compact display
        
        Args:
            max_length: Maximum length for display
            
        Returns:
            Formatted string like "3 entries (45)" or full text if short
        """
        if not self.entries:
            return ""
        
        # Build full text
        parts = []
        for start, end in self.entries:
            if start == end:
                parts.append(str(start))
            else:
                parts.append(f"{start}-{end}")
        
        full_text = ", ".join(parts)
        
        # If short enough, return as is
        if len(full_text) <= max_length:
            return full_text
        
        # Otherwise, return compact format
        return f"{len(self.entries)} entries ({self.total_qty})"
    
    def get_detailed_breakdown(self) -> str:
        """
        Get detailed breakdown of all OOR entries
        
        Returns:
            Multi-line string with each entry and its count
        """
        if not self.entries:
            return "No entries"
        
        lines = []
        for i, (start, end) in enumerate(self.entries, 1):
            if start == end:
                lines.append(f"{i}. {start} (1 item)")
            else:
                count = end - start + 1
                lines.append(f"{i}. {start}-{end} ({count} items)")
        
        lines.append(f"\nTotal: {self.total_qty} items")
        return "\n".join(lines)
    
    @staticmethod
    def validate_oor_text(oor_text: str) -> Tuple[bool, str]:
        """
        Validate OOR text and return error message if invalid
        
        Args:
            oor_text: The OOR serial text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        parser = OORParser()
        if parser.parse(oor_text):
            return True, ""
        else:
            return False, "Invalid OOR format. Use ranges (1000-1010) or singles (1050), separated by commas."
