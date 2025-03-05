#web sitesi üzerindeki isteklerimizi yönetmesi için requests kütüphanesini import ediyoruz
#web deki verileri çekmesi için bs4 kütüphanesinden BeautifulSoup'ı import ediyoruz
#veritabanı işlemleri için sqlite3 kütüphanesini import ediyoruz
import requests
from bs4 import BeautifulSoup
import sqlite3

# Veritabanı bağlantısını oluşturduk
conn = sqlite3.connect('maskara.db')
cursor = conn.cursor()

# Veritabanında tablo oluşturduk
cursor.execute('''
    CREATE TABLE IF NOT EXISTS maskara (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT,
        yorumsayisi INTEGER,
        urunyildiz REAL,
        adsoyad TEXT,
        yorum TEXT,
        yorumyildiz INTEGER,
        tarih TEXT,
        fiyat REAL
    )'''
)

# Bağlantıyı onayladık
conn.commit()

# Url adresimize gidiyoruz
urlUrn = "https://www.cosmetica.com.tr"
urnName="maskara"

# Web sitesine GET isteği gönderiyoruz
response = requests.get(urlUrn+"/"+urnName)

# Eğer istek başarılıysa devam ediyoruz
if response.status_code == 200:

    # HTML içeriğini analiz etmek için BeautifulSoup kullanıyoruz
    soup = BeautifulSoup(response.text, "html.parser")
    pageNumber = soup.find_all("a", class_="paging")

    # Liste uzunluğunu kontrol ediyoruz
    if len(pageNumber) > 1:
        # Son index'teki data hangi sayfa numarasında olduğumuzu söylediği için -2 kullandık
        pageNumber = pageNumber[len(pageNumber)-2].text
    else:
        # Hata mesajı veya alternatif işlem
        print("Yeterli sayfa numarası bulunamadı.")
        pageNumber = 1  # Alternatif olarak 1. sayfa ile devam edebiliriz

    # Sayfa sayısı kadar döngüyü dönüyoruz
    pageCount = 1
    while(pageCount <= int(pageNumber)):
        response = requests.get(urlUrn +"/"+urnName + "?o=3&page=" + str(pageCount))
        pageCount = pageCount+1
        # Ürün linklerini içeren HTML öğelerini buluyoruz
        soup = BeautifulSoup(response.text, "html.parser")
        product_links = soup.find_all("a", class_="loadedImg")
        product_links = soup.find('div', class_='urnList')

        if product_links is None:
            print("Ürün bulunamadı")
            continue
        
        urn = product_links.findAll('li')

        # Ürün linklerini döngüye sokuyoruz yıldız değerini, yorum sayısını ve fiyatını çekiyoruz
        for link in urn:
            print("ürün")
            asd = link.find('a')
            print(asd.get("href"))
            title = link.find('div', class_='urunListe_ratingbar star-rating')
            if (title == None):
                print("ürünün ortalama yıldız değeri ve yorumu yok")
                print("-------------------")
                continue
            print("ürünün yıldız değeri %", title.get('title'))
            yrmCount = link.find('div', class_='urunListe_yorumSayi')
            number = yrmCount.get_text().split('(')[1].split(')')[0]
            print("ürünün yorum sayısı", number)
            price = link.find('div', class_='urunListe_satisFiyat')
            pricee = price.get_text().split(' ')[0]
            print(pricee + " TL ürünün fiyatı")
            print("---------")

            # Ürün linkine gidiyoruz ve gerekli bilgileri çekiyoruz
            requestUrnUrl = urlUrn + asd.get("href")
            responseUrn = requests.get(requestUrnUrl)
            soupUrn = BeautifulSoup(responseUrn.text, "html.parser")
            urnYrm = soupUrn.findAll("div", class_="tableYorumListe_yorumMesaj")
            yrmYldz = soupUrn.findAll("div", class_="tableYorumListe_yorumPuan emos_invisible")
            yrmAdsoyad = soupUrn.findAll("div", class_="tableYorumListe_yorumAdSoyad")
            yrmTarih = soupUrn.findAll("div", class_="tableYorumListe_yorumTarih")

            # Yorum sayısını eğer sıfır değilse döngüye sokuyoruz ve yorumlarla birlikte diğer bilgileri çekiyoruz
            i = 0
            while(i!=len(urnYrm)):
                print("yorum yapan kişi")
                print(yrmAdsoyad[i].text)
                print("yorumu")
                print(urnYrm[i].text)
                print("verdiği yıldız değeri")
                print(yrmYldz[i].text)
                print("yorum yaptığı tarih")
                print(yrmTarih[i].text)
                print("------------------------------------------------")

                # Veritabanına ürün bilgilerini kaydediyoruz yorum sayısı sıfır ise kaydetmiyoruz
                cursor.execute('INSERT INTO maskara (adsoyad, yorum, yorumsayisi, yorumyildiz, urunyildiz, tarih, link, fiyat) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (yrmAdsoyad[i].text, urnYrm[i].text, number, yrmYldz[i].text, float(title.get('title').replace(',' , '.')), yrmTarih[i].text, requestUrnUrl, pricee))
                conn.commit()

                # Bir sonraki yorum için i'yi bir arttırıyoruz
                i=i+1

    # En yüksek yıldız puanına sahip ürünü bulduruyoruz
    cursor.execute('SELECT link, yorumsayisi,urunyildiz FROM maskara ORDER BY urunyildiz DESC LIMIT 1')
    en_yuksek_yildizli_urun = cursor.fetchone()

    # En çok yorum sayısına sahip ürünü bulduruyoruz
    cursor.execute('SELECT link, yorumsayisi,urunyildiz FROM maskara ORDER BY yorumsayisi DESC LIMIT 1')
    en_cok_yorumlu_urun = cursor.fetchone()

    # Sonuçları ekrana yazdırıyoruz
    print("En yüksek yıldız puanına sahip ürün")
    print(en_yuksek_yildizli_urun)
    print("En çok yorum sayısına sahip ürün")
    print(en_cok_yorumlu_urun)

    # Veritabanı bağlantısını kapatıyoruz
    conn.close()

# Eğer istek başarısızsa hata kodunu ekrana yazdırıyoruz
else:
    print(f"Error: {response.status_code}")