import pygame
import random
import os
import time
pygame.init()
pygame.font.init()
beyaz = (255,255,255)
EN = 750
BOY = 750
ekran = pygame.display.set_mode((EN, BOY))
pygame.display.set_caption("Koddunyam.net Space Oyunu")

# Resimler Ucaklar
MAVI_UCAK = pygame.image.load("pixel_ship_blue_small.png")
YESIL_UCAK = pygame.image.load("pixel_ship_green_small.png")
KIRMIZI_UCAK = pygame.image.load("pixel_ship_red_small.png")
SARI_UCAK = pygame.image.load("pixel_ship_yellow.png")
# Resimler Laserler
MAVI_LAZER = pygame.image.load("pixel_laser_blue.png")
YESIL_LAZER = pygame.image.load("pixel_laser_green.png")
KIRMIZI_LAZER = pygame.image.load("pixel_laser_red.png")
SARI_LAZER = pygame.image.load("pixel_laser_yellow.png")

# Arkaplan
Arka_Plan_Resmi = pygame.image.load("arkaplan.jpeg")
BG = pygame.transform.scale(Arka_Plan_Resmi,(EN, BOY))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, ekran):
        ekran.blit(self.img, (self.x, self.y))

    def hareket(self, ivme):
        self.y += ivme

    def ekran_disi(self, yukseklik):
        return not(self.y <= yukseklik and self.y >= 0)

    def carpisma(self, obj):
        return carpisma(self, obj)

class Ucak:
    DOLUMSURESI = 30
    def __init__(self, x, y, can=100):
        self.x = x
        self.y = y
        self.can = can
        self.ucak_resim = None
        self.lazer_resim = None
        self.lazerler = []
        self.lazer_suresi = 0

    def draw(self, ekran):
        ekran.blit(self.ucak_resim, (self.x, self.y))
        for lazer in self.lazerler:
            lazer.draw(ekran)

    def dolum_suresi(self):
        if self.lazer_suresi >= self.DOLUMSURESI:
            self.lazer_suresi = 0
        elif self.lazer_suresi > 0:
            self.lazer_suresi += 1

    def lazer_hareket(self, ivme, obj):
        self.dolum_suresi()
        for lazer in self.lazerler:
            lazer.hareket(ivme)
            if lazer.ekran_disi(BOY):
                self.lazerler.remove(lazer)
            elif lazer.carpisma(obj):
                obj.can -= 10
                self.lazerler.remove(lazer)

    def ates_et(self):
        if self.lazer_suresi == 0:
            lazer = Laser(self.x,self.y, self.lazer_resim)
            self.lazerler.append(lazer)
            self.lazer_suresi = 1

    def boy_bilgi(self):
        return self.ucak_resim.get_height()

    def en_bilgi(self):
        return self.ucak_resim.get_width()

class Dusman(Ucak):
    DUSMAN_LISTESI = { "kirmizi": (KIRMIZI_UCAK, KIRMIZI_LAZER),
                       "mavi": (MAVI_UCAK, MAVI_LAZER),
                       "yesil": (YESIL_UCAK, YESIL_LAZER)}
    def __init__(self, x, y, renk, can=100):
        super().__init__(x, y, can)
        self.ucak_resim, self.lazer_resim = self.DUSMAN_LISTESI[renk]
        self.mask = pygame.mask.from_surface(self.ucak_resim)

    def hareket(self, ivme):
        self.y += ivme

    def ates_et(self):
        if self.lazer_suresi == 0:
            lazer = Laser(self.x, self.y +20,self.lazer_resim)
            self.lazerler.append(lazer)
            self.lazer_suresi = 1

class Oyuncu(Ucak):
    def __init__(self, x, y, can=100):
        super().__init__(x, y, can)
        self.ucak_resim = SARI_UCAK
        self.lazer_resim = SARI_LAZER
        self.mask = pygame.mask.from_surface(self.ucak_resim)
        self.max_can = can

    def lazer_hareket(self, ivme, objler):
        self.dolum_suresi()
        for lazer in self.lazerler:
            lazer.hareket(ivme)
            if lazer.ekran_disi(BOY):
                self.lazerler.remove(lazer)
            else:
                for obj in objler:
                    if lazer.carpisma(obj):
                        objler.remove(obj)
                        if lazer in self.lazerler:
                            self.lazerler.remove(lazer)


    def draw(self, ekran):
        super().draw(ekran)
        self.can_bar(ekran)

    def can_bar(self, ekran):
        pygame.draw.rect(ekran, (255,0,0), (self.x, self.y + self.ucak_resim.get_height()+10, self.ucak_resim.get_width(),10))
        pygame.draw.rect(ekran,(0,255,0), (self.x, self.y + self.ucak_resim.get_height()+10, self.ucak_resim.get_width() * (self.can/self.max_can),10))

