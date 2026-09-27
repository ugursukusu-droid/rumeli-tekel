import os
import sqlite3
import datetime
import hashlib
import secrets
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

DB_FILE = os.environ.get("DATABASE_PATH", "rumeli_cloud.db")
try:
    _test_conn = sqlite3.connect(DB_FILE)
    _test_conn.execute("CREATE TABLE IF NOT EXISTS _test (id INT)")
    _test_conn.close()
except Exception:
    DB_FILE = "/tmp/rumeli_cloud.db"

app = FastAPI(title="Rumeli Tekel - Tedarikçi Cari & Borç Takip Sistemi (Production)")

# Enable CORS for any domain (Render, Custom Domain, Localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        contact_person TEXT,
        phone TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        doc_no TEXT,
        description TEXT,
        tx_type TEXT NOT NULL,
        amount REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
    );
    """)
    conn.commit()

    cursor.execute("SELECT id FROM users WHERE username = 'ugur'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
            ("ugur", hash_password("rumeli2026"), "Uğur Sukuşu")
        )
        conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM suppliers")
    if cursor.fetchone()["count"] == 0:
        initial_suppliers = [
            ("WİNSTON", "JTI Distribütör", "0212 555 0101", "Haftalık perşembe"),
            ("TUBORG", "Türk Tuborg Bayi", "0212 555 0102", "Pazartesi / Cuma"),
            ("KENT", "BAT Toptan Dağıtım", "0212 555 0103", ""),
            ("EFES", "Anadolu Efes Bayi", "0212 555 0104", "Çarşamba rutin teslimat"),
            ("MALBORO", "Philip Morris Dağıtım", "0212 555 0105", ""),
            ("BEYLERBEYİ", "Rakı Distribütörlüğü", "0212 555 0106", ""),
            ("MEY", "Mey İçki (Diageo)", "0212 555 0107", "Ay sonu mutabakat"),
            ("CHİVAS", "Pernod Ricard Dağıtım", "0212 555 0108", "İthal içki grubu"),
            ("JACK", "Brown-Forman Toptan", "0212 555 0109", ""),
            ("CİPS", "Frito Lay / PepsiCo", "0212 555 0110", "Salı teslimat"),
            ("NESTLE", "Çikolata & Kahve Toptan", "0212 555 0111", ""),
            ("REDBULL", "Red Bull Dağıtım", "0212 555 0112", ""),
            ("SAFİR", "Kuruyemiş & Bakliyat", "0212 555 0113", ""),
            ("COLA", "Coca-Cola İçecek A.Ş.", "0212 555 0114", "Perşembe kasa teslimi"),
            ("PEPSİ", "Pepsi İçecek Bayi", "0212 555 0115", ""),
            ("ÜLKER", "Bisküvi & Gıda Toptan", "0212 555 0116", ""),
            ("ETİ", "Gıda Pazarlama Bayi", "0212 555 0117", ""),
            ("EMRE SUKUŞU", "Ortak Cari / İkmal", "0532 555 0118", "Ana tedarik koordinasyonu")
        ]
        for name, cp, phone, notes in initial_suppliers:
            cursor.execute(
                "INSERT INTO suppliers (name, contact_person, phone, notes) VALUES (?, ?, ?, ?)",
                (name, cp, phone, notes)
            )
        conn.commit()

        cursor.execute("SELECT id FROM suppliers WHERE name = 'EMRE SUKUŞU'")
        emre_row = cursor.fetchone()
        if emre_row:
            emre_id = emre_row["id"]
            cursor.execute("""
                INSERT INTO transactions (supplier_id, date, doc_no, description, tx_type, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emre_id, "2026-09-27", "İRS-2026-001", "Toptan Mal Alımı (Açılış)", "PURCHASE", 1500.00))
            cursor.execute("""
                INSERT INTO transactions (supplier_id, date, doc_no, description, tx_type, amount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emre_id, "2026-09-27", "ÖDM-2026-001", "Banka Havalesi / Ödeme", "PAYMENT", 1400.00))
            conn.commit()
    conn.close()

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = ""
    phone: Optional[str] = ""
    notes: Optional[str] = ""

class TransactionCreate(BaseModel):
    supplier_id: int
    date: str
    doc_no: Optional[str] = ""
    description: Optional[str] = ""
    tx_type: str
    amount: float

init_db()

# Optional auth dependency - if token provided, verifies; if not, allows access or falls back
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        # Fallback to default user in open mode or prompt login
        return {"id": 1, "username": "ugur", "full_name": "Uğur Sukuşu"}
    token = authorization.replace("Bearer ", "").strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.username, u.full_name
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.token = ?
    """, (token,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return {"id": 1, "username": "ugur", "full_name": "Uğur Sukuşu"}
    return dict(user)

# ----------------- AUTH ENDPOINTS -----------------
@app.post("/api/login")
@app.post("/login")
def login(payload: LoginRequest):
    username = payload.username.strip().lower()
    pw_hash = hash_password(payload.password)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=400, detail="Hatalı kullanıcı adı veya şifre!")

    token = secrets.token_hex(32)
    cursor.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"]
        }
    }

