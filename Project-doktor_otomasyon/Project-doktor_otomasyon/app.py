from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="tunahan123", #mysqldeki parola
        database="doktor_otomasyon",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return redirect(url_for('ana_menu'))

@app.route('/ana_menu')
def ana_menu():
    return render_template('ana_menu.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# HASTA KAYIT SAYFASI
@app.route('/hasta_kayit_sayfasi')
def hasta_kayit_sayfasi():
    return render_template('hasta_kayit.html')

@app.route('/hasta_kayit', methods=['POST'])
def hasta_kayit():
    ad = request.form['ad']
    soyad = request.form['soyad']
    tc = request.form['tc']
    telefon = request.form['telefon']
    dogum = request.form['dogum']
    sifre = request.form['sifre']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Hasta (Ad, Soyad, TC, Telefon, DogumTarihi, Sifre)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ad, soyad, tc, telefon, dogum, sifre))
    con.commit()
    con.close()
    return redirect(url_for('ana_menu'))

# HASTA LİSTELEME ve SİLME
@app.route('/hastalar')
def hastalari_listele():
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("SELECT * FROM Hasta ORDER BY HastaID DESC")
        hastalar = cursor.fetchall()
    con.close()
    return render_template('hasta_listele.html', hastalar=hastalar)

@app.route('/hasta_sil/<int:hasta_id>')
def hasta_sil(hasta_id):
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("DELETE FROM Hasta WHERE HastaID = %s", (hasta_id,))
    con.commit()
    con.close()
    return redirect(url_for('hastalari_listele'))

# HASTA GİRİŞ ve MENÜ
@app.route('/hasta_giris_sayfasi')
def hasta_giris_sayfasi():
    return render_template('hasta_giris.html')

@app.route('/hasta_giris', methods=['POST'])
def hasta_giris():
    tc = request.form['tc']
    sifre = request.form['sifre']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("SELECT * FROM Hasta WHERE TC=%s AND Sifre=%s", (tc, sifre))
        hasta = cursor.fetchone()
    con.close()
    if hasta:
        session['rol'] = 'hasta'
        session['id'] = hasta['HastaID']
        session['ad'] = hasta['Ad']
        return redirect(url_for('hasta_menu'))
    return "Giriş başarısız. <a href='/hasta_giris_sayfasi'>Geri dön</a>"

@app.route('/hasta_menu')
def hasta_menu():
    if session.get('rol') == 'hasta':
        return render_template('hasta_menu.html')
    return redirect('/')

# HASTA RANDEVU ALMA
@app.route('/randevu_al_sayfasi')
def randevu_al_sayfasi():
    if session.get('rol') == 'hasta':
        con = get_connection()
        with con.cursor() as cursor:
            cursor.execute("SELECT DoktorID, Ad, Soyad FROM Doktor")
            doktorlar = cursor.fetchall()
        con.close()
        return render_template('randevu_al.html', doktorlar=doktorlar)
    return redirect('/')

@app.route('/randevu_al', methods=['POST'])
def randevu_al():
    if session.get('rol') != 'hasta':
        return redirect('/')
    hasta_id = session['id']
    doktor_id = request.form['doktor_id']
    tarih = request.form['tarih']
    sikayet = request.form['sikayet']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Randevu (HastaID, DoktorID, Tarih, Sikayet)
            VALUES (%s, %s, %s, %s)
        """, (hasta_id, doktor_id, tarih, sikayet))
    con.commit()
    con.close()
    return redirect(url_for('hasta_menu'))

@app.route('/randevu_iptal/<int:randevu_id>')
def randevu_iptal(randevu_id):
    if session.get('rol') != 'hasta':
        return redirect('/')

    con = get_connection()
    with con.cursor() as cursor:
        # Bu randevuya ait muayene var mı?
        cursor.execute("SELECT * FROM Muayene WHERE RandevuID = %s", (randevu_id,))
        muayene = cursor.fetchone()

        if muayene:
            con.close()
            return "❌ Bu randevuya ait muayene yapılmış. İptal edilemez. <a href='/randevular_sayfasi'>Geri dön</a>"

        # Muayene yoksa sil
        cursor.execute("DELETE FROM Randevu WHERE RandevuID = %s AND HastaID = %s",
                       (randevu_id, session['id']))
    con.commit()
    con.close()
    return redirect(url_for('randevular_sayfasi'))

# HASTA RANDEVULARINI GÖRÜNTÜLEME
@app.route('/randevular_sayfasi')
def randevular_sayfasi():
    if session.get('rol') != 'hasta':
        return redirect('/')
    hasta_id = session['id']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            SELECT r.RandevuID, r.Tarih, r.Sikayet,
                   d.Ad AS DoktorAd, d.Soyad AS DoktorSoyad
            FROM Randevu r
            JOIN Doktor d ON r.DoktorID = d.DoktorID
            WHERE r.HastaID = %s
            ORDER BY r.Tarih DESC
        """, (hasta_id,))
        randevular = cursor.fetchall()
    con.close()
    return render_template('randevular.html', randevular=randevular)