def carpisma(obj1, obj2):
    fark_x = obj2.x - obj1.x
    fark_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (fark_x,fark_y)) != None

def Oyunu_Baslat():
    basla = True
    FPS = 60
    level = 0
    can = 5
    ana_font = pygame.font.SysFont("Arial", 50)
    kaybet_font = pygame.font.SysFont("Arial", 60)
    dusmanlar = []
    dalga = 5
    dusman_ivmesi = 1
    oyuncu_ivmesi = 4
    lazer_ivmesi = 5
    oyuncu = Oyuncu(350,650)
    clock = pygame.time.Clock()
    kaybet = False
    kaybetme_sayac = 0

    def ekran_olustur():
        ekran.blit(Arka_Plan_Resmi,(0,0))
        #Yazilar:
        can_yazisi = ana_font.render(f"Can: {can}", 1, beyaz)
        bolum_yazisi = ana_font.render(f"Bölüm: {level}", 1, beyaz)
        ekran.blit(can_yazisi, (10,10))
        ekran.blit(bolum_yazisi, (EN - bolum_yazisi.get_width() - 10,10))

        for dusman in dusmanlar:
            dusman.draw(ekran)

        oyuncu.draw(ekran)

        if kaybet:
            kaybet_yazisi = kaybet_font.render("SENI EZIK!", 1, beyaz)
            ekran.blit(kaybet_yazisi, (EN/2 -kaybet_yazisi.get_width(), BOY/2 - kaybet_yazisi.get_height()))
        pygame.display.update()

    while basla:
        clock.tick(FPS)
        ekran_olustur()

        if can <= 0 or oyuncu.can <= 0:
            kaybet = True
            kaybetme_sayac += 1

        if kaybet:
            if kaybetme_sayac > FPS *3:
                basla = False
            else:
                continue

        if len(dusmanlar) == 0:
            level += 1
            dalga += 3
            for i in range(dalga):
                dusman = Dusman(random.randrange(50, EN - 50), random.randrange(-1000,-100), random.choice(["kirmizi", "mavi", "yesil"]))
                dusmanlar.append(dusman)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        tuslar = pygame.key.get_pressed()
        if tuslar[pygame.K_a] and oyuncu.x - oyuncu_ivmesi > 0:
            oyuncu.x -= oyuncu_ivmesi
        if tuslar[pygame.K_d] and oyuncu.x - oyuncu_ivmesi < EN:
            oyuncu.x += oyuncu_ivmesi
        if tuslar[pygame.K_w] and oyuncu.y - oyuncu_ivmesi > 0:
            oyuncu.y -= oyuncu_ivmesi
        if tuslar[pygame.K_s] and oyuncu.y - oyuncu_ivmesi < BOY:
            oyuncu.y += oyuncu_ivmesi
        if tuslar[pygame.K_SPACE]:
            oyuncu.ates_et()

        for dusman in dusmanlar[:]:
            dusman.hareket(dusman_ivmesi)
            dusman.lazer_hareket(lazer_ivmesi, oyuncu)
            if random.randrange(0,120) == 1:
                dusman.ates_et()

            if carpisma(dusman, oyuncu):
                oyuncu.can -= 10
                dusmanlar.remove(dusman)
            elif dusman.y + dusman.boy_bilgi() > BOY:
                can -= 1
                dusmanlar.remove(dusman)

        oyuncu.lazer_hareket(-lazer_ivmesi, dusmanlar)


def Menu():
    baslik_font = pygame.font.SysFont("Arial", 45)
    basla = True
    while basla:
        ekran.blit(Arka_Plan_Resmi, (0,0))
        baslik_yazisi = baslik_font.render("Oyunu baslatmak icin tikla..",1,(255,0,0))
        ekran.blit(baslik_yazisi, (EN/2- baslik_yazisi.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                basla = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                Oyunu_Baslat()
    pygame.quit()

Menu()