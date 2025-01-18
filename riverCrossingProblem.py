import threading
import time

class BoatCrossing:
    def __init__(self, capacity):
        self.boat_capacity = threading.Semaphore(capacity)  # Kayığın kapasitesi
        self.mutex = threading.Lock()  # Genel kontrol için kilit
        self.turn = "Kuzey"  # İlk geçiş sırası kuzeyde
        self.kuzey_sayac = 0  # Kuzeyden geçiş sayacı
        self.guney_sayac = 0  # Güneyden geçiş sayacı
        self.max_turns = capacity  # Maksimum ardışık geçiş limiti
        self.kuzey_sira = threading.Semaphore(0)  # Kuzey kuyruğu
        self.guney_sira = threading.Semaphore(0)  # Güney kuyruğu
        self.waiting_kuzey = 0  # Kuzeyde bekleyen kişi sayısı
        self.waiting_guney = 0  # Güneyde bekleyen kişi sayısı

    def cross(self, start, end):
        print(f"{start} tarafındaki biri kayıkla {end} tarafına geçiyor...")
        time.sleep(1)  # Geçiş süresini simüle etmek için bekle
        print(f"{start} tarafındaki biri kayıkla {end} tarafına geçişini tamamladı.")

    def kuzeyden_guneye(self):
        with self.mutex:
            self.waiting_kuzey += 1
            # Kuzey sırası değilse kuyruğa geç veya max kapasiteyi aştıysan kuyruğa geç
            while self.turn != "Kuzey" or self.kuzey_sayac >= self.max_turns:
                self.mutex.release()
                self.kuzey_sira.acquire()
                self.mutex.acquire()

            # Kayıkta yer varsa geçiş yap
            self.waiting_kuzey -= 1
            self.kuzey_sayac += 1
            self.boat_capacity.acquire()
            

        self.cross("Kuzey", "Guney")
        self.boat_capacity.release()

        with self.mutex:
            # Eğer maksimum geçişe ulaşıldıysa veya tüm kuzeydekiler geçtiyse, sırayı değiştir
            if self.kuzey_sayac >= self.max_turns or self.waiting_kuzey == 0:
                self.kuzey_sayac = 0
                self.turn = "Guney"
                # Güneyde bekleyenleri uyandır
                for _ in range(self.waiting_guney):
                    self.guney_sira.release()

    def guneyden_kuzeye(self):
        with self.mutex:
            self.waiting_guney += 1
            # Güney sırası değilse kuyruğa geç veya max kapasiteyi aştıysan kuyruğa geç
            while self.turn != "Guney" or self.guney_sayac >= self.max_turns:
                self.mutex.release()
                self.guney_sira.acquire()
                self.mutex.acquire()

            # Kayıkta yer varsa geçiş yap
            self.waiting_guney -= 1
            self.guney_sayac += 1
            self.boat_capacity.acquire()
            

        self.cross("Guney", "Kuzey")
        self.boat_capacity.release()

        with self.mutex:
            # Eğer maksimum geçişe ulaşıldıysa veya tüm güneydekiler geçtiyse, sırayı değiştir
            if self.guney_sayac >= self.max_turns or self.waiting_guney == 0:
                self.guney_sayac = 0
                self.turn = "Kuzey"
                # Kuzeyde bekleyenleri uyandır
                for _ in range(self.waiting_kuzey):
                    self.kuzey_sira.release()

# Simülasyon
if __name__ == "__main__":
    boat = BoatCrossing(capacity=7)  # Kapasite: 3, Maksimum geçiş: 3
    threads = []

    # Kuzey ve güneyden gelen kişiler
    for _ in range(10):  # 5 kişi her iki yönden
        threads.append(threading.Thread(target=boat.kuzeyden_guneye))
        threads.append(threading.Thread(target=boat.guneyden_kuzeye))

    # Tüm thread'leri başlat
    for t in threads:
        t.start()

    # Tüm thread'lerin tamamlanmasını bekle
    for t in threads:
        t.join()

    print("Kayık geçişi simülasyonu tamamlandı!")