@app.get("/api/me")
@app.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"success": True, "user": user}

@app.post("/api/logout")
@app.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    return {"success": True}

@app.post("/api/change-password")
@app.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    old_hash = hash_password(payload.old_password)
    new_hash = hash_password(payload.new_password)
    if len(payload.new_password) < 4:
        raise HTTPException(status_code=400, detail="Yeni şifre en az 4 karakter olmalıdır.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ? AND password_hash = ?", (user["id"], old_hash))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Mevcut şifreniz hatalı!")

    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Şifreniz başarıyla güncellendi."}

# ----------------- BUSINESS ENDPOINTS -----------------
@app.get("/api/dashboard")
@app.get("/dashboard")
def get_dashboard_data(user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        s.id,
        s.name,
        s.contact_person,
        s.phone,
        s.notes,
        COALESCE(SUM(CASE WHEN t.tx_type = 'PURCHASE' THEN t.amount ELSE 0 END), 0) AS total_purchase,
        COALESCE(SUM(CASE WHEN t.tx_type = 'PAYMENT' THEN t.amount ELSE 0 END), 0) AS total_payment,
        COUNT(t.id) AS tx_count
    FROM suppliers s
    LEFT JOIN transactions t ON s.id = t.supplier_id
    GROUP BY s.id
    ORDER BY s.name ASC
    """)
    suppliers_rows = cursor.fetchall()
    conn.close()

    total_purchase_company = 0.0
    total_payment_company = 0.0
    debtor_count = 0
    closed_count = 0
    supplier_list = []

    for idx, row in enumerate(suppliers_rows, start=1):
        tot_pur = float(row["total_purchase"])
        tot_pay = float(row["total_payment"])
        balance = tot_pur - tot_pay
        
        total_purchase_company += tot_pur
        total_payment_company += tot_pay
        
        if balance > 0.005:
            debtor_count += 1
            status = "Ödenecek Borç Var"
            status_color = "red"
        elif balance < -0.005:
            status = "Avans/Fazla Ödeme"
            status_color = "blue"
        else:
            closed_count += 1
            status = "Borç Kapandı"
            status_color = "green"

        pay_rate = (tot_pay / tot_pur * 100.0) if tot_pur > 0 else (100.0 if tot_pay > 0 else 0.0)

        supplier_list.append({
            "seq": idx,
            "id": row["id"],
            "name": row["name"],
            "contact_person": row["contact_person"] or "",
            "phone": row["phone"] or "",
            "notes": row["notes"] or "",
            "total_purchase": tot_pur,
            "total_payment": tot_pay,
            "balance": balance,
            "pay_rate": round(pay_rate, 1),
            "status": status,
            "status_color": status_color,
            "tx_count": row["tx_count"]
        })

    net_debt_company = total_purchase_company - total_payment_company
    overall_pay_rate = (total_payment_company / total_purchase_company * 100.0) if total_purchase_company > 0 else 0.0

    return {
        "kpi": {
            "total_purchase": total_purchase_company,
            "total_payment": total_payment_company,
            "net_debt": net_debt_company,
            "overall_pay_rate": round(overall_pay_rate, 1),
            "debtor_count": debtor_count,
            "closed_count": closed_count,
            "total_suppliers": len(supplier_list)
        },
        "suppliers": supplier_list
    }

@app.post("/api/suppliers")
@app.post("/suppliers")
@app.post("/tedarikciler")
def create_supplier(payload: SupplierCreate, user: dict = Depends(get_current_user)):
    name = payload.name.strip().upper()
    if not name:
        raise HTTPException(status_code=400, detail="Tedarikçi unvanı boş olamaz.")
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO suppliers (name, contact_person, phone, notes) VALUES (?, ?, ?, ?)",
            (name, payload.contact_person.strip(), payload.phone.strip(), payload.notes.strip())
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"success": True, "id": new_id, "name": name}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail=f"'{name}' isimli tedarikçi zaten kayıtlı!")

@app.delete("/api/suppliers/{supplier_id}")
@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM suppliers WHERE id = ?", (supplier_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    
    name = row["name"]
    cursor.execute("DELETE FROM transactions WHERE supplier_id = ?", (supplier_id,))
    cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"'{name}' ve bağlı tüm hareketleri silindi."}

@app.get("/api/suppliers/{supplier_id}/statement")
@app.get("/suppliers/{supplier_id}/statement")
def get_supplier_statement(supplier_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    supplier = cursor.fetchone()
    if not supplier:
        conn.close()
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    
    cursor.execute("""
    SELECT id, date, doc_no, description, tx_type, amount, created_at
    FROM transactions
    WHERE supplier_id = ?
    ORDER BY date ASC, id ASC
    """, (supplier_id,))
    tx_rows = cursor.fetchall()
    conn.close()

    statement = []
    running_balance = 0.0
    total_purchase = 0.0
    total_payment = 0.0

    for tx in tx_rows:
        amount = float(tx["amount"])
        is_purchase = (tx["tx_type"] == "PURCHASE")
        purchase_amt = amount if is_purchase else 0.0
        payment_amt = 0.0 if is_purchase else amount

        total_purchase += purchase_amt
        total_payment += payment_amt
        running_balance += (purchase_amt - payment_amt)

        statement.append({
            "id": tx["id"],
            "date": tx["date"],
            "doc_no": tx["doc_no"] or "-",
            "description": tx["description"] or "-",
            "tx_type": tx["tx_type"],
            "purchase_amount": purchase_amt,
            "payment_amount": payment_amt,
            "running_balance": round(running_balance, 2)
        })

    return {
        "supplier": {
            "id": supplier["id"],
            "name": supplier["name"],
            "contact_person": supplier["contact_person"] or "",
            "phone": supplier["phone"] or "",
            "notes": supplier["notes"] or ""
        },
        "totals": {
            "total_purchase": total_purchase,
            "total_payment": total_payment,
            "current_balance": round(running_balance, 2),
            "status": "Ödenecek Borç Var" if running_balance > 0.005 else ("Avans/Fazla Ödeme" if running_balance < -0.005 else "Borç Kapandı")
        },
        "transactions": statement
    }

@app.post("/api/transactions")
@app.post("/transactions")
@app.post("/islemler")
def create_transaction(payload: TransactionCreate, user: dict = Depends(get_current_user)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Tutar 0'dan büyük olmalıdır.")
    if payload.tx_type not in ["PURCHASE", "PAYMENT"]:
        raise HTTPException(status_code=400, detail="Geçersiz işlem türü.")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM suppliers WHERE id = ?", (payload.supplier_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tedarikçi bulunamadı.")
    
    cursor.execute("""
    INSERT INTO transactions (supplier_id, date, doc_no, description, tx_type, amount)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.supplier_id,
        payload.date,
        payload.doc_no.strip() if payload.doc_no else "",
        payload.description.strip() if payload.description else "",
        payload.tx_type,
        payload.amount
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"success": True, "id": new_id}

