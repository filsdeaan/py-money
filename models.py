"""
Data models untuk aplikasi py-money
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Category:
    """Model untuk kategori"""
    id: int
    name: str
    type: str  # 'income' atau 'expense'
    created_at: datetime
    
    @classmethod
    def from_db_row(cls, row):
        """Membuat objek Category dari row database"""
        return cls(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def __str__(self):
        return f"{self.name} ({self.type})"

@dataclass
class Transaction:
    """Model untuk transaksi"""
    id: int
    type: str  # 'income' atau 'expense'
    amount: float
    category_id: int
    category_name: str
    description: Optional[str]
    date: datetime
    created_at: datetime
    
    @classmethod
    def from_db_row(cls, row):
        """Membuat objek Transaction dari row database"""
        return cls(
            id=row['id'],
            type=row['type'],
            amount=row['amount'],
            category_id=row['category_id'],
            category_name=row.get('category_name', 'Unknown'),
            description=row['description'],
            date=datetime.fromisoformat(row['date']),
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def __str__(self):
        return (f"{self.date.strftime('%Y-%m-%d')} | "
                f"{'Pemasukan' if self.type == 'income' else 'Pengeluaran':12} | "
                f"{self.category_name:15} | "
                f"Rp{self.amount:>12,.2f} | "
                f"{self.description or '-'}")