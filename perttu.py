# Wordle-botti Perttu. Mikrobitti & Simo Sahla 2022.

import random
from copy import deepcopy


# Perttu-luokan ulkopuolella määritellään metodi, lataa sanat tekstitiedostosta – yksi sana
# per rivi – ja palauttaa sanan pituuden sekä sanat joukkona (set).
def lataa_sanasto(tiedostonimi):
    sanasto = set(line.strip() for line in open(tiedostonimi))
    # Napataan sanastosta yksi sana sen pituuden mittaamiseksi:
    sanan_pituus = 0
    for sana in sanasto:
        sanan_pituus = len(sana)
        break
    return sanasto, sanan_pituus


class Perttu:

    # Alustukseen ja sanaston käsittelyyn liittyvät metodit

    # Alustusmetodi ottaa parametrinaan tiedoston, josta pohjasanasto luetaan.
    def __init__(self, tiedostonimi):
        self.vokaalit = set('aeiouy')  # Kirjaimet, joista ainakin yhden on esiinnyttävä sanassa
        self.hylatyt = set()           # Hylättyjen ehdotusten joukko
        self.mahdolliset = []          # Lista, jossa pidetään kirjaa mahdollisista kirjaimista kussakin paikassa
        # Ladataan pohjasanasto ja lasketaan siitä arvailuun käytettävät tiedot.
        self.sanasto, self.sanan_pituus = lataa_sanasto(tiedostonimi)
        self.aakkoset = self.luo_aakkoset()
        for i in range(0, self.sanan_pituus):
            self.mahdolliset.append(deepcopy(self.aakkoset))
        self.kirjainparit = self.luo_kirjainparitaulukko()
        self.esiintymiskerrat = self.laske_esiintymiskerrat()
        self.kirjainarvonta = self.luo_arvontataulukko(self.esiintymiskerrat)

    # Tämä metodi määrittelee sanaston pohjalta käytettävät aakkoset eli listaa kirjaimet, joita sanoissa esiintyy.
    def luo_aakkoset(self):
        aakkoset = set()
        for sana in self.sanasto:
            for kirjain in sana:
                if kirjain not in aakkoset:
                    aakkoset.add(kirjain)
        return aakkoset

    # Tämä metodi luo kirjainparien esiintymiskerroista taulukon, jota käytetään kirjainparipisteiden laskemisessa.
    def luo_kirjainparitaulukko(self):
        # Luodaan lista kaikista mahdollisista kirjainpareista:
        kaikki_kirjainparit = []
        for k1 in self.aakkoset:
            for k2 in self.aakkoset:
                kaikki_kirjainparit.append(k1 + k2)
        # Luodaan taulukko, joka sisältää hakemiston (dictionary) jokaiselle sanan kirjainparipaikalle.
        # Niistä kukin sisältää jokaisen mahdollisen kirjainparin esiintymiskerrat sanastossa kyseisellä paikalla.
        # Esimerkiksi jos kirjainparitaulukko[0]['ab'] = 10, kymmenessä sanassa ensimmäinen kirjainpari on 'ab'.
        kirjainparitaulukko = []
        for paikka in range(0, self.sanan_pituus - 1):
            kirjainparitaulukko.append({})
            for pari in kaikki_kirjainparit:
                kirjainparitaulukko[paikka][pari] = 0
                for sana in self.sanasto:
                    if sana[paikka:paikka+2] == pari:
                        kirjainparitaulukko[paikka][pari] += 1
        return kirjainparitaulukko

    # Tämä metodi laskee kirjaimien esiintymiskerrat sanastossa kullakin kirjainpaikalla
    # ja palauttaa listan, joka sisältää yhtä monta hakemistoa kuin sanaston sanoissa on kirjaimia.
    # Esimerkiksi jos esiintymiskerrat[0]['a'] = 75, a on ensimmäinen kirjain 75 sanassa.
    def laske_esiintymiskerrat(self):
        esiintymiskerrat = []
        for paikka in range(0, self.sanan_pituus):
            esiintymiskerrat.append({})
        for k in self.aakkoset:
            for paikka in range(0, self.sanan_pituus):
                esiintymiskerrat[paikka][k] = 0
        for sana in self.sanasto:
            for paikka in range(0, self.sanan_pituus):
                esiintymiskerrat[paikka][sana[paikka]] += 1
        return esiintymiskerrat

    # Seuraavassa luodaan kirjaintaulukon pohjalta arvontataulukko, jota käytetään arvausten laatimisessa.
    # Jokaista kirjainpaikkaa kohden on lista, joka sisältää jokaisen kirjaimen yhtä monta kertaa kuin kyseinen
    # kirjain esiintyy sanastossa kyseisellä paikalla. Esimerkiksi jos a-kirjain esiintyy kolmannella paikalla
    # 100 kertaa ja b-kirjain 50 kertaa, arvontataulukko[2] sisältää sata kappaletta a-kirjaimia ja 50 kappaletta
    # b-kirjaimia. Kun tästä taulukosta valitaan satunnainen kirjain, tulokset vastaavat kirjainten jakaumaa sanastossa.
    # (Esiintymiskertoihin lisätään jokaisen kirjaimen kohdalla 1. Tämä vääristää jakaumaa aavistuksen verran, mutta
    # se tehdään siksi, ettei suljettaisi mahdollisuuksia kokonaan pois: vaikka sanastossamme ei olisi yhtään x:llä
    # alkavaa sanaa, jätetään kuitenkin mahdollisuus, että Perttu voi keksiä x:llä alkavan sanan.)

    def luo_arvontataulukko(self, esiintymiskerrat):
        arvontataulukko = []
        for paikka in range(0, self.sanan_pituus):
            arvontataulukko.append([])
        for k in self.aakkoset:
            for paikka in range(0, self.sanan_pituus):
                kerrat = esiintymiskerrat[paikka][k]
                for kerta in range(0, kerrat + 1):
                    arvontataulukko[paikka].append(k)
        return arvontataulukko