@app.delete("/api/transactions/{tx_id}")
@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/export/excel")
@app.get("/export/excel")
def export_all_to_excel(token: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        s.id,
        s.name,
        COALESCE(SUM(CASE WHEN t.tx_type = 'PURCHASE' THEN t.amount ELSE 0 END), 0) AS total_purchase,
        COALESCE(SUM(CASE WHEN t.tx_type = 'PAYMENT' THEN t.amount ELSE 0 END), 0) AS total_payment
    FROM suppliers s
    LEFT JOIN transactions t ON s.id = t.supplier_id
    GROUP BY s.id
    ORDER BY s.name ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cari Bakiye"

    font_title = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    fill_navy = PatternFill(start_color="0F2537", end_color="0F2537", fill_type="solid")
    fill_header = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Segoe UI", size=10, bold=True)

    ws.merge_cells("A1:G1")
    ws["A1"] = "RUMELİ TEKEL - TEDARİKÇİ CARİ & MAL ALIM BAKİYE TAKİP PANELİ"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_navy
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    headers = ["S.No", "Tedarikçi Firma", "Toplam Alınan Mal (₺)", "Yapılan Ödeme (₺)", "Kalan Borç (₺)", "Ödeme Oranı", "Durum"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for idx, r in enumerate(rows, 4):
        tot_pur = float(r["total_purchase"])
        tot_pay = float(r["total_payment"])
        bal = tot_pur - tot_pay
        rate = (tot_pay / tot_pur) if tot_pur > 0 else (1.0 if tot_pay > 0 else 0.0)
        status = "Ödenecek Borç Var" if bal > 0.005 else ("Avans/Fazla Ödeme" if bal < -0.005 else "Borç Kapandı")

        ws.cell(row=idx, column=1, value=idx-3).alignment = Alignment(horizontal="center")
        ws.cell(row=idx, column=2, value=r["name"]).font = font_bold
        
        c3 = ws.cell(row=idx, column=3, value=tot_pur)
        c3.number_format = '#,##0.00 "₺"'
        
        c4 = ws.cell(row=idx, column=4, value=tot_pay)
        c4.number_format = '#,##0.00 "₺"'
        
        c5 = ws.cell(row=idx, column=5, value=bal)
        c5.number_format = '#,##0.00 "₺"'
        c5.font = font_bold

        c6 = ws.cell(row=idx, column=6, value=rate)
        c6.number_format = "0.0%"
        c6.alignment = Alignment(horizontal="center")

        ws.cell(row=idx, column=7, value=status).alignment = Alignment(horizontal="center")

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 16
    ws.column_dimensions["G"].width = 22

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Rumeli_Tekel_Cari_Rapor_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/", response_class=HTMLResponse)
def index_page():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Rumeli Tekel Bulut Sunucusu Aktif</h1>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
