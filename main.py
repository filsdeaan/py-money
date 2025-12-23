"""
Py-Money - Aplikasi Pencatat Keuangan Berbasis CLI
Entry point utama program
"""
import sys
import sqlite3  # DITAMBAHKAN untuk handle exception
from datetime import datetime

# Import modul internal
from database import Database
from models import Category, Transaction
from utils import (
    clear_screen, print_header, format_currency, 
    format_date, validate_date, validate_amount,
    get_input, confirm_action
)

class PyMoneyApp:
    """Aplikasi utama Py-Money"""
    
    def __init__(self):
        self.db = Database()
        self.running = True
    
    def run(self):
        """Menjalankan aplikasi"""
        self.show_welcome()
        
        while self.running:
            clear_screen()
            self.show_main_menu()
            choice = input("\nPilih menu [1-4, x]: ").strip().lower()
            
            if choice == '1':
                self.income_menu()
            elif choice == '2':
                self.expense_menu()
            elif choice == '3':
                self.category_menu()
            elif choice == '4':
                self.balance_menu()
            elif choice == 'x':
                if confirm_action("Keluar dari program?"):
                    self.running = False
                    print("\n👋 Terima kasih telah menggunakan Py-Money!")
            else:
                print("❌ Pilihan tidak valid!")
                input("\nTekan Enter untuk melanjutkan...")
    
    # ===== WELCOME SCREEN =====
    def show_welcome(self):
        """Menampilkan pesan selamat datang dengan ASCII art"""
        clear_screen()
        welcome_art = """
██████╗ ██╗   ██╗    ███╗   ███╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗
██╔══██╗╚██╗ ██╔╝    ████╗ ████║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝
██████╔╝ ╚████╔╝     ██╔████╔██║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ 
██╔═══╝   ╚██╔╝      ██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  
██║        ██║       ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗   ██║   
╚═╝        ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   
        """
        print(welcome_art)
        print("📊 Aplikasi Pencatat Keuangan Pribadi")
        print("=" * 60)
        input("\nTekan Enter untuk melanjutkan...")
    
    # ===== MAIN MENU =====
    def show_main_menu(self):
        """Menampilkan menu utama"""
        print_header("PY-MONEY - MENU UTAMA")
        print("\n📋 Pilihan Menu:")
        print("1. 💰 Pemasukan")
        print("2. 💸 Pengeluaran")
        print("3. 🏷️  Kategori")
        print("4. 📊 Balance & Ringkasan")
        print("\nx. 🚪 Keluar Program")
        print("\n" + "=" * 60)
    
    # ===== INCOME MENU =====
    def income_menu(self):
        """Menu untuk mengelola pemasukan"""
        while True:
            clear_screen()
            print_header("💰 MENU PEMASUKAN")
            print("\n📋 Pilihan:")
            print("1. 📜 List Pemasukan")
            print("2. ➕ Tambah Pemasukan")
            print("3. 🗑️  Hapus Pemasukan")
            print("\nq. ↩️  Kembali ke Menu Utama")
            print("=" * 60)
            
            choice = input("\nPilih [1-3, q]: ").strip().lower()
            
            if choice == '1':
                self.list_income()
            elif choice == '2':
                self.add_income()
            elif choice == '3':
                self.delete_income()
            elif choice == 'q':
                break
            else:
                print("❌ Pilihan tidak valid!")
                input("Tekan Enter untuk melanjutkan...")
    
    def list_income(self):
        """Menampilkan daftar pemasukan"""
        clear_screen()
        print_header("📜 DAFTAR PEMASUKAN")
        
        transactions = self.db.get_transactions(type_filter='income')
        
        if not transactions:
            print("\n📭 Tidak ada data pemasukan.")
        else:
            total = 0
            print("\nID  | Tanggal      | Kategori       | Jumlah         | Deskripsi")
            print("-" * 70)
            for row in transactions:
                transaction = Transaction.from_db_row(row)
                total += transaction.amount
                print(f"{transaction.id:3d} | {format_date(transaction.date.strftime('%Y-%m-%d')):12} | "
                      f"{transaction.category_name:15} | {format_currency(transaction.amount):15} | "
                      f"{transaction.description or '-'}")
            
            print("-" * 70)
            print(f"Total Pemasukan: {format_currency(total):>49}")
            
            # Tampilkan pilihan edit
            print("\n🔧 Untuk mengedit, masukkan ID pemasukan")
            print("b. ↩️  Kembali ke Menu Pemasukan")
            print("=" * 60)
            
            choice = input("\nPilihan [ID/b]: ").strip().lower()
            
            if choice == 'b':
                return
            elif choice.isdigit():
                self.edit_transaction(int(choice), 'income')
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def add_income(self):
        """Menambah pemasukan baru"""
        clear_screen()
        print_header("➕ TAMBAH PEMASUKAN")
        
        # Dapatkan kategori pemasukan
        categories = self.db.get_all_categories(type_filter='income')
        if not categories:
            print("\n❌ Tidak ada kategori pemasukan. Tambah kategori terlebih dahulu.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        print("\n🏷️  Kategori Pemasukan yang tersedia:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat['name']}")
        
        # Input kategori
        while True:
            try:
                cat_idx = int(input(f"\nPilih kategori [1-{len(categories)}]: "))
                if 1 <= cat_idx <= len(categories):
                    category_id = categories[cat_idx-1]['id']
                    category_name = categories[cat_idx-1]['name']
                    break
                else:
                    print("❌ Pilihan tidak valid!")
            except ValueError:
                print("❌ Masukkan angka yang valid!")
        
        # Input jumlah
        while True:
            amount_str = input("\n💰 Jumlah pemasukan: Rp").strip()
            amount = validate_amount(amount_str)
            if amount is not None:
                break
            print("❌ Jumlah tidak valid! Masukkan angka positif.")
        
        # Input deskripsi
        description = input("\n📝 Deskripsi (opsional): ").strip() or None
        
        # Input tanggal
        today = datetime.now().strftime("%Y-%m-%d")
        while True:
            date_str = input(f"\n📅 Tanggal (YYYY-MM-DD) [{today}]: ").strip()
            if not date_str:
                date_str = today
            
            if validate_date(date_str):
                break
            print("❌ Format tanggal tidak valid! Gunakan format YYYY-MM-DD")
        
        # Konfirmasi
        print("\n" + "=" * 60)
        print("📋 Ringkasan Pemasukan:")
        print(f"Kategori   : {category_name}")
        print(f"Jumlah     : {format_currency(amount)}")
        print(f"Deskripsi  : {description or '-'}")
        print(f"Tanggal    : {format_date(date_str)}")
        print("=" * 60)
        
        if confirm_action("\nSimpan pemasukan ini?"):
            transaction_id = self.db.add_transaction(
                type_='income',
                amount=amount,
                category_id=category_id,
                description=description,
                date=date_str
            )
            print(f"\n✅ Pemasukan berhasil ditambahkan! (ID: {transaction_id})")
        else:
            print("\n❌ Pemasukan dibatalkan.")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def delete_income(self):
        """Menghapus pemasukan"""
        clear_screen()
        print_header("🗑️  HAPUS PEMASUKAN")
        
        # Tampilkan daftar singkat
        transactions = self.db.get_transactions(type_filter='income', limit=10)
        
        if not transactions:
            print("\n📭 Tidak ada data pemasukan.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        print("\n📜 Daftar Pemasukan Terakhir:")
        print("ID  | Tanggal      | Kategori       | Jumlah")
        print("-" * 50)
        for row in transactions:
            transaction = Transaction.from_db_row(row)
            print(f"{transaction.id:3d} | {format_date(transaction.date.strftime('%Y-%m-%d')):12} | "
                  f"{transaction.category_name:15} | {format_currency(transaction.amount)}")
        
        print("=" * 60)
        
        while True:
            choice = input("\nMasukkan ID pemasukan yang akan dihapus (atau 'b' untuk batal): ").strip().lower()
            
            if choice == 'b':
                return
            
            if choice.isdigit():
                transaction_id = int(choice)
                transaction = self.db.get_transaction(transaction_id)
                
                if not transaction:
                    print("❌ ID tidak ditemukan!")
                    continue
                
                if transaction['type'] != 'income':
                    print("❌ ID tersebut bukan pemasukan!")
                    continue
                
                # Tampilkan detail
                print("\n" + "=" * 60)
                print("📋 Detail Pemasukan:")
                print(f"ID         : {transaction['id']}")
                print(f"Tanggal    : {format_date(transaction['date'])}")
                print(f"Kategori   : {transaction.get('category_name', 'Unknown')}")
                print(f"Jumlah     : {format_currency(transaction['amount'])}")
                print(f"Deskripsi  : {transaction['description'] or '-'}")
                print("=" * 60)
                
                if confirm_action("Yakin ingin menghapus pemasukan ini?"):
                    if self.db.delete_transaction(transaction_id):
                        print("✅ Pemasukan berhasil dihapus!")
                    else:
                        print("❌ Gagal menghapus pemasukan!")
                else:
                    print("❌ Penghapusan dibatalkan.")
                
                break
        
        input("\nTekan Enter untuk melanjutkan...")
    
    # ===== EXPENSE MENU =====
    def expense_menu(self):
        """Menu untuk mengelola pengeluaran"""
        while True:
            clear_screen()
            print_header("💸 MENU PENGELUARAN")
            print("\n📋 Pilihan:")
            print("1. 📜 List Pengeluaran")
            print("2. ➕ Tambah Pengeluaran")
            print("3. 🗑️  Hapus Pengeluaran")
            print("\nq. ↩️  Kembali ke Menu Utama")
            print("=" * 60)
            
            choice = input("\nPilih [1-3, q]: ").strip().lower()
            
            if choice == '1':
                self.list_expense()
            elif choice == '2':
                self.add_expense()
            elif choice == '3':
                self.delete_expense()
            elif choice == 'q':
                break
            else:
                print("❌ Pilihan tidak valid!")
                input("Tekan Enter untuk melanjutkan...")
    
    def list_expense(self):
        """Menampilkan daftar pengeluaran"""
        clear_screen()
        print_header("📜 DAFTAR PENGELUARAN")
        
        transactions = self.db.get_transactions(type_filter='expense')
        
        if not transactions:
            print("\n📭 Tidak ada data pengeluaran.")
        else:
            total = 0
            print("\nID  | Tanggal      | Kategori       | Jumlah         | Deskripsi")
            print("-" * 70)
            for row in transactions:
                transaction = Transaction.from_db_row(row)
                total += transaction.amount
                print(f"{transaction.id:3d} | {format_date(transaction.date.strftime('%Y-%m-%d')):12} | "
                      f"{transaction.category_name:15} | {format_currency(transaction.amount):15} | "
                      f"{transaction.description or '-'}")
            
            print("-" * 70)
            print(f"Total Pengeluaran: {format_currency(total):>48}")
            
            # Tampilkan pilihan edit
            print("\n🔧 Untuk mengedit, masukkan ID pengeluaran")
            print("b. ↩️  Kembali ke Menu Pengeluaran")
            print("=" * 60)
            
            choice = input("\nPilihan [ID/b]: ").strip().lower()
            
            if choice == 'b':
                return
            elif choice.isdigit():
                self.edit_transaction(int(choice), 'expense')
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def add_expense(self):
        """Menambah pengeluaran baru"""
        clear_screen()
        print_header("➕ TAMBAH PENGELUARAN")
        
        # Dapatkan kategori pengeluaran
        categories = self.db.get_all_categories(type_filter='expense')
        if not categories:
            print("\n❌ Tidak ada kategori pengeluaran. Tambah kategori terlebih dahulu.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        print("\n🏷️  Kategori Pengeluaran yang tersedia:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat['name']}")
        
        # Input kategori
        while True:
            try:
                cat_idx = int(input(f"\nPilih kategori [1-{len(categories)}]: "))
                if 1 <= cat_idx <= len(categories):
                    category_id = categories[cat_idx-1]['id']
                    category_name = categories[cat_idx-1]['name']
                    break
                else:
                    print("❌ Pilihan tidak valid!")
            except ValueError:
                print("❌ Masukkan angka yang valid!")
        
        # Input jumlah
        while True:
            amount_str = input("\n💰 Jumlah pengeluaran: Rp").strip()
            amount = validate_amount(amount_str)
            if amount is not None:
                break
            print("❌ Jumlah tidak valid! Masukkan angka positif.")
        
        # Input deskripsi
        description = input("\n📝 Deskripsi (opsional): ").strip() or None
        
        # Input tanggal
        today = datetime.now().strftime("%Y-%m-%d")
        while True:
            date_str = input(f"\n📅 Tanggal (YYYY-MM-DD) [{today}]: ").strip()
            if not date_str:
                date_str = today
            
            if validate_date(date_str):
                break
            print("❌ Format tanggal tidak valid! Gunakan format YYYY-MM-DD")
        
        # Konfirmasi
        print("\n" + "=" * 60)
        print("📋 Ringkasan Pengeluaran:")
        print(f"Kategori   : {category_name}")
        print(f"Jumlah     : {format_currency(amount)}")
        print(f"Deskripsi  : {description or '-'}")
        print(f"Tanggal    : {format_date(date_str)}")
        print("=" * 60)
        
        if confirm_action("\nSimpan pengeluaran ini?"):
            transaction_id = self.db.add_transaction(
                type_='expense',
                amount=amount,
                category_id=category_id,
                description=description,
                date=date_str
            )
            print(f"\n✅ Pengeluaran berhasil ditambahkan! (ID: {transaction_id})")
        else:
            print("\n❌ Pengeluaran dibatalkan.")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def delete_expense(self):
        """Menghapus pengeluaran"""
        clear_screen()
        print_header("🗑️  HAPUS PENGELUARAN")
        
        # Tampilkan daftar singkat
        transactions = self.db.get_transactions(type_filter='expense', limit=10)
        
        if not transactions:
            print("\n📭 Tidak ada data pengeluaran.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        print("\n📜 Daftar Pengeluaran Terakhir:")
        print("ID  | Tanggal      | Kategori       | Jumlah")
        print("-" * 50)
        for row in transactions:
            transaction = Transaction.from_db_row(row)
            print(f"{transaction.id:3d} | {format_date(transaction.date.strftime('%Y-%m-%d')):12} | "
                  f"{transaction.category_name:15} | {format_currency(transaction.amount)}")
        
        print("=" * 60)
        
        while True:
            choice = input("\nMasukkan ID pengeluaran yang akan dihapus (atau 'b' untuk batal): ").strip().lower()
            
            if choice == 'b':
                return
            
            if choice.isdigit():
                transaction_id = int(choice)
                transaction = self.db.get_transaction(transaction_id)
                
                if not transaction:
                    print("❌ ID tidak ditemukan!")
                    continue
                
                if transaction['type'] != 'expense':
                    print("❌ ID tersebut bukan pengeluaran!")
                    continue
                
                # Tampilkan detail
                print("\n" + "=" * 60)
                print("📋 Detail Pengeluaran:")
                print(f"ID         : {transaction['id']}")
                print(f"Tanggal    : {format_date(transaction['date'])}")
                print(f"Kategori   : {transaction.get('category_name', 'Unknown')}")
                print(f"Jumlah     : {format_currency(transaction['amount'])}")
                print(f"Deskripsi  : {transaction['description'] or '-'}")
                print("=" * 60)
                
                if confirm_action("Yakin ingin menghapus pengeluaran ini?"):
                    if self.db.delete_transaction(transaction_id):
                        print("✅ Pengeluaran berhasil dihapus!")
                    else:
                        print("❌ Gagal menghapus pengeluaran!")
                else:
                    print("❌ Penghapusan dibatalkan.")
                
                break
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def edit_transaction(self, transaction_id: int, expected_type: str):
        """Edit transaksi (pemasukan/pengeluaran)"""
        transaction = self.db.get_transaction(transaction_id)
        
        if not transaction:
            print("\n❌ Transaksi tidak ditemukan!")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        if transaction['type'] != expected_type:
            print(f"\n❌ ID {transaction_id} bukan {expected_type}!")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        clear_screen()
        type_name = "Pemasukan" if expected_type == 'income' else "Pengeluaran"
        print_header(f"✏️  EDIT {type_name.upper()} (ID: {transaction_id})")
        
        # Tampilkan data saat ini
        print("\n📋 Data Saat Ini:")
        print(f"1. Tanggal     : {format_date(transaction['date'])}")
        print(f"2. Kategori    : {transaction.get('category_name', 'Unknown')}")
        print(f"3. Jumlah      : {format_currency(transaction['amount'])}")
        print(f"4. Deskripsi   : {transaction['description'] or '-'}")
        print("\n" + "=" * 60)
        
        # Input perubahan
        print("\nMasukkan data baru (kosongkan jika tidak ingin mengubah):")
        
        # Tanggal
        current_date = transaction['date']
        new_date = input(f"\n📅 Tanggal (YYYY-MM-DD) [{format_date(current_date)}]: ").strip()
        if not new_date:
            new_date = current_date
        elif not validate_date(new_date):
            print("❌ Format tanggal tidak valid! Data tidak diubah.")
            new_date = current_date
        
        # Kategori
        categories = self.db.get_all_categories(type_filter=expected_type)
        print(f"\n🏷️  Kategori {type_name} yang tersedia:")
        for i, cat in enumerate(categories, 1):
            prefix = ">" if cat['id'] == transaction['category_id'] else " "
            print(f"{prefix}{i}. {cat['name']}")
        
        cat_choice = input(f"\nPilih kategori [1-{len(categories)}, Enter untuk tetap]: ").strip()
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            category_id = categories[int(cat_choice)-1]['id']
        else:
            category_id = transaction['category_id']
        
        # Jumlah
        current_amount = transaction['amount']
        amount_str = input(f"\n💰 Jumlah {type_name.lower()} [Rp{format_currency(current_amount)}]: Rp").strip()
        if amount_str:
            new_amount = validate_amount(amount_str)
            if new_amount is None:
                print("❌ Jumlah tidak valid! Data tidak diubah.")
                new_amount = current_amount
        else:
            new_amount = current_amount
        
        # Deskripsi
        current_desc = transaction['description'] or ''
        new_desc = input(f"\n📝 Deskripsi [{current_desc}]: ").strip()
        if not new_desc:
            new_desc = current_desc
        
        # Konfirmasi
        print("\n" + "=" * 60)
        print("📋 Ringkasan Perubahan:")
        print(f"Tanggal     : {format_date(current_date)} → {format_date(new_date)}")
        category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), "Unknown")
        print(f"Kategori    : {transaction.get('category_name', 'Unknown')} → {category_name}")
        print(f"Jumlah      : {format_currency(current_amount)} → {format_currency(new_amount)}")
        print(f"Deskripsi   : {current_desc or '-'} → {new_desc or '-'}")
        print("=" * 60)
        
        if confirm_action("\nSimpan perubahan?"):
            if self.db.update_transaction(
                transaction_id=transaction_id,
                amount=new_amount,
                category_id=category_id,
                description=new_desc if new_desc != current_desc else transaction['description'],
                date=new_date
            ):
                print("✅ Transaksi berhasil diperbarui!")
            else:
                print("❌ Gagal memperbarui transaksi!")
        else:
            print("❌ Perubahan dibatalakan.")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    # ===== CATEGORY MENU =====
    def category_menu(self):
        """Menu untuk mengelola kategori"""
        while True:
            clear_screen()
            print_header("🏷️  MENU KATEGORI")
            print("\n📋 Pilihan:")
            print("1. 📜 List Kategori")
            print("2. ➕ Tambah Kategori")
            print("3. 🗑️  Hapus Kategori")
            print("\nq. ↩️  Kembali ke Menu Utama")
            print("=" * 60)
            
            choice = input("\nPilih [1-3, q]: ").strip().lower()
            
            if choice == '1':
                self.list_categories()
            elif choice == '2':
                self.add_category()
            elif choice == '3':
                self.delete_category()
            elif choice == 'q':
                break
            else:
                print("❌ Pilihan tidak valid!")
                input("Tekan Enter untuk melanjutkan...")
    
    def list_categories(self):
        """Menampilkan daftar kategori"""
        clear_screen()
        print_header("📜 DAFTAR KATEGORI")
        
        categories = self.db.get_all_categories()
        
        if not categories:
            print("\n📭 Tidak ada kategori.")
        else:
            print("\nID  | Tipe         | Nama Kategori")
            print("-" * 40)
            
            income_categories = [cat for cat in categories if cat['type'] == 'income']
            expense_categories = [cat for cat in categories if cat['type'] == 'expense']
            
            print("\n💰 PEMASUKAN:")
            for cat in income_categories:
                print(f"{cat['id']:3d} | {'Pemasukan':12} | {cat['name']}")
            
            print("\n💸 PENGELUARAN:")
            for cat in expense_categories:
                print(f"{cat['id']:3d} | {'Pengeluaran':12} | {cat['name']}")
            
            print(f"\n📊 Total: {len(categories)} kategori "
                  f"({len(income_categories)} pemasukan, {len(expense_categories)} pengeluaran)")
        
        input("\n\nTekan Enter untuk melanjutkan...")
    
    def add_category(self):
        """Menambah kategori baru"""
        clear_screen()
        print_header("➕ TAMBAH KATEGORI")
        
        # Input nama kategori
        while True:
            name = input("\n🏷️  Nama kategori baru: ").strip()
            if name:
                break
            print("❌ Nama kategori tidak boleh kosong!")
        
        # Input tipe kategori
        print("\n📋 Tipe Kategori:")
        print("1. 💰 Pemasukan")
        print("2. 💸 Pengeluaran")
        
        while True:
            type_choice = input("\nPilih tipe [1-2]: ").strip()
            if type_choice == '1':
                type_ = 'income'
                break
            elif type_choice == '2':
                type_ = 'expense'
                break
            else:
                print("❌ Pilihan tidak valid!")
        
        # Konfirmasi
        type_name = "Pemasukan" if type_ == 'income' else "Pengeluaran"
        print("\n" + "=" * 60)
        print("📋 Ringkasan Kategori:")
        print(f"Nama   : {name}")
        print(f"Tipe   : {type_name}")
        print("=" * 60)
        
        if confirm_action("\nSimpan kategori ini?"):
            try:
                category_id = self.db.add_category(name, type_)
                print(f"\n✅ Kategori berhasil ditambahkan! (ID: {category_id})")
            except sqlite3.IntegrityError:  # DIPERBAIKI: menggunakan sqlite3.IntegrityError
                print("❌ Kategori dengan nama tersebut sudah ada!")
        else:
            print("\n❌ Penambahan kategori dibatalkan.")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def delete_category(self):
        """Menghapus kategori"""
        clear_screen()
        print_header("🗑️  HAPUS KATEGORI")
        
        categories = self.db.get_all_categories()
        
        if not categories:
            print("\n📭 Tidak ada kategori.")
            input("\nTekan Enter untuk melanjutkan...")
            return
        
        print("\n📜 Daftar Kategori:")
        print("ID  | Tipe         | Nama Kategori")
        print("-" * 40)
        for cat in categories:
            type_name = "Pemasukan" if cat['type'] == 'income' else "Pengeluaran"
            print(f"{cat['id']:3d} | {type_name:12} | {cat['name']}")
        
        print("=" * 60)
        
        while True:
            choice = input("\nMasukkan ID kategori yang akan dihapus (atau 'b' untuk batal): ").strip().lower()
            
            if choice == 'b':
                return
            
            if choice.isdigit():
                category_id = int(choice)
                category = self.db.get_category(category_id)
                
                if not category:
                    print("❌ ID tidak ditemukan!")
                    continue
                
                # Tampilkan detail
                type_name = "Pemasukan" if category['type'] == 'income' else "Pengeluaran"
                print("\n" + "=" * 60)
                print("📋 Detail Kategori:")
                print(f"ID   : {category['id']}")
                print(f"Nama : {category['name']}")
                print(f"Tipe : {type_name}")
                print("=" * 60)
                
                if confirm_action("Yakin ingin menghapus kategori ini?"):
                    if self.db.delete_category(category_id):
                        print("✅ Kategori berhasil dihapus!")
                    else:
                        print("❌ Gagal menghapus kategori! Kategori masih digunakan dalam transaksi.")
                else:
                    print("❌ Penghapusan dibatalkan.")
                
                break
        
        input("\nTekan Enter untuk melanjutkan...")
    
    # ===== BALANCE MENU =====
    def balance_menu(self):
        """Menu untuk melihat balance dan ringkasan"""
        clear_screen()
        print_header("📊 BALANCE & RINGKASAN")
        
        summary = self.db.get_balance_summary()
        
        # Ringkasan utama
        print("\n💰 RINGKASAN KEUANGAN")
        print("=" * 40)
        print(f"Total Pemasukan   : {format_currency(summary['total_income']):>20}")
        print(f"Total Pengeluaran : {format_currency(summary['total_expense']):>20}")
        print("-" * 40)
        
        balance = summary['balance']
        balance_str = format_currency(abs(balance))
        if balance >= 0:
            print(f"SISA SALDO        : {balance_str:>20} 💰")
        else:
            print(f"DEFISIT           : {balance_str:>20} ⚠️")
        
        print("=" * 40)
        
        # Ringkasan per kategori
        if summary['by_category']:
            print("\n📈 RINGKASAN PER KATEGORI")
            print("=" * 60)
            
            print("\n💰 PEMASUKAN:")
            income_cats = [row for row in summary['by_category'] if row['type'] == 'income']
            if income_cats:
                for row in income_cats:
                    percentage = (row['total'] / summary['total_income'] * 100) if summary['total_income'] > 0 else 0
                    bar = "█" * int(percentage / 5)  # 5% per karakter
                    print(f"  {row['category_name']:15} {format_currency(row['total']):>15} {percentage:5.1f}% {bar}")
            else:
                print("  (Tidak ada data pemasukan)")
            
            print("\n💸 PENGELUARAN:")
            expense_cats = [row for row in summary['by_category'] if row['type'] == 'expense']
            if expense_cats:
                for row in expense_cats:
                    percentage = (row['total'] / summary['total_expense'] * 100) if summary['total_expense'] > 0 else 0
                    bar = "█" * int(percentage / 5)  # 5% per karakter
                    print(f"  {row['category_name']:15} {format_currency(row['total']):>15} {percentage:5.1f}% {bar}")
            else:
                print("  (Tidak ada data pengeluaran)")
        
        print("\n" + "=" * 60)
        input("\nTekan Enter untuk kembali ke menu utama...")


def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    try:
        app = PyMoneyApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan oleh user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        print("Silakan coba jalankan program kembali.")
        sys.exit(1)


if __name__ == "__main__":
    main()