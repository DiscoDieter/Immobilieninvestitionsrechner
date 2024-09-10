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
Wertsteigerung_Immobilie_pro_Jahr = 0.04
Anschaffungsbetrag = Wohnung + Stellplatz
kaufnebenkosten_prozent = 0.1

######################
# Angaben zum Kreditvertrag
######################
Eigenanteil = 2000
Zinssatz = 0.035
eigenbeitrag_mtl = 0
sondertilgung = 0

######################
# Annahmen zum Mietvertrag
######################
kaltmiete = 600
hausgeld = 70

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
    if i == 2026:
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
    df = df[startjahr < df.index]
    df = df[df.index <= startjahr + kreditlaufzeit]
    df.loc[startjahr + kreditlaufzeit,:] = [0,0,0,abschreibung,abschreibung-monatl_mietertrag*12,
                                            df.iloc[-1,:]["Cash Flow"] + Anschaffungsbetrag *
                                            (1 + Wertsteigerung_Immobilie_pro_Jahr) ** kreditlaufzeit]
    zusatzinvest = sondertilgung + eigenbeitrag_mtl
    endwert_kapitalmarkt = -Eigenanteil + zusatzinvest * (1+erwartete_Rendite_am_Kapitalmarkt)**kreditlaufzeit
    kapitalwert_kapitalmarkt = endwert_kapitalmarkt * (1+Kapitalkostensatz)**-kreditlaufzeit
    print(df)
    print("Kreditlaufzeit " + str(kreditlaufzeit) + " Jahre")

    abgezinst = [-Eigenanteil] + [x * (float(1) + Kapitalkostensatz) ** -float(n) for (n, x) in enumerate(df["Cash Flow"])]
    print(f"Kapitalwert der Immobilieninvestition: {sum(abgezinst):.2f}")
    print(f"Kapitalwert einer Kapitalmarktinvestition: "
          f"{(-Eigenanteil + (Eigenanteil *  (1 + erwartete_Rendite_am_Kapitalmarkt) ** kreditlaufzeit)* (1/(1+Kapitalkostensatz)**kreditlaufzeit)):.2f}")
    print("Monatliche Belastung: " + str(eigenbeitrag_mtl))
except IndexError:
    logging.warning("Ausgaben für Kredit sind aktuell zu hoch: Entweder höherer Monatl. Mietertrag oder höhere "
                    "Sondertilgung oder höherer Eigenbeitrag_mtl")

