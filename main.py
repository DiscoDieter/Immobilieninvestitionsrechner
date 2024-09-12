"""
Cash FLow und Kapitalwertberechnung über den Vergleich einer zu vermieteten Wohnung und einer Kapitalmarktinvestition
"""
import logging
import pandas as pd
import datetime

######################
# Wohnungsparameter
######################
Wohnung = 100000
Stellplatz = 0
Wertsteigerung_Immobilie_pro_Jahr = 0.02
Anschaffungsbetrag = Wohnung + Stellplatz
kaufnebenkosten_prozent = 0.1

######################
# Angaben zum Kreditvertrag
######################
Eigenanteil = 10000
Zinssatz = 0.032
eigenbeitrag_mtl = 500
sondertilgung = 2000

######################
# Annahmen zum Mietvertrag
######################
kaltmiete = 500
hausgeld = 60

######################
# Option: Anlage am Kapitalmarkt
######################
erwartete_Rendite_am_Kapitalmarkt = 0.06

######################
# Sonstige Annahmen
######################
einkommensteuersatz = 0.3
Kapitalkostensatz = 0.03


##############################################################################
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 10)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

Kaufnebenkosten = Anschaffungsbetrag * kaufnebenkosten_prozent
Gesamt_Anschaffung = Anschaffungsbetrag + Kaufnebenkosten
Kreditsumme = Gesamt_Anschaffung - Eigenanteil
monatl_mietertrag = kaltmiete - hausgeld
Monatl_an_bank = monatl_mietertrag + eigenbeitrag_mtl + sondertilgung/12

cols = ["Restschuld", "Zinsen", "Tilgung", "Abschreibung", "Steuern", "Cash Flow"]
df = pd.DataFrame(columns=cols)
restschuld = Kreditsumme
abschreibung = 0
startjahr = datetime.date.today().year + 1
for i in range(startjahr, 2150):
    if i == startjahr:
        restschuld=restschuld
    else:
        restschuld=restschuld - (Monatl_an_bank*12 - restschuld * Zinssatz)
    zinsen = (restschuld*Zinssatz) if restschuld > 0 else 0
    tilgung = (Monatl_an_bank*12-zinsen) if restschuld > 0 else 0
    abschreibung = Anschaffungsbetrag*0.02 if i < 100/0.02 else 0
    steuern = (zinsen + abschreibung - monatl_mietertrag * 12) * einkommensteuersatz
    cf = -zinsen - tilgung + steuern + monatl_mietertrag * 12
    df.loc[i] = [restschuld, zinsen, tilgung, abschreibung, steuern, cf]
try:
    kreditlaufzeit = df.index[df["Restschuld"]<0][0] - startjahr
    df = df[df.index <= startjahr + kreditlaufzeit]
    df.loc[startjahr + kreditlaufzeit,:] = [0,0,0,abschreibung,abschreibung-monatl_mietertrag*12,
                                            df.iloc[-1,:]["Cash Flow"] + Anschaffungsbetrag *
                                            (1 + Wertsteigerung_Immobilie_pro_Jahr) ** kreditlaufzeit]
    print(df)
    print("Kreditlaufzeit " + str(kreditlaufzeit) + " Jahre")
    zusatzinvest = sondertilgung + eigenbeitrag_mtl*12
    kapitalwert_kapitalmarkt = sum([-Eigenanteil] + [(zusatzinvest * (1+erwartete_Rendite_am_Kapitalmarkt)**(kreditlaufzeit-n))*(1+Kapitalkostensatz)**-kreditlaufzeit for n in range(0,kreditlaufzeit)])
    kapitalwert_immo = sum([-Eigenanteil] + [x * (float(1) + Kapitalkostensatz) ** -float(n) for (n, x) in enumerate(df["Cash Flow"])])
    print(f"Kapitalwert der Immobilieninvestition: {kapitalwert_immo:.2f}")
    print(f"Kapitalwert einer Kapitalmarktinvestition: "
          f"{kapitalwert_kapitalmarkt:.2f}")
    if kapitalwert_kapitalmarkt > kapitalwert_immo:
        print("Anlage am Kapitalmarkt vorteilhaft gegenüber Immobilieninvestition!")
    else:
        print("Immobilieninvestition vorteilhaft gegenüber Anlage am Kapitalmarkt!")

    print("Monatliche Belastung: " + str(eigenbeitrag_mtl))
    print("Jährliche Mieteinnahmen: " + str(monatl_mietertrag * 12))
except IndexError:
    logging.warning("Ausgaben für Kredit sind aktuell zu hoch: Entweder höherer Monatl. Mietertrag oder höhere "
                    "Sondertilgung oder höherer Eigenbeitrag_mtl")

