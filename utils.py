"""
Utility functions untuk py-money
"""
import os
from datetime import datetime
from typing import Optional

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Mencetak header dengan border"""
    width = 60
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def format_currency(amount: float) -> str:
    """Format angka menjadi format mata uang Indonesia"""
    return f"Rp{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_date(date_str: str, input_format: str = "%Y-%m-%d") -> str:
    """Format tanggal menjadi string yang lebih mudah dibaca"""
    try:
        date = datetime.strptime(date_str, input_format)
        return date.strftime("%d %b %Y")
    except ValueError:
        return date_str

def validate_date(date_str: str) -> bool:
    """Validasi format tanggal YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_amount(amount_str: str) -> Optional[float]:
    """Validasi dan konversi string amount ke float"""
    try:
        amount = float(amount_str.replace(',', '.'))
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None

def get_input(prompt: str, default: str = "", required: bool = True) -> str:
    """Mendapatkan input dari user dengan validasi"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not required or user_input:
            return user_input
        print("❌ Input tidak boleh kosong!")

def confirm_action(prompt: str = "Apakah Anda yakin?") -> bool:
    """Konfirmasi tindakan dengan user"""
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ['y', 'ya', 'yes']