# Arvailuun liittyvät metodit

    # Tämä metodi päivittää mahdollisten kirjaimien taulukon tehdyn arvauksen ja Wordlen antaman palautteen pohjalta.
    def paivita_mahdolliset(self, edellinen_arvaus, palaute):
        # Ensin katsotaan, mitkä kirjaimet olivat oikein (oikealla paikalla tai väärällä paikalla).
        # Luodaan joukko kirjaimista, jotka olivat oikein mutta väärällä paikalla.
        vaaralla_paikalla = set()
        for paikka in range(0, self.sanan_pituus):
            k = edellinen_arvaus[paikka]
            if palaute[paikka] == 'O':
                # Kirjain oli oikein, joten se on tässä paikassa ainoa mahdollinen.
                self.mahdolliset[paikka] = set(k)
            elif palaute[paikka] == 'o':
                # Kirjain oli oikea mutta väärällä paikalla, joten poistetaan se tämän paikan mahdollisista
                # kirjaimista ja lisätään väärällä paikalla olleiden listaan.
                self.mahdolliset[paikka].discard(k)
                vaaralla_paikalla.add(k)

        # Sitten katsotaan väärin menneet kirjaimet ja poistetaan ne mahdollisten joukosta kaikilla paikoilla.
        # Poikkeustapaus: Jos esimerkiksi ratkaisussa on yksi c-kirjain ja arvauksessa on kaksi c-kirjainta
        # väärillä paikoilla, Wordle merkitsee vain ensimmäisen niistä keltaisella. Jälkimmäinen c-kirjain
        # on siis Wordlen mukaan väärin, mutta emme halua poistaa sitä muualta kuin kyseiseltä paikalta.
        # Siksi tarkistetaan ensin, onko kirjain "väärällä paikalla"-joukossa.
        for paikka in range(0, self.sanan_pituus):
            k = edellinen_arvaus[paikka]
            if palaute[paikka] == '.':
                self.mahdolliset[paikka].discard(k)
                if k not in vaaralla_paikalla:
                    for paikka2 in range(0, self.sanan_pituus):
                        self.mahdolliset[paikka2].discard(k)

    # Seuraava metodi laskee kirjainparipisteet eli pisteyttää sanan sen perusteella, kuinka yleisiä sen kirjainparit
    # ovat sanastossa kyseisillä paikoilla. Pohjapistemäärä on 1. Sana käydään läpi kirjainpari kerrallaan ja pistemäärä
    # kerrotaan kirjainparin esiintymiskerroilla sanastossa kyseisellä paikalla. Kuten kirjainarvontataulukossa,
    # esiintymismäärään lisätään 1, jotta ei suljeta kokonaan pois sanastossa esiintymättömiä kirjainpareja.
    def kirjainparipisteet(self, arvaus):
        pisteet = 1
        for paikka in range(0, self.sanan_pituus - 1):
            pari = ''.join(arvaus[paikka:paikka+2])
            pisteet *= (self.kirjainparit[paikka][pari] + 1)
        return pisteet

    def hylkaa(self, arvaus):
        self.hylatyt.add(arvaus)

    def arvaa(self, edellinen_arvaus, palaute):
        uusi_arvaus = None
        pisteet = None
        sana_loydetty = False
        while not sana_loydetty:
            sana_loydetty = True                               # Oletetaan, että kelvollinen ehdotus löytyy
            uusi_arvaus = list(' ' * self.sanan_pituus)        # Aloitetaan tyhjällä sanalla
            vapaat_paikat = set(range(0, self.sanan_pituus))   # Vapaat paikat, aluksi kaikki

            # Käydään sana läpi kirjain kerrallaan kolme kertaa.

            # Oikea kirjain oikealla paikalla eli vihreät, palautteessa 'O'
            for paikka in range(0, self.sanan_pituus):
                if palaute[paikka] == 'O':
                    uusi_arvaus[paikka] = edellinen_arvaus[paikka]
                    vapaat_paikat.remove(paikka)

            # Oikea kirjain väärällä paikalla eli keltaiset, palautteessa 'o'
            for paikka in range(0, self.sanan_pituus):
                if palaute[paikka] == 'o':
                    k = edellinen_arvaus[paikka]

                    # Pitää löytää uusi paikka kirjaimelle. Luodaan joukko paikoista, jotka ovat mahdollisia:
                    mahdolliset_paikat = deepcopy(vapaat_paikat)
                    for uusi_paikka in vapaat_paikat:
                        if (k not in self.mahdolliset[uusi_paikka]) or (uusi_paikka == paikka):
                            mahdolliset_paikat.remove(uusi_paikka)

                    # Jos yhtään mahdollista paikkaa ei löydy, aiempien kirjaimien kohdalla on jo jotain mennyt pieleen
                    # (tämän kirjaimen oikea paikka on täytetty jollakin muulla kirjaimella) ja tämä yritys hylätään:
                    if len(mahdolliset_paikat) == 0:
                        sana_loydetty = False

                    # Muussa tapauksessa etsitään kirjaimelle paras mahdollinen paikka. Luodaan arvontataulukko, jossa
                    # listataan kaikki kirjaimelle mahdolliset paikat yhtä monta kertaa kuin kirjain sanastossa esiintyy
                    # kyseisellä paikalla (Jälleen lisätään 1, ettei suljeta pois sanastossa esiintymätöntä sanaa).
                    # Arvotaan taulukosta satunnainen paikka.
                    else:
                        paikka_arvonta = []
                        for paikka2 in mahdolliset_paikat:
                            for kerta in range(0, self.esiintymiskerrat[paikka2][k] + 1):
                                paikka_arvonta.append(paikka2)
                        valittu_paikka = random.choice(paikka_arvonta)
                        uusi_arvaus[valittu_paikka] = k
                        vapaat_paikat.remove(valittu_paikka)

            if sana_loydetty:  # Toistaiseksi kaikki hyvin...
                # Täydennetään tyhjät paikat yleisyyden mukaan painotetuilla satunnaiskirjaimilla.
                for paikka in range(0, self.sanan_pituus):
                    while uusi_arvaus[paikka] == ' ':
                        ehdotettu_kirjain = random.choice(self.kirjainarvonta[paikka])
                        # Jos ehdotettu kirjain on mahdollinen kyseisellä paikalla eikä ole sama kuin edellisessä
                        # arvauksessa, hyväksytään se.
                        if (ehdotettu_kirjain in self.mahdolliset[paikka]) \
                                and (ehdotettu_kirjain != edellinen_arvaus[paikka]):
                            uusi_arvaus[paikka] = ehdotettu_kirjain

                # Hylätään sana, jos 1) sitä on ehdotettu aiemmin, 2) siinä on kolme samaa kirjainta peräkkäin tai
                # 3) jos siinä ei ole yhtään vokaalia.
                if ''.join(uusi_arvaus) in self.hylatyt:
                    sana_loydetty = False
                else:
                    for k in uusi_arvaus:
                        if ''.join(uusi_arvaus).count(k + k + k) > 0:
                            sana_loydetty = False
                    vokaali_on = False

                    for k in uusi_arvaus:
                        if k in self.vokaalit:
                            vokaali_on = True
                    if not vokaali_on:
                        sana_loydetty = False

            if sana_loydetty:  # Kaikki edelleen ok! Lasketaan kirjainparipisteet.
                pisteet = self.kirjainparipisteet(''.join(uusi_arvaus))

        return ''.join(uusi_arvaus), pisteet
