all these has been rewritten to vars in english within the code


TRM (NOT NULL): float, manual entry

BTK TRM (NOT NULL): float, manual entry

TRM BROADSPEC: float, calculado como TRM (NOT NULL) - 300

COSTO DE TRANSFERENCIA: float, 6.99 + (6.99 × 0.19 × BTK TRM)

TOKEN VALUE: float, BTK TRM × 0.05

MODELO: string, manual entry

TKS: integer, manual entry

USD: float, TKS / 20

%: float, manual selection (0.60, 0.70, 0.75)

NETO: float, USD × %

Other Site USD: float, manual, se suma por sitio

DÓLARES QUINCENA ANTERIOR: float, manual

TOTALUSD_PRECALC: float, NETO + Other Site USD + DÓLARES QUINCENA ANTERIOR

BTK OFFER: (TOTALUSD_PRECALC × BTK TRM) - COSTO DE TRANSFERENCIA

VALOR BROADSPEC: (TOTALUSD_PRECALC × TRM BROADSPEC) - COSTO DE TRANSFERENCIA

Adelantos: float, manual, cost

Multas: float, manual, cost

Total: VALOR BROADSPEC - Adelantos - Multas

TOKENS REALES BROADSPEC: (Total + COSTO DE TRANSFERENCIA) / TOKEN VALUE

platformusd: TOKENS REALES BROADSPEC / 20