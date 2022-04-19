# Wordle-botti Perttu. Mikrobitti & Simo Sahla 2022.

from perttu import Perttu
from sys import argv

print()
print('Hei, olen Perttu. Arvailen Wordle-sanoja.')
print('Odota hetki, tutkin sanastoa.')

perttu = Perttu(argv[1])

print('Valmista.')
print()
print('Ehdotan sanaa seuraavaksi arvaukseksi. Jos ehdotus kelpaa, anna')
print('vastaukseksi Wordlen palaute viiden merkin merkkijonona, jossa')
print('    O = oikea kirjain oikealla paikalla')
print('    o = oikea kirjain väärällä paikalla')
print('    . = väärä kirjain.')
print('Hylkää ehdotus painamalla enter. Poistu vastaamalla q.')
print()

edellinen_arvaus = ''
arvailu_kaynnissa = True
palaute = None
uusi_arvaus = None
arvauksia = 1

while arvailu_kaynnissa:
    # Jos edellistä arvausta ei ole eli ollaan ensimmäisellä
    # kierroksella, kysytään käyttäjältä avaussana ja Wordlen palaute.
    if edellinen_arvaus == '':
        edellinen_arvaus = input('Syötä avaussana: ')
        if edellinen_arvaus == 'q':
            arvailu_kaynnissa = False
        else:
            palaute = input('Syötä Wordlen palaute: ')
            if palaute == 'q':
                arvailu_kaynnissa = False
    else:
        # Luodaan sata uutta ehdotusta ja tarjotaan niistä parasta.
        # Jos käyttäjän vastaus on tyhjä, otetaan uusiksi.
        vastaus = ''
        while vastaus == '':
            uudet_ehdotukset = []
            for i in range(0, 100):
                uudet_ehdotukset.append((perttu.arvaa(edellinen_arvaus, palaute)))
            uusi_arvaus = sorted(uudet_ehdotukset, key=lambda arvaus: arvaus[1], reverse=True)[0]
            vastaus = input(uusi_arvaus[0] + '? ')
            if vastaus == '':
                perttu.hylkaa(uusi_arvaus[0])  # Lisätään hylätty ehdotus hylättyjen listaan
            elif vastaus == 'q':
                arvailu_kaynnissa = False
        edellinen_arvaus = uusi_arvaus[0]
        palaute = vastaus
    if palaute.count('O') == perttu.sanan_pituus:
        print('Tarvittiin {} arvausta.'.format(arvauksia))
        arvailu_kaynnissa = False
    elif arvailu_kaynnissa:
        arvauksia += 1
        perttu.paivita_mahdolliset(edellinen_arvaus, palaute)