# HASTA MUAYENE GEÇMİŞİ
@app.route('/muayene_gecmisi_sayfasi')
def muayene_gecmisi_sayfasi():
    if session.get('rol') != 'hasta':
        return redirect('/')
    hasta_id = session['id']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            SELECT m.MuayeneID, r.Tarih,
                   d.Ad AS DoktorAd, d.Soyad AS DoktorSoyad,
                   m.Teshis, m.Ilac, m.Notlar
            FROM Muayene m
            JOIN Randevu r ON m.RandevuID = r.RandevuID
            JOIN Doktor d ON r.DoktorID = d.DoktorID
            WHERE r.HastaID = %s
            ORDER BY r.Tarih DESC
        """, (hasta_id,))
        muayeneler = cursor.fetchall()
    con.close()
    return render_template('muayene_gecmisi.html', muayeneler=muayeneler)

# DOKTOR GİRİŞ
@app.route('/doktor_giris_sayfasi')
def doktor_giris_sayfasi():
    return render_template('doktor_giris.html')

@app.route('/doktor_giris', methods=['POST'])
def doktor_giris():
    email = request.form['email']
    sifre = request.form['sifre']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("SELECT * FROM Doktor WHERE Email=%s AND Sifre=%s", (email, sifre))
        doktor = cursor.fetchone()
    con.close()
    if doktor:
        session['rol'] = 'doktor'
        session['id'] = doktor['DoktorID']
        session['ad'] = doktor['Ad']
        return redirect(url_for('doktor_menu'))
    return "Giriş başarısız. <a href='/doktor_giris_sayfasi'>Geri dön</a>"

# DOKTOR MENÜ
@app.route('/doktor_menu')
def doktor_menu():
    if session.get('rol') == 'doktor':
        return render_template('doktor_menu.html')
    return redirect('/')

# DOKTORUN RANDEVULARI
@app.route('/doktor_randevular_sayfasi')
def doktor_randevular_sayfasi():
    if session.get('rol') != 'doktor':
        return redirect('/')
    doktor_id = session['id']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            SELECT r.RandevuID, r.Tarih, r.Sikayet,
                   h.Ad AS HastaAd, h.Soyad AS HastaSoyad
            FROM Randevu r
            JOIN Hasta h ON r.HastaID = h.HastaID
            WHERE r.DoktorID = %s AND r.MuayeneDurumu = 0
            ORDER BY r.Tarih DESC
        """, (doktor_id,))
        randevular = cursor.fetchall()
    con.close()
    return render_template('doktor_randevular.html', randevular=randevular)

# MUAYENE GİRİŞİ
@app.route('/muayene_girisi_sayfasi')
def muayene_girisi_sayfasi():
    if session.get('rol') != 'doktor':
        return redirect('/')
    return render_template('muayene_girisi.html')

@app.route('/muayene_girisi', methods=['POST'])
def muayene_girisi():
    if session.get('rol') != 'doktor':
        return redirect('/')
    randevu_id = request.form['randevu_id']
    teshis = request.form['teshis']
    ilac = request.form['ilac']
    notlar = request.form['notlar']
    con = get_connection()
    with con.cursor() as cursor:
        # Muayene kaydı ekle
        cursor.execute("""
            INSERT INTO Muayene (RandevuID, Teshis, Ilac, Notlar)
            VALUES (%s, %s, %s, %s)
        """, (randevu_id, teshis, ilac, notlar))

        # Randevu durumu güncelle
        cursor.execute("""
            UPDATE Randevu SET MuayeneDurumu = 1 WHERE RandevuID = %s
        """, (randevu_id,))
    con.commit()
    con.close()
    return redirect(url_for('doktor_menu'))

# DOKTORUN MUAYENE GEÇMİŞİ
@app.route('/doktor_muayeneler_sayfasi')
def doktor_muayeneler_sayfasi():
    if session.get('rol') != 'doktor':
        return redirect('/')
    doktor_id = session['id']
    con = get_connection()
    with con.cursor() as cursor:
        cursor.execute("""
            SELECT m.MuayeneID, r.Tarih,
                   h.Ad AS HastaAd, h.Soyad AS HastaSoyad,
                   m.Teshis, m.Ilac, m.Notlar
            FROM Muayene m
            JOIN Randevu r ON m.RandevuID = r.RandevuID
            JOIN Hasta h ON r.HastaID = h.HastaID
            WHERE r.DoktorID = %s
            ORDER BY r.Tarih DESC
        """, (doktor_id,))
        muayeneler = cursor.fetchall()
    con.close()
    return render_template('doktor_muayeneler.html', muayeneler=muayeneler)

if __name__ == '__main__':
    app.run(debug=True)
