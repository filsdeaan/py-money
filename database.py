"""
Modul untuk operasi database SQLite
"""
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_name: str = "py_money.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Membuat koneksi ke database"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Mengembalikan hasil sebagai dictionary
        return conn
    
    def init_database(self):
        """Inisialisasi tabel database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabel kategori
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel transaksi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    amount REAL NOT NULL CHECK(amount >= 0),
                    category_id INTEGER NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
                )
            ''')
            
            # Insert kategori default jika belum ada
            default_categories = [
                ('Gaji', 'income'),
                ('Investasi', 'income'),
                ('Hadiah', 'income'),
                ('Makanan', 'expense'),
                ('Transportasi', 'expense'),
                ('Hiburan', 'expense'),
                ('Tagihan', 'expense'),
            ]
            
            for name, type_ in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, type) 
                    VALUES (?, ?)
                ''', (name, type_))
            
            conn.commit()
    
    # ===== OPERASI KATEGORI =====
    def get_all_categories(self, type_filter: Optional[str] = None) -> List[sqlite3.Row]:
        """Mengambil semua kategori, bisa difilter berdasarkan type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if type_filter:
                cursor.execute('SELECT * FROM categories WHERE type = ? ORDER BY name', (type_filter,))
            else:
                cursor.execute('SELECT * FROM categories ORDER BY type, name')
            return cursor.fetchall()
    
    def get_category(self, category_id: int) -> Optional[sqlite3.Row]:
        """Mengambil kategori berdasarkan ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            return cursor.fetchone()
    
    def add_category(self, name: str, type_: str) -> int:
        """Menambah kategori baru"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO categories (name, type) VALUES (?, ?)',
                (name, type_)
            )
            conn.commit()
            return cursor.lastrowid
    
    def delete_category(self, category_id: int) -> bool:
        """Menghapus kategori jika tidak digunakan"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Cek apakah kategori digunakan dalam transaksi
            cursor.execute('SELECT COUNT(*) FROM transactions WHERE category_id = ?', (category_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                return False  # Tidak bisa dihapus karena masih digunakan
            
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            conn.commit()
            return True
    
    def get_category_id_by_name(self, name: str) -> Optional[int]:
        """Mendapatkan ID kategori berdasarkan nama"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    # ===== OPERASI TRANSAKSI =====
    def add_transaction(self, type_: str, amount: float, category_id: int, 
                       description: str, date: str) -> int:
        """Menambah transaksi baru"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (type, amount, category_id, description, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, amount, category_id, description, date))
            conn.commit()
            return cursor.lastrowid
    
    def get_transactions(self, type_filter: Optional[str] = None, 
                        limit: int = 50) -> List[sqlite3.Row]:
        """Mengambil transaksi dengan join kategori"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT t.*, c.name as category_name, c.type as category_type
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
            '''
            
            params = []
            if type_filter:
                query += ' WHERE t.type = ?'
                params.append(type_filter)
            
            query += ' ORDER BY t.date DESC, t.created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_transaction(self, transaction_id: int) -> Optional[sqlite3.Row]:
        """Mengambil transaksi berdasarkan ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, c.name as category_name, c.type as category_type
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
            ''', (transaction_id,))
            return cursor.fetchone()
    
    def update_transaction(self, transaction_id: int, amount: float, 
                          category_id: int, description: str, date: str) -> bool:
        """Update transaksi"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions 
                SET amount = ?, category_id = ?, description = ?, date = ?
                WHERE id = ?
            ''', (amount, category_id, description, date, transaction_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Menghapus transaksi"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ===== STATISTIK DAN LAPORAN =====
    def get_balance_summary(self) -> dict:
        """Menghitung ringkasan saldo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total pemasukan dan pengeluaran
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions
            ''')
            totals = cursor.fetchone()
            
            # Ringkasan per kategori
            cursor.execute('''
                SELECT 
                    c.type,
                    c.name as category_name,
                    SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                GROUP BY c.type, c.id
                ORDER BY c.type DESC, total DESC
            ''')
            by_category = cursor.fetchall()
            
            return {
                'total_income': totals['total_income'] or 0,
                'total_expense': totals['total_expense'] or 0,
                'balance': (totals['total_income'] or 0) - (totals['total_expense'] or 0),
                'by_category': by_category
            }
    
    def get_transactions_by_date_range(self, start_date: str, end_date: str) -> List[sqlite3.Row]:
        """Mengambil transaksi berdasarkan rentang tanggal"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, c.name as category_name, c.type as category_type
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.date BETWEEN ? AND ?
                ORDER BY t.date DESC
            ''', (start_date, end_date))
            return cursor.fetchall()