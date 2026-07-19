#!/usr/bin/env python3
"""
gen-municipality-ndjson.py

Generate municipality.ndjson and contract.ndjson under data/gov/{cc}/.
Run from the etzhayyim-project-states/ directory.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Contract definitions per country
# Tuple: (name, nameEn, contractSlug, legalBasis, effectiveDate, url)
# ---------------------------------------------------------------------------
CONTRACTS = {
    "jpn": ("地方自治法", "Local Autonomy Act", "local-autonomy-act", "Act No. 67 of 1947", "1947-05-03", "https://elaws.e-gov.go.jp/document?lawid=322AC0000000067"),
    "usa": ("State Municipal Charter", "State Municipal Charter", "state-municipal-charter", "US Constitution 10th Amendment", "1791-12-15", "https://www.usa.gov/"),
    "deu": ("Gemeindeordnung / GG Art.28", "Gemeindeordnung (Grundgesetz Art.28)", "grundgesetz-art-28", "GG Art. 28 Abs. 2", "1949-05-23", "https://www.gesetze-im-internet.de/gg/art_28.html"),
    "fra": ("Code général des collectivités territoriales", "Code général des collectivités territoriales", "cgct", "CGCT L2111-1", "1996-02-21", "https://www.legifrance.gouv.fr/"),
    "gbr": ("Local Government Act 1972", "Local Government Act 1972", "local-government-act-1972", "Local Government Act 1972", "1972-10-26", "https://www.legislation.gov.uk/ukpga/1972/70"),
    "ita": ("TUEL D.Lgs. 267/2000", "Testo Unico Enti Locali", "tuel-2000", "D.Lgs. 18 agosto 2000, n. 267", "2000-08-18", "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2000-08-18;267"),
    "can": ("Municipal Government Acts (provincial)", "Municipal Government Act", "constitution-act-1867", "Constitution Act 1867 s.92", "1867-07-01", "https://laws-lois.justice.gc.ca/eng/const/"),
    "aus": ("Local Government Act (state)", "Local Government Act", "local-government-act", "Local Government Acts per state", "1993-01-01", "https://www.legislation.gov.au/"),
    "kor": ("지방자치법", "Local Autonomy Act", "local-autonomy-act", "Act No. 17893", "2022-01-13", "https://www.law.go.kr/"),
    "ind": ("74th Constitutional Amendment Act 1992", "74th Amendment", "constitution-74th-amendment", "Constitution (74th Amendment) Act 1992", "1992-12-20", "https://legislative.gov.in/"),
    "bra": ("Constituição Federal Art.29-31", "Constituição Federal Arts. 29-31", "constituicao-federal-art-29", "CF/1988 Art. 29", "1988-10-05", "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"),
    "chn": ("城市居民委员会组织法", "Organic Law of Urban Residents Committees", "urban-residents-committees-law", "Order No.21 of NPC Standing Committee 1989", "1989-12-26", "https://www.gov.cn/"),
    "rus": ("Федеральный закон 131-ФЗ", "Federal Law on Local Self-Government No.131-FZ", "federal-law-131-2003", "131-ФЗ от 6 октября 2003", "2003-10-06", "https://www.consultant.ru/document/cons_doc_LAW_44571/"),
    "mex": ("Constitución Política Art.115", "Constitución Política Art.115", "constitucion-art-115", "Constitución Política Art.115", "1917-02-05", "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf"),
    "sau": ("نظام المناطق 1992", "Regions Regulation 1992", "regions-regulation-1992", "Royal Decree No.A/90 1992", "1992-03-01", "https://www.boe.gov.sa/"),
    "tur": ("Belediye Kanunu 5393", "Municipal Law No.5393", "belediye-kanunu-5393", "5393 sayılı Belediye Kanunu", "2005-07-13", "https://www.mevzuat.gov.tr/MevzuatMetin/1.5.5393.pdf"),
    "arg": ("Constitución Nacional Art.123", "Constitución Nacional Art.123", "constitucion-art-123", "CN Art.123", "1994-08-22", "https://www.argentina.gob.ar/constitucion"),
    "zaf": ("Local Government: Municipal Structures Act 117/1998", "Municipal Structures Act 117/1998", "municipal-structures-act-1998", "Act 117 of 1998", "1998-12-18", "https://www.gov.za/documents/local-government-municipal-structures-act"),
    "idn": ("UU No.23 Tahun 2014", "Local Government Law No.23/2014", "uu-23-2014", "Undang-Undang Nomor 23 Tahun 2014", "2014-09-30", "https://jdih.kemenkeu.go.id/"),
    "esp": ("Ley de Bases del Régimen Local 7/1985", "Ley Bases Régimen Local", "lbrl-7-1985", "LBRL 7/1985 de 2 de abril", "1985-04-02", "https://www.boe.es/buscar/act.php?id=BOE-A-1985-5392"),
    "nld": ("Gemeentewet", "Municipalities Act", "gemeentewet", "Wet van 14 februari 1992", "1992-02-14", "https://wetten.overheid.nl/BWBR0005416/"),
    "bel": ("Gemeentewet / Code de la démocratie locale", "New Municipal Law", "new-municipal-law", "Nouvelle loi communale 1988", "1988-01-01", "https://www.belgium.be/"),
    "che": ("Gemeindeordnung per Kanton", "Cantonal Municipal Law", "cantonal-municipal-law", "Bundesverfassung Art.50", "1999-04-18", "https://www.admin.ch/"),
    "aut": ("Gemeindeordnung per Land", "Gemeindeordnung", "gemeindeordnung", "B-VG Art.116", "1920-10-01", "https://www.ris.bka.gv.at/"),
    "pol": ("Ustawa o samorządzie gminnym", "Local Government Act", "ustawa-samorzad-gminny", "Dz. U. 1990 nr 16 poz. 95", "1990-03-08", "https://isap.sejm.gov.pl/"),
    "swe": ("Kommunallagen", "Local Government Act", "kommunallagen", "SFS 2017:725", "2017-06-22", "https://www.riksdagen.se/"),
    "nor": ("Kommuneloven", "Local Government Act", "kommuneloven", "LOV-2018-06-22-83", "2018-06-22", "https://lovdata.no/"),
    "dnk": ("Lov om kommunernes styrelse", "Municipal Governance Act", "kommunestyrelsesloven", "LBK nr 47 af 15/01/2019", "2019-01-15", "https://www.retsinformation.dk/"),
    "fin": ("Kuntalaki", "Local Government Act", "kuntalaki", "410/2015", "2015-04-10", "https://finlex.fi/"),
    "prt": ("Lei das Autarquias Locais 75/2013", "Local Authorities Framework Law", "lei-75-2013", "Lei n.º 75/2013", "2013-09-12", "https://www.pgdlisboa.pt/"),
    "grc": ("Κώδικας Δήμων και Κοινοτήτων Ν.3463/2006", "Municipal and Community Code", "kdkn-3463-2006", "Ν.3463/2006 + Kallikratis 3852/2010", "2006-06-08", "https://www.ypes.gr/"),
    "cze": ("Zákon o obcích 128/2000", "Municipal Act 128/2000", "zakon-o-obcich-128-2000", "Zákon č. 128/2000 Sb.", "2000-04-12", "https://www.zakonyprolidi.cz/"),
    "hun": ("Mötv. 2011. évi CLXXXIX. tv.", "Local Governments Act", "mott-2011", "2011. évi CLXXXIX. törvény", "2011-12-27", "https://njt.hu/"),
    "rou": ("Legea administrației publice locale 215/2001", "Local Public Administration Law", "legea-215-2001", "Legea nr. 215/2001", "2001-04-25", "https://legislatie.just.ro/"),
    "ukr": ("Закон про місцеве самоврядування 280/97-ВР", "Law on Local Self-Government", "zakon-280-1997", "Закон № 280/97-ВР від 21.05.1997", "1997-05-21", "https://zakon.rada.gov.ua/"),
    "bgr": ("Закон за местното самоуправление и местната администрация", "Local Self-Government Act", "zmcma", "ЗМСМА обн. ДВ бр.77/17.09.1991", "1991-09-17", "https://www.lex.bg/"),
    "hrv": ("Zakon o lokalnoj i područnoj (regionalnoj) samoupravi", "Local and Regional Government Act", "zlprs", "NN br. 33/01", "2001-04-05", "https://www.zakon.hr/"),
    "svk": ("Zákon o obecnom zriadení 369/1990", "Municipalities Act 369/1990", "zakon-369-1990", "Zákon č. 369/1990 Zb.", "1990-09-06", "https://www.slov-lex.sk/"),
    "srb": ("Закон о локалној самоуправи 129/2007", "Law on Local Self-Government", "zakon-129-2007", "Сл. гласник РС бр. 129/2007", "2007-11-21", "https://www.paragraf.rs/"),
    "svn": ("Zakon o lokalni samoupravi", "Local Government Act", "zls", "UL RS, št. 72/1993", "1993-12-29", "https://www.uradni-list.si/"),
    "mne": ("Zakon o lokalnoj samoupravi", "Law on Local Self-Government", "zls-mne", "Sl. list CG br. 2/18", "2018-01-10", "https://www.paragraf.me/"),
    "mkd": ("Законот за локалната самоуправа", "Law on Local Self-Government", "lls-mkd", "Сл. весник бр. 5/2002", "2002-01-24", "https://www.slvesnik.com.mk/"),
    "alb": ("Ligji për qeverisjen vendore Nr. 139/2015", "Law on Local Government 139/2015", "ligji-139-2015", "Ligji nr. 139/2015", "2015-12-17", "https://www.qbz.gov.al/"),
    "bih": ("Zakon o principima lokalne samouprave u FBiH / RS", "Law on Principles of Local Self-Government", "zopls", "Sl. glasnik BiH 49/06", "2006-07-19", "https://www.fbihvlada.gov.ba/"),
    "geo": ("საქართველოს ორგანული კანონი ადგილობრივი თვითმმართველობის კოდექსი", "Local Self-Government Code", "lsgc-geo", "სს 16/12/2014 N3031", "2014-12-16", "https://matsne.gov.ge/"),
    "est": ("Kohaliku omavalitsuse korralduse seadus KOKS", "Local Government Organisation Act", "koks", "RT I 1993, 37, 558", "1993-06-02", "https://www.riigiteataja.ee/"),
    "ltu": ("Vietos savivaldos įstatymas", "Law on Local Self-Government", "lsg-ltu", "Žin., 1994, Nr. 55-1049", "1994-07-07", "https://www.e-tar.lt/"),
    "lva": ("Likums Par pašvaldībām", "Law on Local Governments", "pashvaldibam-lva", "LV, 61, 24.05.1994", "1994-05-19", "https://likumi.lv/"),
    "isl": ("Sveitarstjórnarlög nr. 138/2011", "Local Government Act 138/2011", "sveitarstjornarlog", "Nr. 138/2011", "2011-12-28", "https://www.althingi.is/"),
    "lux": ("Loi communale du 13 décembre 1988", "Loi communale", "loi-communale-1988", "Mém. A 1988 No. 75", "1988-12-13", "https://legilux.public.lu/"),
    "cyp": ("Ο Περί Δήμων Νόμος Ν.111/85", "Municipalities Law 111/85", "nomioi-111-85", "Ν.111/85", "1985-01-01", "https://www.cylaw.org/"),
    "mlt": ("Local Government Act Cap. 363", "Local Government Act", "local-government-cap-363", "Cap. 363 of the Laws of Malta", "1993-01-01", "https://legislation.mt/"),
    "are": ("القانون الاتحادي رقم 4 لسنة 2000", "Federal Law No.4/2000 on Local Authorities", "federal-law-4-2000-are", "Federal Law No.4 of 2000", "2000-01-01", "https://uaecabinet.ae/"),
    "qat": ("قانون رقم 12 لسنة 2008 البلديات", "Law No.12/2008 on Municipalities", "law-12-2008-qat", "Law No.12 of 2008", "2008-01-01", "https://www.almeezan.qa/"),
    "kwt": ("قانون رقم 15 لسنة 1964 البلديات", "Law No.15/1964 on Municipalities", "law-15-1964-kwt", "Law No.15 of 1964", "1964-01-01", "https://www.e.gov.kw/"),
    "bhr": ("مرسوم بقانون رقم 35 لسنة 2001 البلديات", "Legislative Decree No.35/2001 on Municipalities", "decree-35-2001-bhr", "LD No.35 of 2001", "2001-09-24", "https://www.moi.gov.bh/"),
    "omn": ("قانون البلديات رقم 116/2021", "Municipalities Law No.116/2021", "law-116-2021-omn", "Law No.116/2021", "2021-01-01", "https://www.mola.gov.om/"),
    "jor": ("قانون الادارة المحلية رقم 71 لسنة 2015", "Decentralization Law No.71/2015", "law-71-2015-jor", "Law No.71 of 2015", "2015-10-22", "https://www.lob.gov.jo/"),
    "lbn": ("قانون البلديات رقم 118/1977", "Municipalities Law No.118/1977", "law-118-1977-lbn", "Law No.118 of 1977", "1977-06-30", "https://www.legallaw.ul.edu.lb/"),
    "irn": ("قانون شوراهای اسلامی", "Islamic Councils Law", "shorahai-islami", "1365/3/29", "1986-06-19", "https://www.ical.ir/"),
    "irq": ("قانون المحافظات رقم 21/2008", "Governorates Law No.21/2008", "law-21-2008-irq", "Law No.21 of 2008", "2008-02-22", "https://www.moj.gov.iq/"),
    "syr": ("قانون الإدارة المحلية رقم 107/2011", "Local Administration Law No.107/2011", "law-107-2011-syr", "Law No.107 of 2011", "2011-05-15", "https://www.parliament.gov.sy/"),
    "yem": ("قانون السلطة المحلية رقم 4 لسنة 2000", "Local Authority Law No.4/2000", "law-4-2000-yem", "Law No.4 of 2000", "2000-01-01", "https://www.yemenlaw.net/"),
    "pak": ("قانون حکومت مقامی", "Local Government Act per province", "local-government-act-pak", "LGA various provincial", "2013-01-01", "https://www.na.gov.pk/"),
    "bgd": ("Local Government Act 1994", "Local Government Act 1994", "local-government-act-bgd", "Act XIV of 1994", "1994-01-01", "https://www.molgrd.gov.bd/"),
    "lka": ("Provincial Councils Act No.42/1987", "Provincial Councils Act", "provincial-councils-act-42-1987", "Act No.42 of 1987", "1987-11-14", "https://www.parliament.lk/"),
    "npl": ("Local Government Operation Act 2074", "Local Government Operation Act 2074", "lgoa-2074", "Act 2074 (2017)", "2017-09-20", "https://www.opmcm.gov.np/"),
    "mmr": ("Ward or Village Tract Administration Law 2012", "Ward/VT Administration Law", "ward-vt-admin-law-2012", "Law No.1/2012", "2012-01-17", "https://www.moi.gov.mm/"),
    "tha": ("พระราชบัญญัติองค์การบริหารส่วนจังหวัด พ.ศ. 2540", "Provincial Administration Organization Act", "pao-act-2540", "พ.ศ. 2540 (1997)", "1997-01-01", "https://www.dla.go.th/"),
    "vnm": ("Luật Tổ chức chính quyền địa phương 77/2015/QH13", "Law on Local Government Organization 77/2015", "lgoa-77-2015", "77/2015/QH13", "2015-06-19", "https://thuvienphapluat.vn/"),
    "phl": ("Local Government Code RA 7160/1991", "Local Government Code", "lgc-ra-7160", "Republic Act No.7160", "1991-10-10", "https://www.officialgazette.gov.ph/"),
    "mys": ("Local Government Act 171/1976", "Local Government Act 171/1976", "lga-171-1976", "Act 171 of 1976", "1976-01-01", "https://www.parlimen.gov.my/"),
    "sgp": ("No municipal act (city-state)", "City-State Administration", "city-state-admin-sgp", "Singapore Constitution 1965", "1965-08-09", "https://www.gov.sg/"),
    "khm": ("Law on Administrative Management of the Capital, Provinces, Municipalities, Districts and Khans 2008", "AMMCDMK Law 2008", "ammcdmk-2008", "NS/RKM/0508/017", "2008-05-22", "https://www.interior.gov.kh/"),
    "lao": ("Law on Local Administration 2015", "Law on Local Administration", "loa-2015", "LNA No.44 of 2015", "2015-12-10", "https://www.na.gov.la/"),
    "zwe": ("Urban Councils Act 29/1973", "Urban Councils Act", "uca-29-1973", "Chapter 29:15", "1973-01-01", "https://www.parlzim.gov.zw/"),
    "ken": ("County Government Act 2012", "County Government Act", "county-government-act-2012", "No.17 of 2012", "2012-07-24", "https://www.parliament.go.ke/"),
    "tza": ("Local Government (Urban Authorities) Act 8/1982", "LG Urban Authorities Act", "lgua-8-1982", "Act No.8 of 1982", "1982-01-01", "https://www.parliament.go.tz/"),
    "nga": ("Local Government Act 1976 (revised)", "Local Government Act", "lga-1976-nga", "Local Government Laws of the Federation", "1976-01-01", "https://www.nassnig.org/"),
    "eth": ("Urban Local Governments Proclamation 624/2009", "Urban LG Proclamation 624", "proclamation-624-2009", "Proclamation No.624/2009", "2009-01-01", "https://www.ethiopialaw.com/"),
    "gha": ("Local Governance Act 936/2016", "Local Governance Act", "local-governance-act-936", "Act 936 of 2016", "2016-01-01", "https://www.parliament.gh/"),
    "cmr": ("Loi 2004/017 sur l'orientation de la décentralisation", "Decentralisation Law 2004", "loi-2004-017", "Loi No.2004/017", "2004-07-22", "https://www.spm.gov.cm/"),
    "sen": ("Code général des Collectivités locales 14/2013", "Code Collectivités locales", "ccl-14-2013", "Loi 2013-10", "2013-12-28", "https://www.gouv.sn/"),
    "ago": ("Lei das Autarquias Locais 27/2019", "Local Authorities Law 27/2019", "lal-27-2019", "Lei no.27/2019", "2019-10-16", "https://www.governo.gov.ao/"),
    "cod": ("Loi organique 08/016 des entités territoriales décentralisées", "ETD Organic Law 08/016", "loi-etd-08-016", "Loi 08/016", "2008-10-07", "https://www.leganet.cd/"),
    "uga": ("Local Government Act Cap.243", "Local Government Act", "lga-cap-243-uga", "Cap. 243 of the Laws of Uganda", "1997-03-27", "https://www.parliament.go.ug/"),
    "moz": ("Lei dos Municípios 2/1997", "Municipalities Law 2/1997", "lei-municipios-2-1997", "Lei n.o 2/1997", "1997-02-18", "https://www.portaldogoverno.gov.mz/"),
    "mdg": ("Loi organique 2014-018 sur les collectivités territoriales", "CTD Law 2014-018", "loi-2014-018-mdg", "Loi 2014-018", "2014-09-12", "https://www.dgd.gov.mg/"),
    "rwa": ("Organic Law 002/2012 on Organisation of Counties", "Organic Law 002/2012", "organic-law-002-2012", "OL No.002/2012/OL", "2012-02-17", "https://www.parliament.gov.rw/"),
    "civ": ("Loi 2001-476 sur l'organisation générale de l'Administration du Territoire", "OGAT Law 2001-476", "loi-2001-476", "Loi no.2001-476", "2001-09-09", "https://www.gouv.ci/"),
    "bfa": ("Code général des collectivités territoriales Loi 055-2004", "CGCT Loi 055-2004", "cgct-055-2004-bfa", "Loi 055-2004/AN", "2004-12-21", "https://www.assemblee-nationale.bf/"),
    "mli": ("Code des collectivités territoriales Loi 2012-007", "CCT Loi 2012-007", "cct-2012-007-mli", "Loi 2012-007", "2012-02-07", "https://www.assemblee-nationale.ml/"),
    "ner": ("Code général des collectivités territoriales Loi 2008-42", "CGCT Loi 2008-42", "cgct-2008-42-ner", "Loi 2008-42", "2008-07-31", "https://www.nigerlegalis.com/"),
    "tcd": ("Loi 002/PR/2000 sur les collectivités territoriales décentralisées", "CTD Law 002/2000", "loi-002-2000-tcd", "Loi no.002/PR/2000", "2000-02-16", "https://www.assemblee-nationale.td/"),
    "gin": ("Loi L/2006/014/AN sur les collectivités locales", "CL Law L/2006/014", "loi-l-2006-014", "Loi L/2006/014/AN", "2006-10-10", "https://www.guineeconakry.gov.gn/"),
    "tgo": ("Code des collectivités locales Loi 2018-003", "CL Code 2018-003", "loi-2018-003-tgo", "Loi 2018-003", "2018-01-12", "https://www.parlement.tg/"),
    "ben": ("Loi 97-029 sur l'organisation des communes", "Communes Law 97-029", "loi-97-029-ben", "Loi 97-029", "1997-01-15", "https://www.gouv.bj/"),
    "nam": ("Local Authorities Act 23/1992", "Local Authorities Act", "laa-23-1992-nam", "Act No.23 of 1992", "1992-09-30", "https://www.lac.org.na/"),
    "bwa": ("Local Government Act Cap 40:01", "Local Government Act", "lga-cap-40-01-bwa", "Cap. 40:01", "1965-01-01", "https://www.parliament.gov.bw/"),
    "lso": ("Local Government Act 1997", "Local Government Act 1997", "lga-1997-lso", "Act of 1997", "1997-01-01", "https://www.parliament.ls/"),
    "swz": ("Swaziland Urban Government Act 8/1969", "Urban Government Act", "uga-8-1969-swz", "Act No.8 of 1969", "1969-01-01", "https://www.gov.sz/"),
    "mwi": ("Local Government Act 42/1998", "Local Government Act", "lga-42-1998-mwi", "Act No.42 of 1998", "1998-09-30", "https://www.parliament.gov.mw/"),
    "zmb": ("Local Government Act Cap 281", "Local Government Act", "lga-cap-281-zmb", "Cap. 281", "1991-01-01", "https://www.parliament.gov.zm/"),
    "col": ("Ley 136/1994 Régimen municipal", "Ley 136/1994", "ley-136-1994-col", "Ley 136 de 1994", "1994-06-02", "https://www.congreso.gov.co/"),
    "ven": ("Ley Orgánica del Poder Público Municipal 2010", "LOPPM 2010", "loppm-2010", "GORBV No.39.163 de 2009", "2009-04-22", "https://www.asambleanacional.gob.ve/"),
    "per": ("Ley Orgánica de Municipalidades 27972/2003", "LOM 27972/2003", "lom-27972-2003", "Ley No.27972", "2003-05-26", "https://www.congreso.gob.pe/"),
    "chl": ("Ley Orgánica Constitucional de Municipalidades 18695/1988", "LOCM 18695", "locm-18695", "Ley 18.695", "1988-12-31", "https://www.bcn.cl/"),
    "ecu": ("COOTAD 2010", "Código Orgánico de Organización Territorial", "cootad-2010", "Registro Oficial 303 de 2010", "2010-10-19", "https://www.asambleanacional.gob.ec/"),
    "bol": ("Ley de Municipalidades 2028/1999", "Ley de Municipalidades", "ley-2028-1999", "Ley No.2028", "1999-10-28", "https://www.gacetaoficialdebolivia.gob.bo/"),
    "pry": ("Ley Orgánica Municipal 3966/2010", "LOM 3966/2010", "lom-3966-2010", "Ley 3966", "2010-02-26", "https://www.congreso.gov.py/"),
    "ury": ("Ley Orgánica Municipal 9515/1935", "LOM 9515/1935", "lom-9515-1935", "Ley 9515", "1935-10-28", "https://www.parlamento.gub.uy/"),
    "pan": ("Ley No.105/1973 régimen municipal", "Ley 105/1973", "ley-105-1973-pan", "Ley No.105", "1973-08-08", "https://www.asamblea.gob.pa/"),
    "cri": ("Código Municipal Ley 7794/1998", "Código Municipal", "cm-ley-7794", "Ley 7794", "1998-04-30", "https://www.asamblea.go.cr/"),
    "gtm": ("Código Municipal Decreto 12-2002", "Código Municipal", "cm-decreto-12-2002", "Decreto 12-2002", "2002-04-02", "https://www.congreso.gob.gt/"),
    "hnd": ("Ley de Municipalidades Decreto 134-1990", "Ley Municipalidades", "lm-decreto-134-1990", "Decreto 134-1990", "1990-10-29", "https://www.congreso.gob.hn/"),
    "slv": ("Código Municipal Decreto 274/1986", "Código Municipal", "cm-decreto-274-1986", "Decreto No.274", "1986-02-05", "https://www.asamblea.gob.sv/"),
    "nic": ("Ley de Municipios 40/1988", "Ley de Municipios", "lm-40-1988", "Ley No.40", "1988-08-17", "https://www.asamblea.gob.ni/"),
    "dom": ("Ley No. 176-07 del Distrito Nacional y los Municipios", "Ley 176-07", "ley-176-07-dom", "Ley No.176-07", "2007-07-17", "https://www.congreso.gov.do/"),
    "cub": ("Ley de los Órganos del Poder Popular 7/1977", "LOPP 7/1977", "lopp-7-1977", "Ley No.7/1977", "1977-08-20", "https://www.parlamentocubano.gob.cu/"),
    "jam": ("Parish Councils Act 1901 (revised)", "Parish Councils Act", "parish-councils-act-jam", "Cap. 303", "1901-01-01", "https://www.japarliament.gov.jm/"),
    "tto": ("Municipal Corporations Act Ch.25:04", "Municipal Corporations Act", "mca-ch-25-04", "Ch.25:04", "1990-01-01", "https://www.ttparliament.org/"),
    "guy": ("Municipal and District Councils Act Cap 28:01", "MDC Act", "mdc-cap-28-01-guy", "Cap.28:01", "1970-01-01", "https://www.parliament.gov.gy/"),
    "kaz": ("Закон о местном государственном управлении и самоуправлении", "Law on Local State Administration", "lmgus-kaz", "ЗРК от 23.01.2001 No.148", "2001-01-23", "https://adilet.zan.kz/"),
    "uzb": ("Закон о самоуправлении граждан", "Law on Citizens' Self-Governance", "lsg-uzb", "ЗРУ No.312", "2013-04-22", "https://lex.uz/"),
    "tkm": ("Закон о статусе города Ашхабада 1999", "Law on Status of Ashgabat", "lsga-1999", "Закон 1999 г.", "1999-01-01", "https://minjust.gov.tm/"),
    "kgz": ("Закон о местном самоуправлении 2011", "Law on Local Self-Government", "lmsg-2011-kgz", "Закон от 15.07.2011 No.101", "2011-07-15", "https://cbd.minjust.gov.kg/"),
    "tjk": ("Закон о местном самоуправлении в посёлках и сёлах", "Law on LSG in Settlements", "lmsg-tjk", "Закон от 01.12.2004 No.68", "2004-12-01", "https://mmk.tj/"),
    "arm": ("Закон об административно-территориальном делении", "Law on ATD", "latd-arm", "ЗА от 07.11.1995", "1995-11-07", "https://www.parliament.am/"),
    "aze": ("Qanun bələdiyyələr haqqında", "Law on Municipalities", "qbh-aze", "31.07.1999-cu il 697-IQ", "1999-07-31", "https://www.e-qanun.az/"),
    "mol": ("Legea privind administrația publică locală 436/2006", "APL Law 436/2006", "apl-436-2006", "Legea nr.436 din 28.12.2006", "2006-12-28", "https://www.parlament.md/"),
    "blr": ("Закон о местном управлении и самоуправлении в Республике Беларусь", "Law on Local Government", "llg-blr", "Закон от 4 января 2010 г. No.108-З", "2010-01-04", "https://pravo.by/"),
}

DEFAULT_CONTRACT = ("Municipal Government Act", "Municipal Government Act", "municipal-government-act", "General Administrative Law", "1948-01-01", "")

# ---------------------------------------------------------------------------
# Contract metadata (govLevel, cofog, extra tags)
# ---------------------------------------------------------------------------
CONTRACT_GOVLEVEL = {
    "jpn": "municipality",
    "usa": "municipality",
    "deu": "municipality",
    "fra": "municipality",
    "gbr": "municipality",
    "ita": "municipality",
    "can": "municipality",
    "aus": "municipality",
    "kor": "municipality",
    "ind": "municipality",
    "bra": "municipality",
    "chn": "municipality",
    "rus": "municipality",
    "mex": "municipality",
    "sau": "municipality",
    "tur": "municipality",
    "arg": "municipality",
    "zaf": "municipality",
    "idn": "municipality",
}

# ---------------------------------------------------------------------------
# Municipality data
# Each record: (path, name, nameEn, adminCode, population, website, municipalType, parentPath)
# adminCode may be None for non-JPN records
# ---------------------------------------------------------------------------

JPN_CONTRACT = "地方自治法"
JPN_CONTRACT_DID = "did:web:gov-jpn.etzhayyim.com:law:local-autonomy-act"

# JPN designated cities
JPN_DESIGNATED = [
    ("prefecture:hokkaido:sapporo",      "札幌市",   "Sapporo",     "011002", 1952356,  "https://www.city.sapporo.jp/",                     "designated-city", "prefecture:hokkaido"),
    ("prefecture:miyagi:sendai",         "仙台市",   "Sendai",      "041009", 1096704,  "https://www.city.sendai.jp/",                      "designated-city", "prefecture:miyagi"),
    ("prefecture:saitama:saitama",       "さいたま市", "Saitama",    "110006", 1324025,  "https://www.city.saitama.lg.jp/",                  "designated-city", "prefecture:saitama"),
    ("prefecture:chiba:chiba",           "千葉市",   "Chiba",       "120006", 972288,   "https://www.city.chiba.jp/",                       "designated-city", "prefecture:chiba"),
    ("prefecture:kanagawa:yokohama",     "横浜市",   "Yokohama",    "141003", 3756317,  "https://www.city.yokohama.lg.jp/",                 "designated-city", "prefecture:kanagawa"),
    ("prefecture:kanagawa:kawasaki",     "川崎市",   "Kawasaki",    "141011", 1539081,  "https://www.city.kawasaki.jp/",                    "designated-city", "prefecture:kanagawa"),
    ("prefecture:kanagawa:sagamihara",   "相模原市", "Sagamihara",   "141291", 724844,   "https://www.city.sagamihara.kanagawa.jp/",         "designated-city", "prefecture:kanagawa"),
    ("prefecture:niigata:niigata",       "新潟市",   "Niigata",     "151009", 793119,   "https://www.city.niigata.lg.jp/",                  "designated-city", "prefecture:niigata"),
    ("prefecture:shizuoka:shizuoka",     "静岡市",   "Shizuoka",    "221007", 693389,   "https://www.city.shizuoka.lg.jp/",                 "designated-city", "prefecture:shizuoka"),
    ("prefecture:shizuoka:hamamatsu",    "浜松市",   "Hamamatsu",   "221317", 785491,   "https://www.city.hamamatsu.shizuoka.jp/",          "designated-city", "prefecture:shizuoka"),
    ("prefecture:aichi:nagoya",          "名古屋市", "Nagoya",       "231002", 2332176,  "https://www.city.nagoya.jp/",                      "designated-city", "prefecture:aichi"),
    ("prefecture:kyoto:kyoto",           "京都市",   "Kyoto",       "261009", 1463723,  "https://www.city.kyoto.lg.jp/",                    "designated-city", "prefecture:kyoto"),
    ("prefecture:osaka:osaka",           "大阪市",   "Osaka",       "271004", 2752412,  "https://www.city.osaka.lg.jp/",                    "designated-city", "prefecture:osaka"),
    ("prefecture:osaka:sakai",           "堺市",     "Sakai",       "271209", 820018,   "https://www.city.sakai.lg.jp/",                    "designated-city", "prefecture:osaka"),
    ("prefecture:hyogo:kobe",            "神戸市",   "Kobe",        "281005", 1518870,  "https://www.city.kobe.lg.jp/",                     "designated-city", "prefecture:hyogo"),
    ("prefecture:okayama:okayama",       "岡山市",   "Okayama",     "331007", 724691,   "https://www.city.okayama.jp/",                     "designated-city", "prefecture:okayama"),
    ("prefecture:hiroshima:hiroshima",   "広島市",   "Hiroshima",   "341002", 1199371,  "https://www.city.hiroshima.lg.jp/",                "designated-city", "prefecture:hiroshima"),
    ("prefecture:fukuoka:kitakyushu",    "北九州市", "Kitakyushu",   "401005", 938695,   "https://www.city.kitakyushu.lg.jp/",               "designated-city", "prefecture:fukuoka"),
    ("prefecture:fukuoka:fukuoka",       "福岡市",   "Fukuoka",     "401308", 1612392,  "https://www.city.fukuoka.lg.jp/",                  "designated-city", "prefecture:fukuoka"),
    ("prefecture:kumamoto:kumamoto",     "熊本市",   "Kumamoto",    "431004", 741284,   "https://www.city.kumamoto.jp/",                    "designated-city", "prefecture:kumamoto"),
]

# JPN special wards (Tokyo 23-ku)
JPN_SPECIAL_WARDS = [
    ("prefecture:tokyo:chiyoda",   "千代田区", "Chiyoda",   "13101", 67226,  "https://www.city.chiyoda.lg.jp/",   "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:chuo",      "中央区",   "Chuo",      "13102", 170231, "https://www.city.chuo.lg.jp/",      "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:minato",    "港区",     "Minato",    "13103", 260486, "https://www.city.minato.tokyo.jp/", "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:shinjuku",  "新宿区",   "Shinjuku",  "13104", 346235, "https://www.city.shinjuku.lg.jp/",  "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:bunkyo",    "文京区",   "Bunkyo",    "13105", 231549, "https://www.city.bunkyo.lg.jp/",    "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:taito",     "台東区",   "Taito",     "13106", 209627, "https://www.city.taito.lg.jp/",     "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:sumida",    "墨田区",   "Sumida",    "13107", 272629, "https://www.city.sumida.lg.jp/",    "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:koto",      "江東区",   "Koto",      "13108", 522026, "https://www.city.koto.lg.jp/",      "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:shinagawa", "品川区",   "Shinagawa", "13109", 418510, "https://www.city.shinagawa.tokyo.jp/", "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:meguro",    "目黒区",   "Meguro",    "13110", 281012, "https://www.city.meguro.tokyo.jp/", "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:ota",       "大田区",   "Ota",       "13111", 736307, "https://www.city.ota.tokyo.jp/",    "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:setagaya",  "世田谷区", "Setagaya",  "13112", 946668, "https://www.city.setagaya.lg.jp/",  "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:shibuya",   "渋谷区",   "Shibuya",   "13113", 234980, "https://www.city.shibuya.tokyo.jp/","special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:nakano",    "中野区",   "Nakano",    "13114", 341211, "https://www.city.nakano.tokyo.jp/", "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:suginami",  "杉並区",   "Suginami",  "13115", 578545, "https://www.city.suginami.tokyo.jp/","special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:toshima",   "豊島区",   "Toshima",   "13116", 302473, "https://www.city.toshima.lg.jp/",  "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:kita",      "北区",     "Kita",      "13117", 355352, "https://www.city.kita.tokyo.jp/",   "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:arakawa",   "荒川区",   "Arakawa",   "13118", 221225, "https://www.city.arakawa.tokyo.jp/","special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:itabashi",  "板橋区",   "Itabashi",  "13119", 575588, "https://www.city.itabashi.tokyo.jp/","special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:nerima",    "練馬区",   "Nerima",    "13120", 751767, "https://www.nerima.tokyo.jp/",      "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:adachi",    "足立区",   "Adachi",    "13121", 685488, "https://www.city.adachi.tokyo.jp/", "special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:katsushika","葛飾区",   "Katsushika","13122", 455826, "https://www.city.katsushika.lg.jp/","special-ward", "prefecture:tokyo"),
    ("prefecture:tokyo:edogawa",   "江戸川区", "Edogawa",   "13123", 689700, "https://www.city.edogawa.tokyo.jp/","special-ward", "prefecture:tokyo"),
]

# JPN prefectural capitals (non-designated-city)
JPN_CAPITALS = [
    ("prefecture:aomori:aomori",       "青森市",   "Aomori",       "022012", 270000, "https://www.city.aomori.aomori.jp/",     "city", "prefecture:aomori"),
    ("prefecture:iwate:morioka",       "盛岡市",   "Morioka",      "032018", 290000, "https://www.city.morioka.iwate.jp/",     "city", "prefecture:iwate"),
    ("prefecture:akita:akita",         "秋田市",   "Akita",        "052019", 305000, "https://www.city.akita.akita.jp/",       "city", "prefecture:akita"),
    ("prefecture:yamagata:yamagata",   "山形市",   "Yamagata",     "062014", 247000, "https://www.city.yamagata.yamagata.jp/", "city", "prefecture:yamagata"),
    ("prefecture:fukushima:fukushima", "福島市",   "Fukushima",    "072010", 285000, "https://www.city.fukushima.fukushima.jp/","city", "prefecture:fukushima"),
    ("prefecture:ibaraki:mito",        "水戸市",   "Mito",         "082015", 271000, "https://www.city.mito.ibaraki.jp/",      "city", "prefecture:ibaraki"),
    ("prefecture:tochigi:utsunomiya",  "宇都宮市", "Utsunomiya",   "092011", 519000, "https://www.city.utsunomiya.tochigi.jp/","city", "prefecture:tochigi"),
    ("prefecture:gunma:maebashi",      "前橋市",   "Maebashi",     "102016", 333000, "https://www.city.maebashi.gunma.jp/",    "city", "prefecture:gunma"),
    ("prefecture:yamanashi:kofu",      "甲府市",   "Kofu",         "192015", 189000, "https://www.city.kofu.yamanashi.jp/",    "city", "prefecture:yamanashi"),
    ("prefecture:nagano:nagano",       "長野市",   "Nagano",       "202011", 370000, "https://www.city.nagano.nagano.jp/",     "city", "prefecture:nagano"),
    ("prefecture:gifu:gifu",           "岐阜市",   "Gifu",         "212016", 404000, "https://www.city.gifu.lg.jp/",           "city", "prefecture:gifu"),
    ("prefecture:mie:tsu",             "津市",     "Tsu",          "242012", 279000, "https://www.city.tsu.mie.jp/",           "city", "prefecture:mie"),
    ("prefecture:shiga:otsu",          "大津市",   "Otsu",         "252014", 344000, "https://www.city.otsu.lg.jp/",           "city", "prefecture:shiga"),
    ("prefecture:nara:nara",           "奈良市",   "Nara",         "292010", 356000, "https://www.city.nara.lg.jp/",           "city", "prefecture:nara"),
    ("prefecture:wakayama:wakayama",   "和歌山市", "Wakayama",     "302015", 359000, "https://www.city.wakayama.wakayama.jp/", "city", "prefecture:wakayama"),
    ("prefecture:tottori:tottori",     "鳥取市",   "Tottori",      "312011", 188000, "https://www.city.tottori.lg.jp/",        "city", "prefecture:tottori"),
    ("prefecture:shimane:matsue",      "松江市",   "Matsue",       "322015", 204000, "https://www.city.matsue.lg.jp/",         "city", "prefecture:shimane"),
    ("prefecture:yamaguchi:yamaguchi", "山口市",   "Yamaguchi",    "352012", 193000, "https://www.city.yamaguchi.lg.jp/",      "city", "prefecture:yamaguchi"),
    ("prefecture:tokushima:tokushima", "徳島市",   "Tokushima",    "362012", 257000, "https://www.city.tokushima.tokushima.jp/","city", "prefecture:tokushima"),
    ("prefecture:kagawa:takamatsu",    "高松市",   "Takamatsu",    "372013", 420000, "https://www.city.takamatsu.kagawa.jp/",  "city", "prefecture:kagawa"),
    ("prefecture:ehime:matsuyama",     "松山市",   "Matsuyama",    "382019", 507000, "https://www.city.matsuyama.ehime.jp/",   "city", "prefecture:ehime"),
    ("prefecture:kochi:kochi",         "高知市",   "Kochi",        "392014", 332000, "https://www.city.kochi.kochi.jp/",       "city", "prefecture:kochi"),
    ("prefecture:saga:saga",           "佐賀市",   "Saga",         "412015", 236000, "https://www.city.saga.lg.jp/",           "city", "prefecture:saga"),
    ("prefecture:nagasaki:nagasaki",   "長崎市",   "Nagasaki",     "422012", 406000, "https://www.city.nagasaki.lg.jp/",       "city", "prefecture:nagasaki"),
    ("prefecture:oita:oita",           "大分市",   "Oita",         "442011", 478000, "https://www.city.oita.oita.jp/",         "city", "prefecture:oita"),
    ("prefecture:miyazaki:miyazaki",   "宮崎市",   "Miyazaki",     "452017", 401000, "https://www.city.miyazaki.miyazaki.jp/", "city", "prefecture:miyazaki"),
    ("prefecture:kagoshima:kagoshima", "鹿児島市", "Kagoshima",    "462012", 599000, "https://www.city.kagoshima.lg.jp/",      "city", "prefecture:kagoshima"),
    ("prefecture:okinawa:naha",        "那覇市",   "Naha",         "472018", 317000, "https://www.city.naha.okinawa.jp/",      "city", "prefecture:okinawa"),
]

# ---------------------------------------------------------------------------
# USA — 50 state capitals
# ---------------------------------------------------------------------------
USA_CONTRACT = "State Municipal Charter"
USA_CONTRACT_DID = "did:web:gov-usa.etzhayyim.com:law:state-municipal-charter"

USA_CAPITALS = [
    ("state:alabama:montgomery",         "Montgomery",    "Montgomery",     None, 200000,  "https://www.montgomeryal.gov/",           "capital", "state:alabama"),
    ("state:alaska:juneau",              "Juneau",        "Juneau",         None, 31000,   "https://juneau.org/",                     "capital", "state:alaska"),
    ("state:arizona:phoenix",            "Phoenix",       "Phoenix",        None, 1608000, "https://www.phoenix.gov/",                "capital", "state:arizona"),
    ("state:arkansas:little-rock",       "Little Rock",   "Little Rock",    None, 202000,  "https://www.littlerock.gov/",             "capital", "state:arkansas"),
    ("state:california:sacramento",      "Sacramento",    "Sacramento",     None, 524000,  "https://www.cityofsacramento.org/",       "capital", "state:california"),
    ("state:colorado:denver",            "Denver",        "Denver",         None, 715000,  "https://www.denvergov.org/",              "capital", "state:colorado"),
    ("state:connecticut:hartford",       "Hartford",      "Hartford",       None, 122000,  "https://www.hartfordct.gov/",             "capital", "state:connecticut"),
    ("state:delaware:dover",             "Dover",         "Dover",          None, 38000,   "https://www.cityofdover.com/",            "capital", "state:delaware"),
    ("state:florida:tallahassee",        "Tallahassee",   "Tallahassee",    None, 196000,  "https://www.talgov.com/",                 "capital", "state:florida"),
    ("state:georgia:atlanta",            "Atlanta",       "Atlanta",        None, 498000,  "https://www.atlantaga.gov/",              "capital", "state:georgia"),
    ("state:hawaii:honolulu",            "Honolulu",      "Honolulu",       None, 350000,  "https://www.honolulu.gov/",               "capital", "state:hawaii"),
    ("state:idaho:boise",                "Boise",         "Boise",          None, 235000,  "https://www.cityofboise.org/",            "capital", "state:idaho"),
    ("state:illinois:springfield",       "Springfield",   "Springfield",    None, 114000,  "https://www.springfield.il.us/",          "capital", "state:illinois"),
    ("state:indiana:indianapolis",       "Indianapolis",  "Indianapolis",   None, 887000,  "https://www.indy.gov/",                   "capital", "state:indiana"),
    ("state:iowa:des-moines",            "Des Moines",    "Des Moines",     None, 214000,  "https://www.dsm.city/",                   "capital", "state:iowa"),
    ("state:kansas:topeka",              "Topeka",        "Topeka",         None, 126000,  "https://www.topeka.org/",                 "capital", "state:kansas"),
    ("state:kentucky:frankfort",         "Frankfort",     "Frankfort",      None, 27000,   "https://www.frankfort.ky.gov/",           "capital", "state:kentucky"),
    ("state:louisiana:baton-rouge",      "Baton Rouge",   "Baton Rouge",    None, 228000,  "https://www.brla.gov/",                   "capital", "state:louisiana"),
    ("state:maine:augusta",              "Augusta",       "Augusta",        None, 19000,   "https://www.augustamaine.gov/",           "capital", "state:maine"),
    ("state:maryland:annapolis",         "Annapolis",     "Annapolis",      None, 40000,   "https://www.annapolis.gov/",              "capital", "state:maryland"),
    ("state:massachusetts:boston",       "Boston",        "Boston",         None, 675000,  "https://www.boston.gov/",                 "capital", "state:massachusetts"),
    ("state:michigan:lansing",           "Lansing",       "Lansing",        None, 112000,  "https://www.lansingmi.gov/",              "capital", "state:michigan"),
    ("state:minnesota:saint-paul",       "Saint Paul",    "Saint Paul",     None, 308000,  "https://www.stpaul.gov/",                 "capital", "state:minnesota"),
    ("state:mississippi:jackson",        "Jackson",       "Jackson",        None, 153000,  "https://www.jacksonms.gov/",              "capital", "state:mississippi"),
    ("state:missouri:jefferson-city",    "Jefferson City","Jefferson City",  None, 43000,   "https://www.jeffcitymo.org/",             "capital", "state:missouri"),
    ("state:montana:helena",             "Helena",        "Helena",         None, 32000,   "https://www.helenamt.gov/",               "capital", "state:montana"),
    ("state:nebraska:lincoln",           "Lincoln",       "Lincoln",        None, 295000,  "https://lincoln.ne.gov/",                 "capital", "state:nebraska"),
    ("state:nevada:carson-city",         "Carson City",   "Carson City",    None, 58000,   "https://www.carson.org/",                 "capital", "state:nevada"),
    ("state:new-hampshire:concord",      "Concord",       "Concord",        None, 43000,   "https://www.concordnh.gov/",              "capital", "state:new-hampshire"),
    ("state:new-jersey:trenton",         "Trenton",       "Trenton",        None, 90000,   "https://www.trentonnj.org/",              "capital", "state:new-jersey"),
    ("state:new-mexico:santa-fe",        "Santa Fe",      "Santa Fe",       None, 84000,   "https://www.santafenm.gov/",              "capital", "state:new-mexico"),
    ("state:new-york:albany",            "Albany",        "Albany",         None, 99000,   "https://www.albanyny.gov/",               "capital", "state:new-york"),
    ("state:north-carolina:raleigh",     "Raleigh",       "Raleigh",        None, 467000,  "https://raleighnc.gov/",                  "capital", "state:north-carolina"),
    ("state:north-dakota:bismarck",      "Bismarck",      "Bismarck",       None, 73000,   "https://bismarcknq.gov/",                 "capital", "state:north-dakota"),
    ("state:ohio:columbus",              "Columbus",      "Columbus",       None, 905000,  "https://www.columbus.gov/",               "capital", "state:ohio"),
    ("state:oklahoma:oklahoma-city",     "Oklahoma City", "Oklahoma City",  None, 681000,  "https://www.okc.gov/",                    "capital", "state:oklahoma"),
    ("state:oregon:salem",               "Salem",         "Salem",          None, 174000,  "https://www.cityofsalem.net/",            "capital", "state:oregon"),
    ("state:pennsylvania:harrisburg",    "Harrisburg",    "Harrisburg",     None, 50000,   "https://www.harrisburgpa.gov/",           "capital", "state:pennsylvania"),
    ("state:rhode-island:providence",    "Providence",    "Providence",     None, 190000,  "https://www.providenceri.gov/",           "capital", "state:rhode-island"),
    ("state:south-carolina:columbia",    "Columbia",      "Columbia",       None, 136000,  "https://www.columbiasc.gov/",             "capital", "state:south-carolina"),
    ("state:south-dakota:pierre",        "Pierre",        "Pierre",         None, 14000,   "https://www.pierre.sd.gov/",              "capital", "state:south-dakota"),
    ("state:tennessee:nashville",        "Nashville",     "Nashville",      None, 689000,  "https://www.nashville.gov/",              "capital", "state:tennessee"),
    ("state:texas:austin",               "Austin",        "Austin",         None, 961000,  "https://www.austintexas.gov/",            "capital", "state:texas"),
    ("state:utah:salt-lake-city",        "Salt Lake City","Salt Lake City",  None, 200000,  "https://www.slc.gov/",                    "capital", "state:utah"),
    ("state:vermont:montpelier",         "Montpelier",    "Montpelier",     None, 8000,    "https://www.montpelier-vt.org/",          "capital", "state:vermont"),
    ("state:virginia:richmond",          "Richmond",      "Richmond",       None, 226000,  "https://www.rva.gov/",                    "capital", "state:virginia"),
    ("state:washington:olympia",         "Olympia",       "Olympia",        None, 52000,   "https://olympiawa.gov/",                  "capital", "state:washington"),
    ("state:west-virginia:charleston",   "Charleston",    "Charleston",     None, 48000,   "https://www.cityofcharleston.org/",       "capital", "state:west-virginia"),
    ("state:wisconsin:madison",          "Madison",       "Madison",        None, 258000,  "https://www.cityofmadison.com/",          "capital", "state:wisconsin"),
    ("state:wyoming:cheyenne",           "Cheyenne",      "Cheyenne",       None, 63000,   "https://www.cheyennecity.org/",           "capital", "state:wyoming"),
]

# ---------------------------------------------------------------------------
# DEU — 16 Länder capitals
# ---------------------------------------------------------------------------
DEU_CONTRACT = "Gemeindeordnung / GG Art.28"
DEU_CONTRACT_DID = "did:web:gov-deu.etzhayyim.com:law:grundgesetz-art-28"

DEU_CAPITALS = [
    ("land:baden-wuerttemberg:stuttgart",     "Stuttgart",  "Stuttgart",  None, 635000,   "https://www.stuttgart.de/",    "capital", "land:baden-wuerttemberg"),
    ("land:bayern:muenchen",                  "München",    "Munich",     None, 1488000,  "https://www.muenchen.de/",     "capital", "land:bayern"),
    ("land:berlin:berlin",                    "Berlin",     "Berlin",     None, 3644826,  "https://www.berlin.de/",       "capital", "land:berlin"),
    ("land:brandenburg:potsdam",              "Potsdam",    "Potsdam",    None, 183000,   "https://www.potsdam.de/",      "capital", "land:brandenburg"),
    ("land:bremen:bremen",                    "Bremen",     "Bremen",     None, 569000,   "https://www.bremen.de/",       "capital", "land:bremen"),
    ("land:hamburg:hamburg",                  "Hamburg",    "Hamburg",    None, 1841000,  "https://www.hamburg.de/",      "capital", "land:hamburg"),
    ("land:hessen:wiesbaden",                 "Wiesbaden",  "Wiesbaden",  None, 279000,   "https://www.wiesbaden.de/",    "capital", "land:hessen"),
    ("land:mecklenburg-vorpommern:schwerin",  "Schwerin",   "Schwerin",   None, 96000,    "https://www.schwerin.de/",     "capital", "land:mecklenburg-vorpommern"),
    ("land:niedersachsen:hannover",           "Hannover",   "Hannover",   None, 532000,   "https://www.hannover.de/",     "capital", "land:niedersachsen"),
    ("land:nordrhein-westfalen:duesseldorf",  "Düsseldorf", "Dusseldorf", None, 619000,   "https://www.duesseldorf.de/",  "capital", "land:nordrhein-westfalen"),
    ("land:rheinland-pfalz:mainz",            "Mainz",      "Mainz",      None, 218000,   "https://www.mainz.de/",        "capital", "land:rheinland-pfalz"),
    ("land:saarland:saarbruecken",            "Saarbrücken","Saarbrucken", None, 180000,   "https://www.saarbruecken.de/", "capital", "land:saarland"),
    ("land:sachsen:dresden",                  "Dresden",    "Dresden",    None, 554000,   "https://www.dresden.de/",      "capital", "land:sachsen"),
    ("land:sachsen-anhalt:magdeburg",         "Magdeburg",  "Magdeburg",  None, 237000,   "https://www.magdeburg.de/",    "capital", "land:sachsen-anhalt"),
    ("land:schleswig-holstein:kiel",          "Kiel",       "Kiel",       None, 247000,   "https://www.kiel.de/",         "capital", "land:schleswig-holstein"),
    ("land:thueringen:erfurt",                "Erfurt",     "Erfurt",     None, 213000,   "https://www.erfurt.de/",       "capital", "land:thueringen"),
]

# ---------------------------------------------------------------------------
# FRA — 13 région capitals
# ---------------------------------------------------------------------------
FRA_CONTRACT = "Code général des collectivités territoriales"
FRA_CONTRACT_DID = "did:web:gov-fra.etzhayyim.com:law:cgct"

FRA_CAPITALS = [
    ("region:ile-de-france:paris",                  "Paris",      "Paris",      None, 2161000, "https://www.paris.fr/",               "capital", "region:ile-de-france"),
    ("region:auvergne-rhone-alpes:lyon",            "Lyon",       "Lyon",       None, 522000,  "https://www.lyon.fr/",                "capital", "region:auvergne-rhone-alpes"),
    ("region:nouvelle-aquitaine:bordeaux",          "Bordeaux",   "Bordeaux",   None, 254000,  "https://www.bordeaux.fr/",            "capital", "region:nouvelle-aquitaine"),
    ("region:occitanie:toulouse",                   "Toulouse",   "Toulouse",   None, 479000,  "https://www.toulouse.fr/",            "capital", "region:occitanie"),
    ("region:hauts-de-france:lille",                "Lille",      "Lille",      None, 232000,  "https://www.lille.fr/",               "capital", "region:hauts-de-france"),
    ("region:grand-est:strasbourg",                 "Strasbourg", "Strasbourg", None, 284000,  "https://www.strasbourg.eu/",          "capital", "region:grand-est"),
    ("region:pays-de-la-loire:nantes",              "Nantes",     "Nantes",     None, 314000,  "https://www.nantes.fr/",              "capital", "region:pays-de-la-loire"),
    ("region:provence-alpes-cote-dazur:marseille",  "Marseille",  "Marseille",  None, 861000,  "https://www.marseille.fr/",           "capital", "region:provence-alpes-cote-dazur"),
    ("region:normandie:rouen",                      "Rouen",      "Rouen",      None, 112000,  "https://www.rouen.fr/",               "capital", "region:normandie"),
    ("region:bretagne:rennes",                      "Rennes",     "Rennes",     None, 216000,  "https://metropole.rennes.fr/",        "capital", "region:bretagne"),
    ("region:bourgogne-franche-comte:dijon",        "Dijon",      "Dijon",      None, 156000,  "https://www.dijon.fr/",               "capital", "region:bourgogne-franche-comte"),
    ("region:centre-val-de-loire:orleans",          "Orléans",    "Orleans",    None, 117000,  "https://www.orleans.fr/",             "capital", "region:centre-val-de-loire"),
    ("region:corse:ajaccio",                        "Ajaccio",    "Ajaccio",    None, 70000,   "https://www.ajaccio.fr/",             "capital", "region:corse"),
]

# ---------------------------------------------------------------------------
# GBR — major cities
# ---------------------------------------------------------------------------
GBR_CONTRACT = "Local Government Act 1972"
GBR_CONTRACT_DID = "did:web:gov-gbr.etzhayyim.com:law:local-government-act-1972"

GBR_CITIES = [
    ("nation:england:london",           "London",          "London",          None, 8799800, "https://www.london.gov.uk/",          "metropolitan", "nation:england"),
    ("nation:england:manchester",       "Manchester",      "Manchester",      None, 553000,  "https://www.manchester.gov.uk/",      "city",         "nation:england"),
    ("nation:england:birmingham",       "Birmingham",      "Birmingham",      None, 1144900, "https://www.birmingham.gov.uk/",      "city",         "nation:england"),
    ("nation:england:leeds",            "Leeds",           "Leeds",           None, 812000,  "https://www.leeds.gov.uk/",           "city",         "nation:england"),
    ("nation:england:bristol",          "Bristol",         "Bristol",         None, 463000,  "https://www.bristol.gov.uk/",         "city",         "nation:england"),
    ("nation:wales:cardiff",            "Cardiff",         "Cardiff",         None, 362400,  "https://www.cardiff.gov.uk/",         "capital",      "nation:wales"),
    ("nation:scotland:edinburgh",       "Edinburgh",       "Edinburgh",       None, 536000,  "https://www.edinburgh.gov.uk/",       "capital",      "nation:scotland"),
    ("nation:scotland:glasgow",         "Glasgow",         "Glasgow",         None, 635000,  "https://www.glasgow.gov.uk/",         "city",         "nation:scotland"),
    ("nation:northern-ireland:belfast", "Belfast",         "Belfast",         None, 345000,  "https://www.belfastcity.gov.uk/",     "capital",      "nation:northern-ireland"),
]

# ---------------------------------------------------------------------------
# ITA — 20 regional capitals (+ extras)
# ---------------------------------------------------------------------------
ITA_CONTRACT = "TUEL D.Lgs. 267/2000"
ITA_CONTRACT_DID = "did:web:gov-ita.etzhayyim.com:law:tuel-2000"

ITA_CAPITALS = [
    ("regione:lazio:roma",                         "Roma",            "Rome",           None, 2873494, "https://www.comune.roma.it/",                "capital", "regione:lazio"),
    ("regione:lombardia:milano",                   "Milano",          "Milan",          None, 1371498, "https://www.comune.milano.it/",              "capital", "regione:lombardia"),
    ("regione:campania:napoli",                    "Napoli",          "Naples",         None, 959052,  "https://www.comune.napoli.it/",              "capital", "regione:campania"),
    ("regione:piemonte:torino",                    "Torino",          "Turin",          None, 870456,  "https://www.comune.torino.it/",              "capital", "regione:piemonte"),
    ("regione:sicilia:palermo",                    "Palermo",         "Palermo",        None, 663401,  "https://www.comune.palermo.it/",             "capital", "regione:sicilia"),
    ("regione:liguria:genova",                     "Genova",          "Genoa",          None, 586655,  "https://www.comune.genova.it/",              "capital", "regione:liguria"),
    ("regione:emilia-romagna:bologna",             "Bologna",         "Bologna",        None, 413502,  "https://www.comune.bologna.it/",             "capital", "regione:emilia-romagna"),
    ("regione:toscana:firenze",                    "Firenze",         "Florence",       None, 382258,  "https://www.comune.fi.it/",                  "capital", "regione:toscana"),
    ("regione:puglia:bari",                        "Bari",            "Bari",           None, 320657,  "https://www.comune.bari.it/",                "capital", "regione:puglia"),
    ("regione:veneto:venezia",                     "Venezia",         "Venice",         None, 258685,  "https://www.comune.venezia.it/",             "capital", "regione:veneto"),
    ("regione:veneto:verona",                      "Verona",          "Verona",         None, 257353,  "https://www.comune.verona.it/",              "city",    "regione:veneto"),
    ("regione:sicilia:messina",                    "Messina",         "Messina",        None, 228247,  "https://www.comune.messina.it/",             "city",    "regione:sicilia"),
    ("regione:sicilia:catania",                    "Catania",         "Catania",        None, 313747,  "https://www.comune.catania.it/",             "city",    "regione:sicilia"),
    ("regione:calabria:reggio-calabria",           "Reggio Calabria", "Reggio Calabria",None, 182551,  "https://www.comune.reggio-calabria.it/",     "capital", "regione:calabria"),
    ("regione:trentino-alto-adige:trento",         "Trento",          "Trento",         None, 120000,  "https://www.comune.trento.it/",              "capital", "regione:trentino-alto-adige"),
    ("regione:friuli-venezia-giulia:trieste",      "Trieste",         "Trieste",        None, 205338,  "https://www.comune.trieste.it/",             "capital", "regione:friuli-venezia-giulia"),
    ("regione:umbria:perugia",                     "Perugia",         "Perugia",        None, 165683,  "https://www.comune.perugia.it/",             "capital", "regione:umbria"),
    ("regione:abruzzo:laquila",                    "L'Aquila",        "L'Aquila",       None, 68503,   "https://www.comune.laquila.it/",             "capital", "regione:abruzzo"),
    ("regione:molise:campobasso",                  "Campobasso",      "Campobasso",     None, 49048,   "https://www.comune.campobasso.it/",          "capital", "regione:molise"),
    ("regione:basilicata:potenza",                 "Potenza",         "Potenza",        None, 67122,   "https://www.comune.potenza.it/",             "capital", "regione:basilicata"),
    ("regione:sardegna:cagliari",                  "Cagliari",        "Cagliari",       None, 154083,  "https://www.comune.cagliari.it/",            "capital", "regione:sardegna"),
    ("regione:calabria:catanzaro",                 "Catanzaro",       "Catanzaro",      None, 89662,   "https://www.comune.catanzaro.it/",           "city",    "regione:calabria"),
    ("regione:marche:ancona",                      "Ancona",          "Ancona",         None, 101997,  "https://www.comune.ancona.it/",              "capital", "regione:marche"),
    ("regione:valle-daosta:aosta",                 "Aosta",           "Aosta",          None, 33561,   "https://www.comune.aosta.it/",               "capital", "regione:valle-daosta"),
]

# ---------------------------------------------------------------------------
# CAN — provincial/territorial capitals
# ---------------------------------------------------------------------------
CAN_CONTRACT = "Municipal Government Acts (provincial)"
CAN_CONTRACT_DID = "did:web:gov-can.etzhayyim.com:law:constitution-act-1867"

CAN_CITIES = [
    ("province:ontario:ottawa",                         "Ottawa",       "Ottawa",       None, 1017449,  "https://ottawa.ca/",                    "capital",  "province:ontario"),
    ("province:ontario:toronto",                        "Toronto",      "Toronto",      None, 2794356,  "https://www.toronto.ca/",               "city",     "province:ontario"),
    ("province:quebec:quebec-city",                     "Quebec City",  "Quebec City",  None, 549459,   "https://www.ville.quebec.qc.ca/",       "capital",  "province:quebec"),
    ("province:quebec:montreal",                        "Montreal",     "Montreal",     None, 2037000,  "https://montreal.ca/",                  "city",     "province:quebec"),
    ("province:british-columbia:vancouver",             "Vancouver",    "Vancouver",    None, 662248,   "https://vancouver.ca/",                 "city",     "province:british-columbia"),
    ("province:british-columbia:victoria",              "Victoria",     "Victoria",     None, 91867,    "https://www.victoria.ca/",              "capital",  "province:british-columbia"),
    ("province:alberta:edmonton",                       "Edmonton",     "Edmonton",     None, 1010899,  "https://www.edmonton.ca/",              "capital",  "province:alberta"),
    ("province:alberta:calgary",                        "Calgary",      "Calgary",      None, 1336000,  "https://www.calgary.ca/",               "city",     "province:alberta"),
    ("province:manitoba:winnipeg",                      "Winnipeg",     "Winnipeg",     None, 749607,   "https://www.winnipeg.ca/",              "capital",  "province:manitoba"),
    ("province:saskatchewan:regina",                    "Regina",       "Regina",       None, 215106,   "https://www.regina.ca/",                "capital",  "province:saskatchewan"),
    ("province:nova-scotia:halifax",                    "Halifax",      "Halifax",      None, 348634,   "https://www.halifax.ca/",               "capital",  "province:nova-scotia"),
    ("province:new-brunswick:fredericton",              "Fredericton",  "Fredericton",  None, 63116,    "https://www.fredericton.ca/",           "capital",  "province:new-brunswick"),
    ("province:prince-edward-island:charlottetown",     "Charlottetown","Charlottetown",None, 38809,    "https://www.charlottetown.ca/",         "capital",  "province:prince-edward-island"),
    ("province:newfoundland-and-labrador:st-johns",     "St. John's",   "St. John's",   None, 110525,   "https://www.stjohns.ca/",               "capital",  "province:newfoundland-and-labrador"),
    ("territory:yukon:whitehorse",                      "Whitehorse",   "Whitehorse",   None, 25085,    "https://www.whitehorse.ca/",            "capital",  "territory:yukon"),
    ("territory:northwest-territories:yellowknife",     "Yellowknife",  "Yellowknife",  None, 19569,    "https://www.yellowknife.ca/",           "capital",  "territory:northwest-territories"),
    ("territory:nunavut:iqaluit",                       "Iqaluit",      "Iqaluit",      None, 7429,     "https://www.city.iqaluit.nu.ca/",       "capital",  "territory:nunavut"),
]

# ---------------------------------------------------------------------------
# AUS — state/territory capitals
# ---------------------------------------------------------------------------
AUS_CONTRACT = "Local Government Act (state)"
AUS_CONTRACT_DID = "did:web:gov-aus.etzhayyim.com:law:local-government-act"

AUS_CAPITALS = [
    ("state:new-south-wales:sydney",    "Sydney",    "Sydney",    None, 5312000, "https://www.cityofsydney.nsw.gov.au/", "capital", "state:new-south-wales"),
    ("state:victoria:melbourne",        "Melbourne", "Melbourne", None, 5078000, "https://www.melbourne.vic.gov.au/",    "capital", "state:victoria"),
    ("state:queensland:brisbane",       "Brisbane",  "Brisbane",  None, 2360241, "https://www.brisbane.qld.gov.au/",     "capital", "state:queensland"),
    ("state:western-australia:perth",   "Perth",     "Perth",     None, 2024000, "https://www.perth.wa.gov.au/",         "capital", "state:western-australia"),
    ("state:south-australia:adelaide",  "Adelaide",  "Adelaide",  None, 1376601, "https://www.cityofadelaide.com.au/",   "capital", "state:south-australia"),
    ("state:tasmania:hobart",           "Hobart",    "Hobart",    None, 238834,  "https://www.hobartcity.com.au/",       "capital", "state:tasmania"),
    ("territory:northern-territory:darwin", "Darwin","Darwin",    None, 147231,  "https://www.darwin.nt.gov.au/",        "capital", "territory:northern-territory"),
    ("territory:act:canberra",          "Canberra",  "Canberra",  None, 454499,  "https://www.cityservices.act.gov.au/", "capital", "territory:act"),
]

# ---------------------------------------------------------------------------
# KOR — 17 시도 capitals
# ---------------------------------------------------------------------------
KOR_CONTRACT = "지방자치법"
KOR_CONTRACT_DID = "did:web:gov-kor.etzhayyim.com:law:local-autonomy-act"

KOR_CAPITALS = [
    ("gwangyeok:seoul:seoul",           "서울특별시",     "Seoul",      None, 9720846,  "https://english.seoul.go.kr/",         "metropolitan", "gwangyeok:seoul"),
    ("gwangyeok:busan:busan",           "부산광역시",     "Busan",      None, 3350380,  "https://www.busan.go.kr/",             "metropolitan", "gwangyeok:busan"),
    ("gwangyeok:daegu:daegu",           "대구광역시",     "Daegu",      None, 2418346,  "https://www.daegu.go.kr/",             "metropolitan", "gwangyeok:daegu"),
    ("gwangyeok:incheon:incheon",       "인천광역시",     "Incheon",    None, 2942828,  "https://www.incheon.go.kr/",           "metropolitan", "gwangyeok:incheon"),
    ("gwangyeok:gwangju:gwangju",       "광주광역시",     "Gwangju",    None, 1441585,  "https://www.gwangju.go.kr/",           "metropolitan", "gwangyeok:gwangju"),
    ("gwangyeok:daejeon:daejeon",       "대전광역시",     "Daejeon",    None, 1463882,  "https://www.daejeon.go.kr/",           "metropolitan", "gwangyeok:daejeon"),
    ("gwangyeok:ulsan:ulsan",           "울산광역시",     "Ulsan",      None, 1136017,  "https://www.ulsan.go.kr/",             "metropolitan", "gwangyeok:ulsan"),
    ("gwangyeok:sejong:sejong",         "세종특별자치시", "Sejong",     None, 388000,   "https://www.sejong.go.kr/",            "city",         "gwangyeok:sejong"),
    ("gwangyeok:gyeonggi:suwon",        "경기도 수원시",  "Suwon",      None, 1194313,  "https://www.suwon.go.kr/",             "city",         "gwangyeok:gyeonggi"),
    ("gwangyeok:gangwon:chuncheon",     "강원도 춘천시",  "Chuncheon",  None, 283000,   "https://www.chuncheon.go.kr/",         "city",         "gwangyeok:gangwon"),
    ("gwangyeok:chungbuk:cheongju",     "충청북도 청주시","Cheongju",   None, 845000,   "https://www.cheongju.go.kr/",          "city",         "gwangyeok:chungbuk"),
    ("gwangyeok:chungnam:hongseong",    "충청남도 홍성군","Hongseong",  None, 97000,    "https://www.hongseong.go.kr/",         "county",       "gwangyeok:chungnam"),
    ("gwangyeok:jeonbuk:jeonju",        "전라북도 전주시","Jeonju",     None, 659000,   "https://www.jeonju.go.kr/",            "city",         "gwangyeok:jeonbuk"),
    ("gwangyeok:jeonnam:muan",          "전라남도 무안군","Muan",       None, 83000,    "https://www.muan.go.kr/",              "county",       "gwangyeok:jeonnam"),
    ("gwangyeok:gyeongbuk:andong",      "경상북도 안동시","Andong",     None, 159000,   "https://www.andong.go.kr/",            "city",         "gwangyeok:gyeongbuk"),
    ("gwangyeok:gyeongnam:changwon",    "경상남도 창원시","Changwon",   None, 1044000,  "https://www.changwon.go.kr/",          "city",         "gwangyeok:gyeongnam"),
    ("gwangyeok:jeju:jeju",             "제주특별자치도 제주시","Jeju",  None, 489000,   "https://www.jeju.go.kr/",              "city",         "gwangyeok:jeju"),
]

# ---------------------------------------------------------------------------
# IND — state/UT capitals
# ---------------------------------------------------------------------------
IND_CONTRACT = "74th Constitutional Amendment Act 1992"
IND_CONTRACT_DID = "did:web:gov-ind.etzhayyim.com:law:constitution-74th-amendment"

IND_CAPITALS = [
    ("ut:delhi:new-delhi",                        "New Delhi",          "New Delhi",          None, 11034555, "https://www.mcdonline.nic.in/",                 "capital", "ut:delhi"),
    ("state:maharashtra:mumbai",                  "Mumbai",             "Mumbai",             None, 12442373, "https://www.mcgm.gov.in/",                      "capital", "state:maharashtra"),
    ("state:west-bengal:kolkata",                 "Kolkata",            "Kolkata",            None, 4496694,  "https://www.kmcgov.in/",                        "capital", "state:west-bengal"),
    ("state:tamil-nadu:chennai",                  "Chennai",            "Chennai",            None, 7088000,  "https://www.chennaicorporation.gov.in/",         "capital", "state:tamil-nadu"),
    ("state:karnataka:bangalore",                 "Bangalore",          "Bangalore",          None, 8443675,  "https://bbmp.gov.in/",                          "capital", "state:karnataka"),
    ("state:telangana:hyderabad",                 "Hyderabad",          "Hyderabad",          None, 6993262,  "https://ghmc.telangana.gov.in/",                "capital", "state:telangana"),
    ("state:gujarat:ahmedabad",                   "Ahmedabad",          "Ahmedabad",          None, 5633927,  "https://ahmedabadcity.gov.in/",                 "capital", "state:gujarat"),
    ("state:uttar-pradesh:lucknow",               "Lucknow",            "Lucknow",            None, 2901474,  "https://www.lmc.up.nic.in/",                    "capital", "state:uttar-pradesh"),
    ("state:rajasthan:jaipur",                    "Jaipur",             "Jaipur",             None, 3046163,  "https://jaipurmc.org/",                         "capital", "state:rajasthan"),
    ("state:madhya-pradesh:bhopal",               "Bhopal",             "Bhopal",             None, 1798218,  "https://www.bhopalmunicipal.com/",              "capital", "state:madhya-pradesh"),
    ("state:bihar:patna",                         "Patna",              "Patna",              None, 1684222,  "https://www.pmc.bihar.gov.in/",                 "capital", "state:bihar"),
    ("ut:chandigarh:chandigarh",                  "Chandigarh",         "Chandigarh",         None, 960787,   "https://www.chandigarh.gov.in/",                "capital", "ut:chandigarh"),
    ("state:odisha:bhubaneswar",                  "Bhubaneswar",        "Bhubaneswar",        None, 837737,   "https://www.bmc.gov.in/",                       "capital", "state:odisha"),
    ("state:jharkhand:ranchi",                    "Ranchi",             "Ranchi",             None, 1073427,  "https://www.ranchimc.in/",                      "capital", "state:jharkhand"),
    ("state:chhattisgarh:raipur",                 "Raipur",             "Raipur",             None, 1010087,  "https://www.raipur.gov.in/",                    "capital", "state:chhattisgarh"),
    ("state:uttarakhand:dehradun",                "Dehradun",           "Dehradun",           None, 578420,   "https://ddmcorp.in/",                           "capital", "state:uttarakhand"),
    ("state:himachal-pradesh:shimla",             "Shimla",             "Shimla",             None, 171817,   "https://www.shimlamc.org/",                     "capital", "state:himachal-pradesh"),
    ("state:jammu-and-kashmir:srinagar",          "Srinagar",           "Srinagar",           None, 1192792,  "https://smcjk.nic.in/",                         "capital", "state:jammu-and-kashmir"),
    ("state:manipur:imphal",                      "Imphal",             "Imphal",             None, 268243,   "https://imcmanipuregovernance.com/",             "capital", "state:manipur"),
    ("state:meghalaya:shillong",                  "Shillong",           "Shillong",           None, 143229,   "https://meghalaya.gov.in/",                     "capital", "state:meghalaya"),
    ("state:mizoram:aizawl",                      "Aizawl",             "Aizawl",             None, 293416,   "https://aizawl.nic.in/",                        "capital", "state:mizoram"),
    ("state:nagaland:kohima",                     "Kohima",             "Kohima",             None, 99039,    "https://nagaland.gov.in/",                      "capital", "state:nagaland"),
    ("state:arunachal-pradesh:itanagar",          "Itanagar",           "Itanagar",           None, 44971,    "https://itanagar.nic.in/",                      "capital", "state:arunachal-pradesh"),
    ("state:sikkim:gangtok",                      "Gangtok",            "Gangtok",            None, 100286,   "https://www.gangtokmc.in/",                     "capital", "state:sikkim"),
    ("state:assam:guwahati",                      "Guwahati",           "Guwahati",           None, 962334,   "https://gmc.gov.in/",                           "capital", "state:assam"),
    ("state:tripura:agartala",                    "Agartala",           "Agartala",           None, 438853,   "https://www.amc.gov.in/",                       "capital", "state:tripura"),
    ("state:goa:panaji",                          "Panaji",             "Panaji",             None, 114759,   "https://panaji.gov.in/",                        "capital", "state:goa"),
    ("state:kerala:thiruvananthapuram",           "Thiruvananthapuram", "Thiruvananthapuram", None, 957730,   "https://www.corporationoftrivandrum.in/",        "capital", "state:kerala"),
    ("ut:ladakh:leh",                             "Leh",                "Leh",                None, 27513,    "https://lahdc.nic.in/",                         "capital", "ut:ladakh"),
]

# ---------------------------------------------------------------------------
# BRA — state capitals
# ---------------------------------------------------------------------------
BRA_CONTRACT = "Constituição Federal Art.29-31"
BRA_CONTRACT_DID = "did:web:gov-bra.etzhayyim.com:law:constituicao-federal-art-29"

BRA_CAPITALS = [
    ("df:distrito-federal:brasilia",                     "Brasília",       "Brasilia",       None, 2817068,  "https://www.agefis.df.gov.br/",             "capital", "df:distrito-federal"),
    ("estado:sao-paulo:sao-paulo",                       "São Paulo",      "Sao Paulo",      None, 11451245, "https://www.prefeitura.sp.gov.br/",         "capital", "estado:sao-paulo"),
    ("estado:rio-de-janeiro:rio-de-janeiro",             "Rio de Janeiro", "Rio de Janeiro", None, 6211223,  "https://prefeitura.rio/",                   "capital", "estado:rio-de-janeiro"),
    ("estado:minas-gerais:belo-horizonte",               "Belo Horizonte", "Belo Horizonte", None, 2315560,  "https://prefeitura.pbh.gov.br/",            "capital", "estado:minas-gerais"),
    ("estado:bahia:salvador",                            "Salvador",       "Salvador",       None, 2417678,  "https://www.salvador.ba.gov.br/",           "capital", "estado:bahia"),
    ("estado:ceara:fortaleza",                           "Fortaleza",      "Fortaleza",      None, 2452185,  "https://www.fortaleza.ce.gov.br/",          "capital", "estado:ceara"),
    ("estado:amazonas:manaus",                           "Manaus",         "Manaus",         None, 1802014,  "https://www.manaus.am.gov.br/",             "capital", "estado:amazonas"),
    ("estado:parana:curitiba",                           "Curitiba",       "Curitiba",       None, 1749130,  "https://www.curitiba.pr.gov.br/",           "capital", "estado:parana"),
    ("estado:pernambuco:recife",                         "Recife",         "Recife",         None, 1488920,  "https://www2.recife.pe.gov.br/",            "capital", "estado:pernambuco"),
    ("estado:rio-grande-do-sul:porto-alegre",            "Porto Alegre",   "Porto Alegre",   None, 1332570,  "https://prefeitura.poa.br/",                "capital", "estado:rio-grande-do-sul"),
    ("estado:para:belem",                                "Belém",          "Belem",          None, 1303389,  "https://www.belem.pa.gov.br/",              "capital", "estado:para"),
    ("estado:goias:goiania",                             "Goiânia",        "Goiania",        None, 1302001,  "https://www.goiania.go.gov.br/",            "capital", "estado:goias"),
    ("estado:maranhao:sao-luis",                         "São Luís",       "Sao Luis",       None, 1003396,  "https://www.saoluis.ma.gov.br/",            "capital", "estado:maranhao"),
    ("estado:alagoas:maceio",                            "Maceió",         "Maceio",         None, 932748,   "https://www.maceio.al.gov.br/",             "capital", "estado:alagoas"),
    ("estado:rio-grande-do-norte:natal",                 "Natal",          "Natal",          None, 803739,   "https://natal.rn.gov.br/",                  "capital", "estado:rio-grande-do-norte"),
    ("estado:piaui:teresina",                            "Teresina",       "Teresina",       None, 814230,   "https://semplan.teresina.pi.gov.br/",       "capital", "estado:piaui"),
    ("estado:mato-grosso-do-sul:campo-grande",           "Campo Grande",   "Campo Grande",   None, 906092,   "https://www.campogrande.ms.gov.br/",        "capital", "estado:mato-grosso-do-sul"),
    ("estado:paraiba:joao-pessoa",                       "João Pessoa",    "Joao Pessoa",    None, 800323,   "https://www.joaopessoa.pb.gov.br/",         "capital", "estado:paraiba"),
    ("estado:sergipe:aracaju",                           "Aracaju",        "Aracaju",        None, 641523,   "https://www.aracaju.se.gov.br/",            "capital", "estado:sergipe"),
    ("estado:rondonia:porto-velho",                      "Porto Velho",    "Porto Velho",    None, 428527,   "https://www.portovelho.ro.gov.br/",         "capital", "estado:rondonia"),
    ("estado:mato-grosso:cuiaba",                        "Cuiabá",         "Cuiaba",         None, 594828,   "https://www.cuiaba.mt.gov.br/",             "capital", "estado:mato-grosso"),
    ("estado:amapa:macapa",                              "Macapá",         "Macapa",         None, 503327,   "https://www.macapa.ap.gov.br/",             "capital", "estado:amapa"),
    ("estado:acre:rio-branco",                           "Rio Branco",     "Rio Branco",     None, 363928,   "https://riobranco.ac.gov.br/",              "capital", "estado:acre"),
    ("estado:roraima:boa-vista",                         "Boa Vista",      "Boa Vista",      None, 399213,   "https://www.boavista.rr.gov.br/",           "capital", "estado:roraima"),
    ("estado:santa-catarina:florianopolis",              "Florianópolis",  "Florianopolis",  None, 508826,   "https://www.pmf.sc.gov.br/",                "capital", "estado:santa-catarina"),
    ("estado:espirito-santo:vitoria",                    "Vitória",        "Vitoria",        None, 354205,   "https://www.vitoria.es.gov.br/",            "capital", "estado:espirito-santo"),
    ("estado:tocantins:palmas",                          "Palmas",         "Palmas",         None, 229907,   "https://www.palmas.to.gov.br/",             "capital", "estado:tocantins"),
]

# ---------------------------------------------------------------------------
# CHN — direct-controlled municipalities
# ---------------------------------------------------------------------------
CHN_CONTRACT = "城市居民委员会组织法"
CHN_CONTRACT_DID = "did:web:gov-chn.etzhayyim.com:law:urban-residents-committees-law"

CHN_CITIES = [
    ("municipality:beijing",   "北京市", "Beijing",  None, 21893095, "https://www.beijing.gov.cn/", "metropolitan", "municipality:beijing"),
    ("municipality:shanghai",  "上海市", "Shanghai", None, 24870895, "https://www.shanghai.gov.cn/","metropolitan", "municipality:shanghai"),
    ("municipality:tianjin",   "天津市", "Tianjin",  None, 13866009, "https://www.tj.gov.cn/",      "metropolitan", "municipality:tianjin"),
    ("municipality:chongqing", "重庆市", "Chongqing",None, 32000000, "https://www.cq.gov.cn/",      "metropolitan", "municipality:chongqing"),
]

# For CHN, parentPath = same as path (direct-controlled, no separate parent)
CHN_PARENT_OVERRIDES = {
    "municipality:beijing":   ("municipality:beijing",   "did:web:gov-chn.etzhayyim.com:municipality:beijing"),
    "municipality:shanghai":  ("municipality:shanghai",  "did:web:gov-chn.etzhayyim.com:municipality:shanghai"),
    "municipality:tianjin":   ("municipality:tianjin",   "did:web:gov-chn.etzhayyim.com:municipality:tianjin"),
    "municipality:chongqing": ("municipality:chongqing", "did:web:gov-chn.etzhayyim.com:municipality:chongqing"),
}

# ---------------------------------------------------------------------------
# RUS
# ---------------------------------------------------------------------------
RUS_CONTRACT = "Федеральный закон 131-ФЗ"
RUS_CONTRACT_DID = "did:web:gov-rus.etzhayyim.com:law:federal-law-131-2003"

RUS_CITIES = [
    ("federal-city:moscow",           "Москва",           "Moscow",           None, 12506468, "https://www.mos.ru/",         "metropolitan", "federal-city:moscow"),
    ("federal-city:saint-petersburg", "Санкт-Петербург",  "Saint Petersburg", None, 5376000,  "https://www.gov.spb.ru/",     "metropolitan", "federal-city:saint-petersburg"),
]

# ---------------------------------------------------------------------------
# MEX
# ---------------------------------------------------------------------------
MEX_CONTRACT = "Constitución Política Art.115"
MEX_CONTRACT_DID = "did:web:gov-mex.etzhayyim.com:law:constitucion-art-115"

MEX_CITIES = [
    ("estado:ciudad-de-mexico:cdmx",    "Ciudad de México", "Mexico City",  None, 9209944,  "https://www.cdmx.gob.mx/",              "capital", "estado:ciudad-de-mexico"),
    ("estado:jalisco:guadalajara",       "Guadalajara",      "Guadalajara",  None, 1385629,  "https://www.guadalajara.gob.mx/",       "capital", "estado:jalisco"),
    ("estado:nuevo-leon:monterrey",      "Monterrey",        "Monterrey",    None, 1142994,  "https://www.monterrey.gob.mx/",         "capital", "estado:nuevo-leon"),
]

# ---------------------------------------------------------------------------
# SAU
# ---------------------------------------------------------------------------
SAU_CONTRACT = "نظام المناطق 1992"
SAU_CONTRACT_DID = "did:web:gov-sau.etzhayyim.com:law:regions-regulation-1992"

SAU_CITIES = [
    ("mintaqah:riyadh:riyadh", "الرياض", "Riyadh", None, 7676654, "https://www.alriyadh.gov.sa/", "capital", "mintaqah:riyadh"),
    ("mintaqah:makkah:jeddah", "جدة",    "Jeddah", None, 4082560, "https://www.jeddah.gov.sa/",   "city",    "mintaqah:makkah"),
]

# ---------------------------------------------------------------------------
# TUR
# ---------------------------------------------------------------------------
TUR_CONTRACT = "Belediye Kanunu 5393"
TUR_CONTRACT_DID = "did:web:gov-tur.etzhayyim.com:law:belediye-kanunu-5393"

TUR_CITIES = [
    ("il:ankara:ankara",   "Ankara",   "Ankara",   None, 5747325,  "https://www.ankara.bel.tr/", "capital", "il:ankara"),
    ("il:istanbul:istanbul","İstanbul", "Istanbul", None, 15840900, "https://www.ibb.istanbul/",  "city",    "il:istanbul"),
]

# ---------------------------------------------------------------------------
# ARG
# ---------------------------------------------------------------------------
ARG_CONTRACT = "Constitución Nacional Art.123"
ARG_CONTRACT_DID = "did:web:gov-arg.etzhayyim.com:law:constitucion-art-123"

ARG_CITIES = [
    ("provincia:buenos-aires:buenos-aires", "Buenos Aires", "Buenos Aires", None, 2890151, "https://buenosaires.gob.ar/",      "capital", "provincia:buenos-aires"),
    ("provincia:cordoba:cordoba",           "Córdoba",      "Cordoba",      None, 1454536, "https://www.cordoba.gob.ar/",      "capital", "provincia:cordoba"),
]

# ---------------------------------------------------------------------------
# ZAF
# ---------------------------------------------------------------------------
ZAF_CONTRACT = "Local Government: Municipal Structures Act 117/1998"
ZAF_CONTRACT_DID = "did:web:gov-zaf.etzhayyim.com:law:municipal-structures-act-1998"

ZAF_CITIES = [
    ("province:gauteng:pretoria",        "Pretoria",     "Pretoria",     None, 741651,   "https://www.tshwane.gov.za/",     "capital", "province:gauteng"),
    ("province:western-cape:cape-town",  "Cape Town",    "Cape Town",    None, 4618000,  "https://www.capetown.gov.za/",    "capital", "province:western-cape"),
    ("province:gauteng:johannesburg",    "Johannesburg", "Johannesburg", None, 5635127,  "https://www.joburg.org.za/",      "city",    "province:gauteng"),
]

# ---------------------------------------------------------------------------
# IDN
# ---------------------------------------------------------------------------
IDN_CONTRACT = "UU No.23 Tahun 2014"
IDN_CONTRACT_DID = "did:web:gov-idn.etzhayyim.com:law:uu-23-2014"

IDN_CITIES = [
    ("special-region:jakarta:jakarta",  "Jakarta",  "Jakarta",  None, 10562088, "https://jakarta.go.id/",         "capital", "special-region:jakarta"),
    ("province:east-java:surabaya",     "Surabaya", "Surabaya", None, 2874314,  "https://surabaya.go.id/",        "city",    "province:east-java"),
    ("province:west-java:bandung",      "Bandung",  "Bandung",  None, 2444160,  "https://www.bandung.go.id/",     "city",    "province:west-java"),
]

# ---------------------------------------------------------------------------
# ESP
# ---------------------------------------------------------------------------
ESP_CONTRACT = CONTRACTS["esp"][1]
ESP_CONTRACT_DID = f"did:web:gov-esp.etzhayyim.com:law:{CONTRACTS['esp'][2]}"

ESP_CITIES = [
    ("city:madrid", "Madrid", "Madrid", None, 3300000, "https://www.madrid.es/", "capital", "capital-district"),
    ("city:barcelona", "Barcelona", "Barcelona", None, 1620000, "https://www.bcn.cat/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# NLD
# ---------------------------------------------------------------------------
NLD_CONTRACT = CONTRACTS["nld"][1]
NLD_CONTRACT_DID = f"did:web:gov-nld.etzhayyim.com:law:{CONTRACTS['nld'][2]}"

NLD_CITIES = [
    ("city:amsterdam", "Amsterdam", "Amsterdam", None, 872680, "https://www.amsterdam.nl/", "capital", "capital-district"),
    ("city:the-hague", "Den Haag", "The Hague", None, 545000, "https://www.denhaag.nl/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BEL
# ---------------------------------------------------------------------------
BEL_CONTRACT = CONTRACTS["bel"][1]
BEL_CONTRACT_DID = f"did:web:gov-bel.etzhayyim.com:law:{CONTRACTS['bel'][2]}"

BEL_CITIES = [
    ("city:brussels", "Bruxelles", "Brussels", None, 185000, "https://www.brussels.be/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CHE
# ---------------------------------------------------------------------------
CHE_CONTRACT = CONTRACTS["che"][1]
CHE_CONTRACT_DID = f"did:web:gov-che.etzhayyim.com:law:{CONTRACTS['che'][2]}"

CHE_CITIES = [
    ("city:bern", "Bern", "Bern", None, 133115, "https://www.bern.ch/", "capital", "capital-district"),
    ("city:zurich", "Zürich", "Zurich", None, 402762, "https://www.stadt-zuerich.ch/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# AUT
# ---------------------------------------------------------------------------
AUT_CONTRACT = CONTRACTS["aut"][1]
AUT_CONTRACT_DID = f"did:web:gov-aut.etzhayyim.com:law:{CONTRACTS['aut'][2]}"

AUT_CITIES = [
    ("city:vienna", "Wien", "Vienna", None, 1897000, "https://www.wien.gv.at/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# POL
# ---------------------------------------------------------------------------
POL_CONTRACT = CONTRACTS["pol"][1]
POL_CONTRACT_DID = f"did:web:gov-pol.etzhayyim.com:law:{CONTRACTS['pol'][2]}"

POL_CITIES = [
    ("city:warsaw", "Warszawa", "Warsaw", None, 1794166, "https://www.um.warszawa.pl/", "capital", "capital-district"),
    ("city:krakow", "Kraków", "Krakow", None, 779115, "https://www.krakow.pl/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# SWE
# ---------------------------------------------------------------------------
SWE_CONTRACT = CONTRACTS["swe"][1]
SWE_CONTRACT_DID = f"did:web:gov-swe.etzhayyim.com:law:{CONTRACTS['swe'][2]}"

SWE_CITIES = [
    ("city:stockholm", "Stockholm", "Stockholm", None, 975551, "https://start.stockholm/", "capital", "capital-district"),
    ("city:gothenburg", "Göteborg", "Gothenburg", None, 583056, "https://goteborg.se/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# NOR
# ---------------------------------------------------------------------------
NOR_CONTRACT = CONTRACTS["nor"][1]
NOR_CONTRACT_DID = f"did:web:gov-nor.etzhayyim.com:law:{CONTRACTS['nor'][2]}"

NOR_CITIES = [
    ("city:oslo", "Oslo", "Oslo", None, 693494, "https://www.oslo.kommune.no/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# DNK
# ---------------------------------------------------------------------------
DNK_CONTRACT = CONTRACTS["dnk"][1]
DNK_CONTRACT_DID = f"did:web:gov-dnk.etzhayyim.com:law:{CONTRACTS['dnk'][2]}"

DNK_CITIES = [
    ("city:copenhagen", "København", "Copenhagen", None, 794128, "https://www.kk.dk/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# FIN
# ---------------------------------------------------------------------------
FIN_CONTRACT = CONTRACTS["fin"][1]
FIN_CONTRACT_DID = f"did:web:gov-fin.etzhayyim.com:law:{CONTRACTS['fin'][2]}"

FIN_CITIES = [
    ("city:helsinki", "Helsinki", "Helsinki", None, 656229, "https://www.hel.fi/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# PRT
# ---------------------------------------------------------------------------
PRT_CONTRACT = CONTRACTS["prt"][1]
PRT_CONTRACT_DID = f"did:web:gov-prt.etzhayyim.com:law:{CONTRACTS['prt'][2]}"

PRT_CITIES = [
    ("city:lisbon", "Lisboa", "Lisbon", None, 545245, "https://www.cm-lisboa.pt/", "capital", "capital-district"),
    ("city:porto", "Porto", "Porto", None, 237591, "https://www.cm-porto.pt/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# GRC
# ---------------------------------------------------------------------------
GRC_CONTRACT = CONTRACTS["grc"][1]
GRC_CONTRACT_DID = f"did:web:gov-grc.etzhayyim.com:law:{CONTRACTS['grc'][2]}"

GRC_CITIES = [
    ("city:athens", "Αθήνα", "Athens", None, 664046, "https://www.cityofathens.gr/", "capital", "capital-district"),
    ("city:thessaloniki", "Θεσσαλονίκη", "Thessaloniki", None, 325182, "https://www.thessaloniki.gr/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# CZE
# ---------------------------------------------------------------------------
CZE_CONTRACT = CONTRACTS["cze"][1]
CZE_CONTRACT_DID = f"did:web:gov-cze.etzhayyim.com:law:{CONTRACTS['cze'][2]}"

CZE_CITIES = [
    ("city:prague", "Praha", "Prague", None, 1335084, "https://www.praha.eu/", "capital", "capital-district"),
    ("city:brno", "Brno", "Brno", None, 382405, "https://www.brno.cz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# HUN
# ---------------------------------------------------------------------------
HUN_CONTRACT = CONTRACTS["hun"][1]
HUN_CONTRACT_DID = f"did:web:gov-hun.etzhayyim.com:law:{CONTRACTS['hun'][2]}"

HUN_CITIES = [
    ("city:budapest", "Budapest", "Budapest", None, 1752286, "https://budapest.hu/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ROU
# ---------------------------------------------------------------------------
ROU_CONTRACT = CONTRACTS["rou"][1]
ROU_CONTRACT_DID = f"did:web:gov-rou.etzhayyim.com:law:{CONTRACTS['rou'][2]}"

ROU_CITIES = [
    ("city:bucharest", "București", "Bucharest", None, 1716983, "https://www.pmb.ro/", "capital", "capital-district"),
    ("city:cluj-napoca", "Cluj-Napoca", "Cluj-Napoca", None, 324576, "https://www.primariaclujnapoca.ro/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# UKR
# ---------------------------------------------------------------------------
UKR_CONTRACT = CONTRACTS["ukr"][1]
UKR_CONTRACT_DID = f"did:web:gov-ukr.etzhayyim.com:law:{CONTRACTS['ukr'][2]}"

UKR_CITIES = [
    ("city:kyiv", "Київ", "Kyiv", None, 2952301, "https://kyivcity.gov.ua/", "capital", "capital-district"),
    ("city:kharkiv", "Харків", "Kharkiv", None, 1443211, "https://www.city.kharkov.ua/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BGR
# ---------------------------------------------------------------------------
BGR_CONTRACT = CONTRACTS["bgr"][1]
BGR_CONTRACT_DID = f"did:web:gov-bgr.etzhayyim.com:law:{CONTRACTS['bgr'][2]}"

BGR_CITIES = [
    ("city:sofia", "София", "Sofia", None, 1241675, "https://www.sofia.bg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# HRV
# ---------------------------------------------------------------------------
HRV_CONTRACT = CONTRACTS["hrv"][1]
HRV_CONTRACT_DID = f"did:web:gov-hrv.etzhayyim.com:law:{CONTRACTS['hrv'][2]}"

HRV_CITIES = [
    ("city:zagreb", "Zagreb", "Zagreb", None, 767131, "https://www.zagreb.hr/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SRB
# ---------------------------------------------------------------------------
SRB_CONTRACT = CONTRACTS["srb"][1]
SRB_CONTRACT_DID = f"did:web:gov-srb.etzhayyim.com:law:{CONTRACTS['srb'][2]}"

SRB_CITIES = [
    ("city:belgrade", "Beograd", "Belgrade", None, 1688667, "https://www.beograd.rs/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SVK
# ---------------------------------------------------------------------------
SVK_CONTRACT = CONTRACTS["svk"][1]
SVK_CONTRACT_DID = f"did:web:gov-svk.etzhayyim.com:law:{CONTRACTS['svk'][2]}"

SVK_CITIES = [
    ("city:bratislava", "Bratislava", "Bratislava", None, 477174, "https://www.bratislava.sk/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SVN
# ---------------------------------------------------------------------------
SVN_CONTRACT = CONTRACTS["svn"][1]
SVN_CONTRACT_DID = f"did:web:gov-svn.etzhayyim.com:law:{CONTRACTS['svn'][2]}"

SVN_CITIES = [
    ("city:ljubljana", "Ljubljana", "Ljubljana", None, 295504, "https://www.ljubljana.si/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ALB
# ---------------------------------------------------------------------------
ALB_CONTRACT = CONTRACTS["alb"][1]
ALB_CONTRACT_DID = f"did:web:gov-alb.etzhayyim.com:law:{CONTRACTS['alb'][2]}"

ALB_CITIES = [
    ("city:tirana", "Tiranë", "Tirana", None, 897631, "https://bashkiatirane.gov.al/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BIH
# ---------------------------------------------------------------------------
BIH_CONTRACT = CONTRACTS["bih"][1]
BIH_CONTRACT_DID = f"did:web:gov-bih.etzhayyim.com:law:{CONTRACTS['bih'][2]}"

BIH_CITIES = [
    ("city:sarajevo", "Sarajevo", "Sarajevo", None, 419957, "https://www.sarajevo.ba/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MKD
# ---------------------------------------------------------------------------
MKD_CONTRACT = CONTRACTS["mkd"][1]
MKD_CONTRACT_DID = f"did:web:gov-mkd.etzhayyim.com:law:{CONTRACTS['mkd'][2]}"

MKD_CITIES = [
    ("city:skopje", "Скопје", "Skopje", None, 444831, "https://www.skopje.gov.mk/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GEO
# ---------------------------------------------------------------------------
GEO_CONTRACT = CONTRACTS["geo"][1]
GEO_CONTRACT_DID = f"did:web:gov-geo.etzhayyim.com:law:{CONTRACTS['geo'][2]}"

GEO_CITIES = [
    ("city:tbilisi", "თბილისი", "Tbilisi", None, 1171100, "https://tbilisi.gov.ge/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# EST
# ---------------------------------------------------------------------------
EST_CONTRACT = CONTRACTS["est"][1]
EST_CONTRACT_DID = f"did:web:gov-est.etzhayyim.com:law:{CONTRACTS['est'][2]}"

EST_CITIES = [
    ("city:tallinn", "Tallinn", "Tallinn", None, 455695, "https://www.tallinn.ee/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LTU
# ---------------------------------------------------------------------------
LTU_CONTRACT = CONTRACTS["ltu"][1]
LTU_CONTRACT_DID = f"did:web:gov-ltu.etzhayyim.com:law:{CONTRACTS['ltu'][2]}"

LTU_CITIES = [
    ("city:vilnius", "Vilnius", "Vilnius", None, 574147, "https://www.vilnius.lt/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LVA
# ---------------------------------------------------------------------------
LVA_CONTRACT = CONTRACTS["lva"][1]
LVA_CONTRACT_DID = f"did:web:gov-lva.etzhayyim.com:law:{CONTRACTS['lva'][2]}"

LVA_CITIES = [
    ("city:riga", "Rīga", "Riga", None, 614618, "https://www.riga.lv/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ISL
# ---------------------------------------------------------------------------
ISL_CONTRACT = CONTRACTS["isl"][1]
ISL_CONTRACT_DID = f"did:web:gov-isl.etzhayyim.com:law:{CONTRACTS['isl'][2]}"

ISL_CITIES = [
    ("city:reykjavik", "Reykjavík", "Reykjavik", None, 131136, "https://reykjavik.is/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LUX
# ---------------------------------------------------------------------------
LUX_CONTRACT = CONTRACTS["lux"][1]
LUX_CONTRACT_DID = f"did:web:gov-lux.etzhayyim.com:law:{CONTRACTS['lux'][2]}"

LUX_CITIES = [
    ("city:luxembourg", "Luxembourg", "Luxembourg City", None, 125000, "https://www.vdl.lu/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CYP
# ---------------------------------------------------------------------------
CYP_CONTRACT = CONTRACTS["cyp"][1]
CYP_CONTRACT_DID = f"did:web:gov-cyp.etzhayyim.com:law:{CONTRACTS['cyp'][2]}"

CYP_CITIES = [
    ("city:nicosia", "Λευκωσία", "Nicosia", None, 313626, "https://www.nicosia.org.cy/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# IRL
# ---------------------------------------------------------------------------
IRL_DEFAULT = ("Municipal Government Act", "Municipal Government Act", "municipal-government-act", "Local Government Act 2001", "2001-01-01", "https://www.gov.ie/")
IRL_CONTRACT = IRL_DEFAULT[1]
IRL_CONTRACT_DID = "did:web:gov-irl.etzhayyim.com:law:municipal-government-act"

IRL_CITIES = [
    ("city:dublin", "Dublin", "Dublin", None, 553165, "https://www.dublincity.ie/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# QAT
# ---------------------------------------------------------------------------
QAT_CONTRACT = CONTRACTS["qat"][1]
QAT_CONTRACT_DID = f"did:web:gov-qat.etzhayyim.com:law:{CONTRACTS['qat'][2]}"

QAT_CITIES = [
    ("city:doha", "الدوحة", "Doha", None, 2400000, "https://www.doha.gov.qa/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# KWT
# ---------------------------------------------------------------------------
KWT_CONTRACT = CONTRACTS["kwt"][1]
KWT_CONTRACT_DID = f"did:web:gov-kwt.etzhayyim.com:law:{CONTRACTS['kwt'][2]}"

KWT_CITIES = [
    ("city:kuwait-city", "مدينة الكويت", "Kuwait City", None, 2989000, "https://www.baladia.gov.kw/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# OMN
# ---------------------------------------------------------------------------
OMN_CONTRACT = CONTRACTS["omn"][1]
OMN_CONTRACT_DID = f"did:web:gov-omn.etzhayyim.com:law:{CONTRACTS['omn'][2]}"

OMN_CITIES = [
    ("city:muscat", "مسقط", "Muscat", None, 1550000, "https://www.muscat.gov.om/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# JOR
# ---------------------------------------------------------------------------
JOR_CONTRACT = CONTRACTS["jor"][1]
JOR_CONTRACT_DID = f"did:web:gov-jor.etzhayyim.com:law:{CONTRACTS['jor'][2]}"

JOR_CITIES = [
    ("city:amman", "عمّان", "Amman", None, 4007526, "https://www.ammancity.gov.jo/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LBN
# ---------------------------------------------------------------------------
LBN_CONTRACT = CONTRACTS["lbn"][1]
LBN_CONTRACT_DID = f"did:web:gov-lbn.etzhayyim.com:law:{CONTRACTS['lbn'][2]}"

LBN_CITIES = [
    ("city:beirut", "بيروت", "Beirut", None, 2200000, "https://www.beirut.gov.lb/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# IRN
# ---------------------------------------------------------------------------
IRN_CONTRACT = CONTRACTS["irn"][1]
IRN_CONTRACT_DID = f"did:web:gov-irn.etzhayyim.com:law:{CONTRACTS['irn'][2]}"

IRN_CITIES = [
    ("city:tehran", "تهران", "Tehran", None, 9259009, "https://www.tehran.ir/", "capital", "capital-district"),
    ("city:mashhad", "مشهد", "Mashhad", None, 3372660, "https://www.mashhad.ir/", "city", "capital-district"),
    ("city:isfahan", "اصفهان", "Isfahan", None, 2220000, "https://www.isfahan.ir/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# IRQ
# ---------------------------------------------------------------------------
IRQ_CONTRACT = CONTRACTS["irq"][1]
IRQ_CONTRACT_DID = f"did:web:gov-irq.etzhayyim.com:law:{CONTRACTS['irq'][2]}"

IRQ_CITIES = [
    ("city:baghdad", "بغداد", "Baghdad", None, 7682136, "https://www.amanatbaghdad.gov.iq/", "capital", "capital-district"),
    ("city:basra", "البصرة", "Basra", None, 2600000, "https://www.basrah.gov.iq/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# SYR
# ---------------------------------------------------------------------------
SYR_CONTRACT = CONTRACTS["syr"][1]
SYR_CONTRACT_DID = f"did:web:gov-syr.etzhayyim.com:law:{CONTRACTS['syr'][2]}"

SYR_CITIES = [
    ("city:damascus", "دمشق", "Damascus", None, 2500000, "https://www.damascus.gov.sy/", "capital", "capital-district"),
    ("city:aleppo", "حلب", "Aleppo", None, 2098210, "https://www.aleppo.gov.sy/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# YEM
# ---------------------------------------------------------------------------
YEM_CONTRACT = CONTRACTS["yem"][1]
YEM_CONTRACT_DID = f"did:web:gov-yem.etzhayyim.com:law:{CONTRACTS['yem'][2]}"

YEM_CITIES = [
    ("city:sanaa", "صنعاء", "Sana'a", None, 2957000, "https://www.sanaa.gov.ye/", "capital", "capital-district"),
    ("city:aden", "عدن", "Aden", None, 863000, "https://www.aden.gov.ye/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PAK
# ---------------------------------------------------------------------------
PAK_CONTRACT = CONTRACTS["pak"][1]
PAK_CONTRACT_DID = f"did:web:gov-pak.etzhayyim.com:law:{CONTRACTS['pak'][2]}"

PAK_CITIES = [
    ("city:islamabad", "اسلام آباد", "Islamabad", None, 1014825, "https://www.islamabad.gov.pk/", "capital", "capital-district"),
    ("city:karachi", "کراچی", "Karachi", None, 14910352, "https://www.kmc.gok.pk/", "city", "capital-district"),
    ("city:lahore", "لاہور", "Lahore", None, 11126285, "https://lahore.gov.pk/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BGD
# ---------------------------------------------------------------------------
BGD_CONTRACT = CONTRACTS["bgd"][1]
BGD_CONTRACT_DID = f"did:web:gov-bgd.etzhayyim.com:law:{CONTRACTS['bgd'][2]}"

BGD_CITIES = [
    ("city:dhaka", "ঢাকা", "Dhaka", None, 10278882, "https://www.dhakacity.org/", "capital", "capital-district"),
    ("city:chittagong", "চট্টগ্রাম", "Chittagong", None, 2591502, "https://www.ccc.gov.bd/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# LKA
# ---------------------------------------------------------------------------
LKA_CONTRACT = CONTRACTS["lka"][1]
LKA_CONTRACT_DID = f"did:web:gov-lka.etzhayyim.com:law:{CONTRACTS['lka'][2]}"

LKA_CITIES = [
    ("city:colombo", "කොළඹ", "Colombo", None, 752993, "https://www.colombo.mc.gov.lk/", "capital", "capital-district"),
    ("city:sri-jayawardenepura-kotte", "ශ්‍රී ජයවර්ධනපුර කෝට්ටේ", "Sri Jayawardenepura Kotte", None, 115826, "https://www.kotte.mc.gov.lk/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# NPL
# ---------------------------------------------------------------------------
NPL_CONTRACT = CONTRACTS["npl"][1]
NPL_CONTRACT_DID = f"did:web:gov-npl.etzhayyim.com:law:{CONTRACTS['npl'][2]}"

NPL_CITIES = [
    ("city:kathmandu", "काठमाडौं", "Kathmandu", None, 975453, "https://kathmandacity.gov.np/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MMR
# ---------------------------------------------------------------------------
MMR_CONTRACT = CONTRACTS["mmr"][1]
MMR_CONTRACT_DID = f"did:web:gov-mmr.etzhayyim.com:law:{CONTRACTS['mmr'][2]}"

MMR_CITIES = [
    ("city:naypyidaw", "နေပြည်တော်", "Naypyidaw", None, 1160000, "https://www.naypyidaw.gov.mm/", "capital", "capital-district"),
    ("city:yangon", "ရန်ကုန်", "Yangon", None, 7360703, "https://www.yangoncitydc.gov.mm/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# THA
# ---------------------------------------------------------------------------
THA_CONTRACT = CONTRACTS["tha"][1]
THA_CONTRACT_DID = f"did:web:gov-tha.etzhayyim.com:law:{CONTRACTS['tha'][2]}"

THA_CITIES = [
    ("city:bangkok", "กรุงเทพมหานคร", "Bangkok", None, 10539000, "https://www.bangkok.go.th/", "capital", "capital-district"),
    ("city:chiang-mai", "เชียงใหม่", "Chiang Mai", None, 131091, "https://www.chiangmai.go.th/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# VNM
# ---------------------------------------------------------------------------
VNM_CONTRACT = CONTRACTS["vnm"][1]
VNM_CONTRACT_DID = f"did:web:gov-vnm.etzhayyim.com:law:{CONTRACTS['vnm'][2]}"

VNM_CITIES = [
    ("city:hanoi", "Hà Nội", "Hanoi", None, 8053663, "https://hanoi.gov.vn/", "capital", "capital-district"),
    ("city:ho-chi-minh-city", "Thành phố Hồ Chí Minh", "Ho Chi Minh City", None, 8993082, "https://www.hochiminhcity.gov.vn/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PHL
# ---------------------------------------------------------------------------
PHL_CONTRACT = CONTRACTS["phl"][1]
PHL_CONTRACT_DID = f"did:web:gov-phl.etzhayyim.com:law:{CONTRACTS['phl'][2]}"

PHL_CITIES = [
    ("city:manila", "Manila", "Manila", None, 1846513, "https://www.manila.gov.ph/", "capital", "capital-district"),
    ("city:quezon-city", "Quezon City", "Quezon City", None, 2936116, "https://www.quezoncity.gov.ph/", "city", "capital-district"),
    ("city:davao", "Davao City", "Davao City", None, 1776949, "https://www.davaocity.gov.ph/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# MYS
# ---------------------------------------------------------------------------
MYS_CONTRACT = CONTRACTS["mys"][1]
MYS_CONTRACT_DID = f"did:web:gov-mys.etzhayyim.com:law:{CONTRACTS['mys'][2]}"

MYS_CITIES = [
    ("city:kuala-lumpur", "Kuala Lumpur", "Kuala Lumpur", None, 1982112, "https://www.dbkl.gov.my/", "capital", "capital-district"),
    ("city:george-town", "George Town", "George Town", None, 708127, "https://www.mbpp.gov.my/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# SGP
# ---------------------------------------------------------------------------
SGP_CONTRACT = CONTRACTS["sgp"][1]
SGP_CONTRACT_DID = f"did:web:gov-sgp.etzhayyim.com:law:{CONTRACTS['sgp'][2]}"

SGP_CITIES = [
    ("city:singapore", "Singapore", "Singapore", None, 5850342, "https://www.gov.sg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# KHM
# ---------------------------------------------------------------------------
KHM_CONTRACT = CONTRACTS["khm"][1]
KHM_CONTRACT_DID = f"did:web:gov-khm.etzhayyim.com:law:{CONTRACTS['khm'][2]}"

KHM_CITIES = [
    ("city:phnom-penh", "ភ្នំពេញ", "Phnom Penh", None, 2281951, "https://www.phnompenh.gov.kh/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LAO
# ---------------------------------------------------------------------------
LAO_CONTRACT = CONTRACTS["lao"][1]
LAO_CONTRACT_DID = f"did:web:gov-lao.etzhayyim.com:law:{CONTRACTS['lao'][2]}"

LAO_CITIES = [
    ("city:vientiane", "ວຽງຈັນ", "Vientiane", None, 948477, "https://www.vientiane.gov.la/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ZWE
# ---------------------------------------------------------------------------
ZWE_CONTRACT = CONTRACTS["zwe"][1]
ZWE_CONTRACT_DID = f"did:web:gov-zwe.etzhayyim.com:law:{CONTRACTS['zwe'][2]}"

ZWE_CITIES = [
    ("city:harare", "Harare", "Harare", None, 1485231, "https://www.hararecity.co.zw/", "capital", "capital-district"),
    ("city:bulawayo", "Bulawayo", "Bulawayo", None, 653337, "https://www.citybyo.co.zw/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# KEN
# ---------------------------------------------------------------------------
KEN_CONTRACT = CONTRACTS["ken"][1]
KEN_CONTRACT_DID = f"did:web:gov-ken.etzhayyim.com:law:{CONTRACTS['ken'][2]}"

KEN_CITIES = [
    ("city:nairobi", "Nairobi", "Nairobi", None, 4397073, "https://www.nairobi.go.ke/", "capital", "capital-district"),
    ("city:mombasa", "Mombasa", "Mombasa", None, 1208333, "https://www.mombasa.go.ke/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# TZA
# ---------------------------------------------------------------------------
TZA_CONTRACT = CONTRACTS["tza"][1]
TZA_CONTRACT_DID = f"did:web:gov-tza.etzhayyim.com:law:{CONTRACTS['tza'][2]}"

TZA_CITIES = [
    ("city:dodoma", "Dodoma", "Dodoma", None, 410956, "https://www.dodoma.go.tz/", "capital", "capital-district"),
    ("city:dar-es-salaam", "Dar es Salaam", "Dar es Salaam", None, 6368000, "https://www.dar.go.tz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# NGA
# ---------------------------------------------------------------------------
NGA_CONTRACT = CONTRACTS["nga"][1]
NGA_CONTRACT_DID = f"did:web:gov-nga.etzhayyim.com:law:{CONTRACTS['nga'][2]}"

NGA_CITIES = [
    ("city:abuja", "Abuja", "Abuja", None, 3649000, "https://www.fcta.gov.ng/", "capital", "capital-district"),
    ("city:lagos", "Lagos", "Lagos", None, 14862111, "https://lagosstate.gov.ng/", "city", "capital-district"),
    ("city:kano", "Kano", "Kano", None, 3626068, "https://www.kanostate.gov.ng/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# ETH
# ---------------------------------------------------------------------------
ETH_CONTRACT = CONTRACTS["eth"][1]
ETH_CONTRACT_DID = f"did:web:gov-eth.etzhayyim.com:law:{CONTRACTS['eth'][2]}"

ETH_CITIES = [
    ("city:addis-ababa", "አዲስ አበባ", "Addis Ababa", None, 3353000, "https://www.addisababacity.gov.et/", "capital", "capital-district"),
    ("city:dire-dawa", "ድሬ ዳዋ", "Dire Dawa", None, 440000, "https://www.diredawa.gov.et/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# GHA
# ---------------------------------------------------------------------------
GHA_CONTRACT = CONTRACTS["gha"][1]
GHA_CONTRACT_DID = f"did:web:gov-gha.etzhayyim.com:law:{CONTRACTS['gha'][2]}"

GHA_CITIES = [
    ("city:accra", "Accra", "Accra", None, 2514000, "https://www.ghanadistricts.gov.gh/", "capital", "capital-district"),
    ("city:kumasi", "Kumasi", "Kumasi", None, 3179000, "https://www.kma.gov.gh/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# CMR
# ---------------------------------------------------------------------------
CMR_CONTRACT = CONTRACTS["cmr"][1]
CMR_CONTRACT_DID = f"did:web:gov-cmr.etzhayyim.com:law:{CONTRACTS['cmr'][2]}"

CMR_CITIES = [
    ("city:yaounde", "Yaoundé", "Yaounde", None, 3236000, "https://www.communaute-urbaine-de-yaounde.cm/", "capital", "capital-district"),
    ("city:douala", "Douala", "Douala", None, 3966000, "https://www.cudn.cm/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# SEN
# ---------------------------------------------------------------------------
SEN_CONTRACT = CONTRACTS["sen"][1]
SEN_CONTRACT_DID = f"did:web:gov-sen.etzhayyim.com:law:{CONTRACTS['sen'][2]}"

SEN_CITIES = [
    ("city:dakar", "Dakar", "Dakar", None, 3137196, "https://www.ville.dakar.sn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# AGO
# ---------------------------------------------------------------------------
AGO_CONTRACT = CONTRACTS["ago"][1]
AGO_CONTRACT_DID = f"did:web:gov-ago.etzhayyim.com:law:{CONTRACTS['ago'][2]}"

AGO_CITIES = [
    ("city:luanda", "Luanda", "Luanda", None, 8330000, "https://www.luanda.gov.ao/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# COD
# ---------------------------------------------------------------------------
COD_CONTRACT = CONTRACTS["cod"][1]
COD_CONTRACT_DID = f"did:web:gov-cod.etzhayyim.com:law:{CONTRACTS['cod'][2]}"

COD_CITIES = [
    ("city:kinshasa", "Kinshasa", "Kinshasa", None, 14970460, "https://www.kinshasa.cd/", "capital", "capital-district"),
    ("city:lubumbashi", "Lubumbashi", "Lubumbashi", None, 2136000, "https://www.haut-katanga.cd/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# UGA
# ---------------------------------------------------------------------------
UGA_CONTRACT = CONTRACTS["uga"][1]
UGA_CONTRACT_DID = f"did:web:gov-uga.etzhayyim.com:law:{CONTRACTS['uga'][2]}"

UGA_CITIES = [
    ("city:kampala", "Kampala", "Kampala", None, 1659600, "https://www.kcca.go.ug/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MOZ
# ---------------------------------------------------------------------------
MOZ_CONTRACT = CONTRACTS["moz"][1]
MOZ_CONTRACT_DID = f"did:web:gov-moz.etzhayyim.com:law:{CONTRACTS['moz'][2]}"

MOZ_CITIES = [
    ("city:maputo", "Maputo", "Maputo", None, 1101170, "https://www.cm-maputo.gov.mz/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MDG
# ---------------------------------------------------------------------------
MDG_CONTRACT = CONTRACTS["mdg"][1]
MDG_CONTRACT_DID = f"did:web:gov-mdg.etzhayyim.com:law:{CONTRACTS['mdg'][2]}"

MDG_CITIES = [
    ("city:antananarivo", "Antananarivo", "Antananarivo", None, 1391433, "https://www.tananarive.gov.mg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# RWA
# ---------------------------------------------------------------------------
RWA_CONTRACT = CONTRACTS["rwa"][1]
RWA_CONTRACT_DID = f"did:web:gov-rwa.etzhayyim.com:law:{CONTRACTS['rwa'][2]}"

RWA_CITIES = [
    ("city:kigali", "Kigali", "Kigali", None, 1132686, "https://www.kigalicity.gov.rw/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CIV
# ---------------------------------------------------------------------------
CIV_CONTRACT = CONTRACTS["civ"][1]
CIV_CONTRACT_DID = f"did:web:gov-civ.etzhayyim.com:law:{CONTRACTS['civ'][2]}"

CIV_CITIES = [
    ("city:yamoussoukro", "Yamoussoukro", "Yamoussoukro", None, 350000, "https://www.yamoussoukro.ci/", "capital", "capital-district"),
    ("city:abidjan", "Abidjan", "Abidjan", None, 5515000, "https://www.mairie-abidjan.ci/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BFA
# ---------------------------------------------------------------------------
BFA_CONTRACT = CONTRACTS["bfa"][1]
BFA_CONTRACT_DID = f"did:web:gov-bfa.etzhayyim.com:law:{CONTRACTS['bfa'][2]}"

BFA_CITIES = [
    ("city:ouagadougou", "Ouagadougou", "Ouagadougou", None, 2415266, "https://www.mairie-ouagadougou.bf/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MLI
# ---------------------------------------------------------------------------
MLI_CONTRACT = CONTRACTS["mli"][1]
MLI_CONTRACT_DID = f"did:web:gov-mli.etzhayyim.com:law:{CONTRACTS['mli'][2]}"

MLI_CITIES = [
    ("city:bamako", "Bamako", "Bamako", None, 2929519, "https://www.mairie-bamako.ml/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# NER
# ---------------------------------------------------------------------------
NER_CONTRACT = CONTRACTS["ner"][1]
NER_CONTRACT_DID = f"did:web:gov-ner.etzhayyim.com:law:{CONTRACTS['ner'][2]}"

NER_CITIES = [
    ("city:niamey", "Niamey", "Niamey", None, 1324508, "https://www.niamey.ne/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TCD
# ---------------------------------------------------------------------------
TCD_CONTRACT = CONTRACTS["tcd"][1]
TCD_CONTRACT_DID = f"did:web:gov-tcd.etzhayyim.com:law:{CONTRACTS['tcd'][2]}"

TCD_CITIES = [
    ("city:ndjamena", "N'Djamena", "N'Djamena", None, 1508000, "https://www.mairie-ndjamena.td/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GIN
# ---------------------------------------------------------------------------
GIN_CONTRACT = CONTRACTS["gin"][1]
GIN_CONTRACT_DID = f"did:web:gov-gin.etzhayyim.com:law:{CONTRACTS['gin'][2]}"

GIN_CITIES = [
    ("city:conakry", "Conakry", "Conakry", None, 1667864, "https://www.mairie-conakry.gov.gn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TGO
# ---------------------------------------------------------------------------
TGO_CONTRACT = CONTRACTS["tgo"][1]
TGO_CONTRACT_DID = f"did:web:gov-tgo.etzhayyim.com:law:{CONTRACTS['tgo'][2]}"

TGO_CITIES = [
    ("city:lome", "Lomé", "Lome", None, 1477660, "https://www.mairie-lome.tg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BEN
# ---------------------------------------------------------------------------
BEN_CONTRACT = CONTRACTS["ben"][1]
BEN_CONTRACT_DID = f"did:web:gov-ben.etzhayyim.com:law:{CONTRACTS['ben'][2]}"

BEN_CITIES = [
    ("city:porto-novo", "Porto-Novo", "Porto-Novo", None, 264320, "https://www.porto-novo.bj/", "capital", "capital-district"),
    ("city:cotonou", "Cotonou", "Cotonou", None, 762000, "https://www.cotonou.bj/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# NAM
# ---------------------------------------------------------------------------
NAM_CONTRACT = CONTRACTS["nam"][1]
NAM_CONTRACT_DID = f"did:web:gov-nam.etzhayyim.com:law:{CONTRACTS['nam'][2]}"

NAM_CITIES = [
    ("city:windhoek", "Windhoek", "Windhoek", None, 431000, "https://www.windhoekcc.org.na/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BWA
# ---------------------------------------------------------------------------
BWA_CONTRACT = CONTRACTS["bwa"][1]
BWA_CONTRACT_DID = f"did:web:gov-bwa.etzhayyim.com:law:{CONTRACTS['bwa'][2]}"

BWA_CITIES = [
    ("city:gaborone", "Gaborone", "Gaborone", None, 231592, "https://www.gaborone.gov.bw/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LSO
# ---------------------------------------------------------------------------
LSO_CONTRACT = CONTRACTS["lso"][1]
LSO_CONTRACT_DID = f"did:web:gov-lso.etzhayyim.com:law:{CONTRACTS['lso'][2]}"

LSO_CITIES = [
    ("city:maseru", "Maseru", "Maseru", None, 330760, "https://www.maseru.gov.ls/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SWZ
# ---------------------------------------------------------------------------
SWZ_CONTRACT = CONTRACTS["swz"][1]
SWZ_CONTRACT_DID = f"did:web:gov-swz.etzhayyim.com:law:{CONTRACTS['swz'][2]}"

SWZ_CITIES = [
    ("city:mbabane", "Mbabane", "Mbabane", None, 94874, "https://www.mbabane.gov.sz/", "capital", "capital-district"),
    ("city:lobamba", "Lobamba", "Lobamba", None, 11000, "https://www.gov.sz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# MWI
# ---------------------------------------------------------------------------
MWI_CONTRACT = CONTRACTS["mwi"][1]
MWI_CONTRACT_DID = f"did:web:gov-mwi.etzhayyim.com:law:{CONTRACTS['mwi'][2]}"

MWI_CITIES = [
    ("city:lilongwe", "Lilongwe", "Lilongwe", None, 989318, "https://www.lilongwe.mw/", "capital", "capital-district"),
    ("city:blantyre", "Blantyre", "Blantyre", None, 800264, "https://www.blantyre.mw/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# ZMB
# ---------------------------------------------------------------------------
ZMB_CONTRACT = CONTRACTS["zmb"][1]
ZMB_CONTRACT_DID = f"did:web:gov-zmb.etzhayyim.com:law:{CONTRACTS['zmb'][2]}"

ZMB_CITIES = [
    ("city:lusaka", "Lusaka", "Lusaka", None, 2731696, "https://www.lcc.gov.zm/", "capital", "capital-district"),
    ("city:kitwe", "Kitwe", "Kitwe", None, 580887, "https://www.kmc.gov.zm/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# COL
# ---------------------------------------------------------------------------
COL_CONTRACT = CONTRACTS["col"][1]
COL_CONTRACT_DID = f"did:web:gov-col.etzhayyim.com:law:{CONTRACTS['col'][2]}"

COL_CITIES = [
    ("city:bogota", "Bogotá", "Bogota", None, 7743955, "https://www.bogota.gov.co/", "capital", "capital-district"),
    ("city:medellin", "Medellín", "Medellin", None, 2572157, "https://www.medellin.gov.co/", "city", "capital-district"),
    ("city:cali", "Cali", "Cali", None, 2227642, "https://www.cali.gov.co/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# VEN
# ---------------------------------------------------------------------------
VEN_CONTRACT = CONTRACTS["ven"][1]
VEN_CONTRACT_DID = f"did:web:gov-ven.etzhayyim.com:law:{CONTRACTS['ven'][2]}"

VEN_CITIES = [
    ("city:caracas", "Caracas", "Caracas", None, 2900000, "https://www.alcaldiadecaracas.gob.ve/", "capital", "capital-district"),
    ("city:maracaibo", "Maracaibo", "Maracaibo", None, 1495182, "https://www.alcaldiademaracaibo.gob.ve/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PER
# ---------------------------------------------------------------------------
PER_CONTRACT = CONTRACTS["per"][1]
PER_CONTRACT_DID = f"did:web:gov-per.etzhayyim.com:law:{CONTRACTS['per'][2]}"

PER_CITIES = [
    ("city:lima", "Lima", "Lima", None, 10555782, "https://www.munlima.gob.pe/", "capital", "capital-district"),
    ("city:arequipa", "Arequipa", "Arequipa", None, 1008290, "https://www.muniarequipa.gob.pe/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# CHL
# ---------------------------------------------------------------------------
CHL_CONTRACT = CONTRACTS["chl"][1]
CHL_CONTRACT_DID = f"did:web:gov-chl.etzhayyim.com:law:{CONTRACTS['chl'][2]}"

CHL_CITIES = [
    ("city:santiago", "Santiago", "Santiago", None, 5220161, "https://www.munistgo.cl/", "capital", "capital-district"),
    ("city:valparaiso", "Valparaíso", "Valparaiso", None, 296655, "https://www.municipalidaddevalparaiso.cl/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# ECU
# ---------------------------------------------------------------------------
ECU_CONTRACT = CONTRACTS["ecu"][1]
ECU_CONTRACT_DID = f"did:web:gov-ecu.etzhayyim.com:law:{CONTRACTS['ecu'][2]}"

ECU_CITIES = [
    ("city:quito", "Quito", "Quito", None, 1619146, "https://www.quito.gob.ec/", "capital", "capital-district"),
    ("city:guayaquil", "Guayaquil", "Guayaquil", None, 2278691, "https://www.guayaquil.gob.ec/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BOL
# ---------------------------------------------------------------------------
BOL_CONTRACT = CONTRACTS["bol"][1]
BOL_CONTRACT_DID = f"did:web:gov-bol.etzhayyim.com:law:{CONTRACTS['bol'][2]}"

BOL_CITIES = [
    ("city:sucre", "Sucre", "Sucre", None, 281000, "https://www.sucre.bo/", "capital", "capital-district"),
    ("city:la-paz", "La Paz", "La Paz", None, 789585, "https://www.lapaz.bo/", "city", "capital-district"),
    ("city:santa-cruz", "Santa Cruz de la Sierra", "Santa Cruz de la Sierra", None, 1453549, "https://www.santacruz.gob.bo/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PRY
# ---------------------------------------------------------------------------
PRY_CONTRACT = CONTRACTS["pry"][1]
PRY_CONTRACT_DID = f"did:web:gov-pry.etzhayyim.com:law:{CONTRACTS['pry'][2]}"

PRY_CITIES = [
    ("city:asuncion", "Asunción", "Asuncion", None, 729307, "https://www.asuncion.gov.py/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# URY
# ---------------------------------------------------------------------------
URY_CONTRACT = CONTRACTS["ury"][1]
URY_CONTRACT_DID = f"did:web:gov-ury.etzhayyim.com:law:{CONTRACTS['ury'][2]}"

URY_CITIES = [
    ("city:montevideo", "Montevideo", "Montevideo", None, 1382481, "https://montevideo.gub.uy/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# PAN
# ---------------------------------------------------------------------------
PAN_CONTRACT = CONTRACTS["pan"][1]
PAN_CONTRACT_DID = f"did:web:gov-pan.etzhayyim.com:law:{CONTRACTS['pan'][2]}"

PAN_CITIES = [
    ("city:panama-city", "Ciudad de Panamá", "Panama City", None, 880691, "https://www.ciudaddepanama.gob.pa/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CRI
# ---------------------------------------------------------------------------
CRI_CONTRACT = CONTRACTS["cri"][1]
CRI_CONTRACT_DID = f"did:web:gov-cri.etzhayyim.com:law:{CONTRACTS['cri'][2]}"

CRI_CITIES = [
    ("city:san-jose", "San José", "San Jose", None, 340000, "https://www.msj.go.cr/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GTM
# ---------------------------------------------------------------------------
GTM_CONTRACT = CONTRACTS["gtm"][1]
GTM_CONTRACT_DID = f"did:web:gov-gtm.etzhayyim.com:law:{CONTRACTS['gtm'][2]}"

GTM_CITIES = [
    ("city:guatemala-city", "Ciudad de Guatemala", "Guatemala City", None, 994938, "https://www.muniguate.com/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# HND
# ---------------------------------------------------------------------------
HND_CONTRACT = CONTRACTS["hnd"][1]
HND_CONTRACT_DID = f"did:web:gov-hnd.etzhayyim.com:law:{CONTRACTS['hnd'][2]}"

HND_CITIES = [
    ("city:tegucigalpa", "Tegucigalpa", "Tegucigalpa", None, 1157509, "https://www.municipalidadtegucigalpa.hn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SLV
# ---------------------------------------------------------------------------
SLV_CONTRACT = CONTRACTS["slv"][1]
SLV_CONTRACT_DID = f"did:web:gov-slv.etzhayyim.com:law:{CONTRACTS['slv'][2]}"

SLV_CITIES = [
    ("city:san-salvador", "San Salvador", "San Salvador", None, 316090, "https://www.sansalvador.gob.sv/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# NIC
# ---------------------------------------------------------------------------
NIC_CONTRACT = CONTRACTS["nic"][1]
NIC_CONTRACT_DID = f"did:web:gov-nic.etzhayyim.com:law:{CONTRACTS['nic'][2]}"

NIC_CITIES = [
    ("city:managua", "Managua", "Managua", None, 1055247, "https://www.managua.gob.ni/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# DOM
# ---------------------------------------------------------------------------
DOM_CONTRACT = CONTRACTS["dom"][1]
DOM_CONTRACT_DID = f"did:web:gov-dom.etzhayyim.com:law:{CONTRACTS['dom'][2]}"

DOM_CITIES = [
    ("city:santo-domingo", "Santo Domingo", "Santo Domingo", None, 965040, "https://www.adn.gob.do/", "capital", "capital-district"),
    ("city:santiago-de-los-caballeros", "Santiago de los Caballeros", "Santiago de los Caballeros", None, 691262, "https://www.ayuntamientosantiago.gob.do/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# CUB
# ---------------------------------------------------------------------------
CUB_CONTRACT = CONTRACTS["cub"][1]
CUB_CONTRACT_DID = f"did:web:gov-cub.etzhayyim.com:law:{CONTRACTS['cub'][2]}"

CUB_CITIES = [
    ("city:havana", "La Habana", "Havana", None, 2130517, "https://www.gobiernoprovincial.oh.cu/", "capital", "capital-district"),
    ("city:santiago-de-cuba", "Santiago de Cuba", "Santiago de Cuba", None, 555865, "https://www.santiago.cu/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# JAM
# ---------------------------------------------------------------------------
JAM_CONTRACT = CONTRACTS["jam"][1]
JAM_CONTRACT_DID = f"did:web:gov-jam.etzhayyim.com:law:{CONTRACTS['jam'][2]}"

JAM_CITIES = [
    ("city:kingston", "Kingston", "Kingston", None, 662426, "https://www.kingstoncityja.com/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GUY
# ---------------------------------------------------------------------------
GUY_CONTRACT = CONTRACTS["guy"][1]
GUY_CONTRACT_DID = f"did:web:gov-guy.etzhayyim.com:law:{CONTRACTS['guy'][2]}"

GUY_CITIES = [
    ("city:georgetown", "Georgetown", "Georgetown", None, 235017, "https://www.gina.gov.gy/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# KAZ
# ---------------------------------------------------------------------------
KAZ_CONTRACT = CONTRACTS["kaz"][1]
KAZ_CONTRACT_DID = f"did:web:gov-kaz.etzhayyim.com:law:{CONTRACTS['kaz'][2]}"

KAZ_CITIES = [
    ("city:astana", "Астана", "Astana", None, 1200000, "https://astana.gov.kz/", "capital", "capital-district"),
    ("city:almaty", "Алматы", "Almaty", None, 1977011, "https://www.almaty.gov.kz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# UZB
# ---------------------------------------------------------------------------
UZB_CONTRACT = CONTRACTS["uzb"][1]
UZB_CONTRACT_DID = f"did:web:gov-uzb.etzhayyim.com:law:{CONTRACTS['uzb'][2]}"

UZB_CITIES = [
    ("city:tashkent", "Тошкент", "Tashkent", None, 2571394, "https://tashkent.uz/", "capital", "capital-district"),
    ("city:samarkand", "Самарқанд", "Samarkand", None, 509000, "https://samarkand.uz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# TKM
# ---------------------------------------------------------------------------
TKM_CONTRACT = CONTRACTS["tkm"][1]
TKM_CONTRACT_DID = f"did:web:gov-tkm.etzhayyim.com:law:{CONTRACTS['tkm'][2]}"

TKM_CITIES = [
    ("city:ashgabat", "Aşgabat", "Ashgabat", None, 1031992, "https://www.turkmenistan.gov.tm/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# KGZ
# ---------------------------------------------------------------------------
KGZ_CONTRACT = CONTRACTS["kgz"][1]
KGZ_CONTRACT_DID = f"did:web:gov-kgz.etzhayyim.com:law:{CONTRACTS['kgz'][2]}"

KGZ_CITIES = [
    ("city:bishkek", "Бишкек", "Bishkek", None, 1053000, "https://www.bishkek.gov.kg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TJK
# ---------------------------------------------------------------------------
TJK_CONTRACT = CONTRACTS["tjk"][1]
TJK_CONTRACT_DID = f"did:web:gov-tjk.etzhayyim.com:law:{CONTRACTS['tjk'][2]}"

TJK_CITIES = [
    ("city:dushanbe", "Душанбе", "Dushanbe", None, 863400, "https://www.hukumat.tj/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ARM
# ---------------------------------------------------------------------------
ARM_CONTRACT = CONTRACTS["arm"][1]
ARM_CONTRACT_DID = f"did:web:gov-arm.etzhayyim.com:law:{CONTRACTS['arm'][2]}"

ARM_CITIES = [
    ("city:yerevan", "Երևան", "Yerevan", None, 1093485, "https://www.yerevan.am/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# AZE
# ---------------------------------------------------------------------------
AZE_CONTRACT = CONTRACTS["aze"][1]
AZE_CONTRACT_DID = f"did:web:gov-aze.etzhayyim.com:law:{CONTRACTS['aze'][2]}"

AZE_CITIES = [
    ("city:baku", "Bakı", "Baku", None, 2293100, "https://www.baku.gov.az/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BLR
# ---------------------------------------------------------------------------
BLR_CONTRACT = CONTRACTS["blr"][1]
BLR_CONTRACT_DID = f"did:web:gov-blr.etzhayyim.com:law:{CONTRACTS['blr'][2]}"

BLR_CITIES = [
    ("city:minsk", "Мінск", "Minsk", None, 2009786, "https://minsk.gov.by/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# AFG (no CONTRACTS entry, use DEFAULT)
# ---------------------------------------------------------------------------
AFG_DEFAULT = DEFAULT_CONTRACT
AFG_CONTRACT = AFG_DEFAULT[1]
AFG_CONTRACT_DID = "did:web:gov-afg.etzhayyim.com:law:municipal-government-act"

AFG_CITIES = [
    ("city:kabul", "کابل", "Kabul", None, 4601789, "https://www.kabul.gov.af/", "capital", "capital-district"),
    ("city:kandahar", "کندهار", "Kandahar", None, 614118, "https://www.kandahar.gov.af/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# DZA (no CONTRACTS entry)
# ---------------------------------------------------------------------------
DZA_CONTRACT = DEFAULT_CONTRACT[1]
DZA_CONTRACT_DID = "did:web:gov-dza.etzhayyim.com:law:municipal-government-act"

DZA_CITIES = [
    ("city:algiers", "الجزائر", "Algiers", None, 3415811, "https://www.wilaya-alger.dz/", "capital", "capital-district"),
    ("city:oran", "وهران", "Oran", None, 803329, "https://www.wilaya-oran.dz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# EGY (no CONTRACTS entry)
# ---------------------------------------------------------------------------
EGY_CONTRACT = DEFAULT_CONTRACT[1]
EGY_CONTRACT_DID = "did:web:gov-egy.etzhayyim.com:law:municipal-government-act"

EGY_CITIES = [
    ("city:cairo", "القاهرة", "Cairo", None, 10107125, "https://www.cairo.gov.eg/", "capital", "capital-district"),
    ("city:alexandria", "الإسكندرية", "Alexandria", None, 5200000, "https://www.alexandria.gov.eg/", "city", "capital-district"),
    ("city:giza", "الجيزة", "Giza", None, 3628062, "https://www.giza.gov.eg/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# ISR (no CONTRACTS entry)
# ---------------------------------------------------------------------------
ISR_CONTRACT = DEFAULT_CONTRACT[1]
ISR_CONTRACT_DID = "did:web:gov-isr.etzhayyim.com:law:municipal-government-act"

ISR_CITIES = [
    ("city:jerusalem", "ירושלים", "Jerusalem", None, 919438, "https://www.jerusalem.muni.il/", "capital", "capital-district"),
    ("city:tel-aviv", "תל אביב", "Tel Aviv", None, 460613, "https://www.tel-aviv.gov.il/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# MAR (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MAR_CONTRACT = DEFAULT_CONTRACT[1]
MAR_CONTRACT_DID = "did:web:gov-mar.etzhayyim.com:law:municipal-government-act"

MAR_CITIES = [
    ("city:rabat", "الرباط", "Rabat", None, 577827, "https://www.ville.rabat.ma/", "capital", "capital-district"),
    ("city:casablanca", "الدار البيضاء", "Casablanca", None, 3752000, "https://www.casablanca.ma/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# SDN (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SDN_CONTRACT = DEFAULT_CONTRACT[1]
SDN_CONTRACT_DID = "did:web:gov-sdn.etzhayyim.com:law:municipal-government-act"

SDN_CITIES = [
    ("city:khartoum", "الخرطوم", "Khartoum", None, 5274321, "https://www.khartoum.gov.sd/", "capital", "capital-district"),
    ("city:omdurman", "أم درمان", "Omdurman", None, 2802000, "https://www.omdurman.gov.sd/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# MNG (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MNG_CONTRACT = DEFAULT_CONTRACT[1]
MNG_CONTRACT_DID = "did:web:gov-mng.etzhayyim.com:law:municipal-government-act"

MNG_CITIES = [
    ("city:ulaanbaatar", "Улаанбаатар", "Ulaanbaatar", None, 1382930, "https://www.ulaanbaatar.mn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# PRK (no CONTRACTS entry)
# ---------------------------------------------------------------------------
PRK_CONTRACT = DEFAULT_CONTRACT[1]
PRK_CONTRACT_DID = "did:web:gov-prk.etzhayyim.com:law:municipal-government-act"

PRK_CITIES = [
    ("city:pyongyang", "평양", "Pyongyang", None, 3255288, "https://www.rodong.rep.kp/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# PSE (no CONTRACTS entry)
# ---------------------------------------------------------------------------
PSE_CONTRACT = DEFAULT_CONTRACT[1]
PSE_CONTRACT_DID = "did:web:gov-pse.etzhayyim.com:law:municipal-government-act"

PSE_CITIES = [
    ("city:ramallah", "رام الله", "Ramallah", None, 38998, "https://www.ramallah.ps/", "capital", "capital-district"),
    ("city:gaza", "غزة", "Gaza City", None, 590481, "https://www.mogaza.org/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# TWN (no CONTRACTS entry)
# ---------------------------------------------------------------------------
TWN_CONTRACT = DEFAULT_CONTRACT[1]
TWN_CONTRACT_DID = "did:web:gov-twn.etzhayyim.com:law:municipal-government-act"

TWN_CITIES = [
    ("city:taipei", "臺北市", "Taipei", None, 2646204, "https://www.gov.taipei/", "capital", "capital-district"),
    ("city:new-taipei", "新北市", "New Taipei City", None, 3974697, "https://www.ntpc.gov.tw/", "city", "capital-district"),
    ("city:taichung", "臺中市", "Taichung", None, 2820000, "https://www.taichung.gov.tw/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# TUN (no CONTRACTS entry)
# ---------------------------------------------------------------------------
TUN_CONTRACT = DEFAULT_CONTRACT[1]
TUN_CONTRACT_DID = "did:web:gov-tun.etzhayyim.com:law:municipal-government-act"

TUN_CITIES = [
    ("city:tunis", "تونس", "Tunis", None, 1056247, "https://www.commune-tunis.gov.tn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# XKX (Kosovo, no CONTRACTS entry)
# ---------------------------------------------------------------------------
XKX_CONTRACT = DEFAULT_CONTRACT[1]
XKX_CONTRACT_DID = "did:web:gov-xkx.etzhayyim.com:law:municipal-government-act"

XKX_CITIES = [
    ("city:pristina", "Prishtinë", "Pristina", None, 198897, "https://kk.rks-gov.net/prishtina/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BDI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
BDI_CONTRACT = DEFAULT_CONTRACT[1]
BDI_CONTRACT_DID = "did:web:gov-bdi.etzhayyim.com:law:municipal-government-act"

BDI_CITIES = [
    ("city:gitega", "Gitega", "Gitega", None, 47300, "https://www.burundi.gov.bi/", "capital", "capital-district"),
    ("city:bujumbura", "Bujumbura", "Bujumbura", None, 1144949, "https://www.bujumbura.bi/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BHS (no CONTRACTS entry)
# ---------------------------------------------------------------------------
BHS_CONTRACT = DEFAULT_CONTRACT[1]
BHS_CONTRACT_DID = "did:web:gov-bhs.etzhayyim.com:law:municipal-government-act"

BHS_CITIES = [
    ("city:nassau", "Nassau", "Nassau", None, 280000, "https://www.bahamas.gov.bs/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BLZ (no CONTRACTS entry)
# ---------------------------------------------------------------------------
BLZ_CONTRACT = DEFAULT_CONTRACT[1]
BLZ_CONTRACT_DID = "did:web:gov-blz.etzhayyim.com:law:municipal-government-act"

BLZ_CITIES = [
    ("city:belmopan", "Belmopan", "Belmopan", None, 22800, "https://www.belize.gov.bz/", "capital", "capital-district"),
    ("city:belize-city", "Belize City", "Belize City", None, 61461, "https://www.belize.gov.bz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# BRN (no CONTRACTS entry)
# ---------------------------------------------------------------------------
BRN_CONTRACT = DEFAULT_CONTRACT[1]
BRN_CONTRACT_DID = "did:web:gov-brn.etzhayyim.com:law:municipal-government-act"

BRN_CITIES = [
    ("city:bandar-seri-begawan", "Bandar Seri Begawan", "Bandar Seri Begawan", None, 100700, "https://www.brunei.gov.bn/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# BTN (no CONTRACTS entry)
# ---------------------------------------------------------------------------
BTN_CONTRACT = DEFAULT_CONTRACT[1]
BTN_CONTRACT_DID = "did:web:gov-btn.etzhayyim.com:law:municipal-government-act"

BTN_CITIES = [
    ("city:thimphu", "ཐིམ་ཕུ", "Thimphu", None, 114551, "https://www.thimphucity.gov.bt/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CAF (no CONTRACTS entry)
# ---------------------------------------------------------------------------
CAF_CONTRACT = DEFAULT_CONTRACT[1]
CAF_CONTRACT_DID = "did:web:gov-caf.etzhayyim.com:law:municipal-government-act"

CAF_CITIES = [
    ("city:bangui", "Bangui", "Bangui", None, 889231, "https://www.gouv.cf/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# COG (no CONTRACTS entry)
# ---------------------------------------------------------------------------
COG_CONTRACT = DEFAULT_CONTRACT[1]
COG_CONTRACT_DID = "did:web:gov-cog.etzhayyim.com:law:municipal-government-act"

COG_CITIES = [
    ("city:brazzaville", "Brazzaville", "Brazzaville", None, 1827000, "https://www.ville-brazzaville.cg/", "capital", "capital-district"),
    ("city:pointe-noire", "Pointe-Noire", "Pointe-Noire", None, 969000, "https://www.mairie-pointenoire.cg/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# COM (no CONTRACTS entry)
# ---------------------------------------------------------------------------
COM_CONTRACT = DEFAULT_CONTRACT[1]
COM_CONTRACT_DID = "did:web:gov-com.etzhayyim.com:law:municipal-government-act"

COM_CITIES = [
    ("city:moroni", "مورونى", "Moroni", None, 54000, "https://www.gouvernement.km/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# CPV (no CONTRACTS entry)
# ---------------------------------------------------------------------------
CPV_CONTRACT = DEFAULT_CONTRACT[1]
CPV_CONTRACT_DID = "did:web:gov-cpv.etzhayyim.com:law:municipal-government-act"

CPV_CITIES = [
    ("city:praia", "Praia", "Praia", None, 168450, "https://www.cmpraia.cv/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# DJI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
DJI_CONTRACT = DEFAULT_CONTRACT[1]
DJI_CONTRACT_DID = "did:web:gov-dji.etzhayyim.com:law:municipal-government-act"

DJI_CITIES = [
    ("city:djibouti", "Djibouti", "Djibouti City", None, 623891, "https://www.gouv.dj/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# ERI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
ERI_CONTRACT = DEFAULT_CONTRACT[1]
ERI_CONTRACT_DID = "did:web:gov-eri.etzhayyim.com:law:municipal-government-act"

ERI_CITIES = [
    ("city:asmara", "ኣስመራ", "Asmara", None, 963000, "https://www.shabait.com/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# FJI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
FJI_CONTRACT = DEFAULT_CONTRACT[1]
FJI_CONTRACT_DID = "did:web:gov-fji.etzhayyim.com:law:municipal-government-act"

FJI_CITIES = [
    ("city:suva", "Suva", "Suva", None, 93970, "https://www.suvacitycouncil.org.fj/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GMB (no CONTRACTS entry)
# ---------------------------------------------------------------------------
GMB_CONTRACT = DEFAULT_CONTRACT[1]
GMB_CONTRACT_DID = "did:web:gov-gmb.etzhayyim.com:law:municipal-government-act"

GMB_CITIES = [
    ("city:banjul", "Banjul", "Banjul", None, 31301, "https://www.banjulcitycouncil.gm/", "capital", "capital-district"),
    ("city:serekunda", "Serekunda", "Serekunda", None, 340000, "https://www.kmc.gov.gm/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# GNB (no CONTRACTS entry)
# ---------------------------------------------------------------------------
GNB_CONTRACT = DEFAULT_CONTRACT[1]
GNB_CONTRACT_DID = "did:web:gov-gnb.etzhayyim.com:law:municipal-government-act"

GNB_CITIES = [
    ("city:bissau", "Bissau", "Bissau", None, 492004, "https://www.gov.gw/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# GNQ (no CONTRACTS entry)
# ---------------------------------------------------------------------------
GNQ_CONTRACT = DEFAULT_CONTRACT[1]
GNQ_CONTRACT_DID = "did:web:gov-gnq.etzhayyim.com:law:municipal-government-act"

GNQ_CITIES = [
    ("city:malabo", "Malabo", "Malabo", None, 297000, "https://www.guineaecuatorialpress.com/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# HTI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
HTI_CONTRACT = DEFAULT_CONTRACT[1]
HTI_CONTRACT_DID = "did:web:gov-hti.etzhayyim.com:law:municipal-government-act"

HTI_CITIES = [
    ("city:port-au-prince", "Port-au-Prince", "Port-au-Prince", None, 1234750, "https://www.haiti.gouv.ht/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# KIR (no CONTRACTS entry)
# ---------------------------------------------------------------------------
KIR_CONTRACT = DEFAULT_CONTRACT[1]
KIR_CONTRACT_DID = "did:web:gov-kir.etzhayyim.com:law:municipal-government-act"

KIR_CITIES = [
    ("city:south-tarawa", "South Tarawa", "South Tarawa", None, 56388, "https://www.kiribati.gov.ki/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LBR (no CONTRACTS entry)
# ---------------------------------------------------------------------------
LBR_CONTRACT = DEFAULT_CONTRACT[1]
LBR_CONTRACT_DID = "did:web:gov-lbr.etzhayyim.com:law:municipal-government-act"

LBR_CITIES = [
    ("city:monrovia", "Monrovia", "Monrovia", None, 1010970, "https://www.monroviacitycooperation.org/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# LCA (no CONTRACTS entry)
# ---------------------------------------------------------------------------
LCA_CONTRACT = DEFAULT_CONTRACT[1]
LCA_CONTRACT_DID = "did:web:gov-lca.etzhayyim.com:law:municipal-government-act"

LCA_CITIES = [
    ("city:castries", "Castries", "Castries", None, 22000, "https://www.gosl.gov.lc/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MCO (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MCO_CONTRACT = DEFAULT_CONTRACT[1]
MCO_CONTRACT_DID = "did:web:gov-mco.etzhayyim.com:law:municipal-government-act"

MCO_CITIES = [
    ("city:monaco", "Monaco", "Monaco", None, 39244, "https://www.gouv.mc/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MDV (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MDV_CONTRACT = DEFAULT_CONTRACT[1]
MDV_CONTRACT_DID = "did:web:gov-mdv.etzhayyim.com:law:municipal-government-act"

MDV_CITIES = [
    ("city:male", "މާލެ", "Male", None, 133412, "https://www.malecity.gov.mv/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MNP (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MNP_CONTRACT = DEFAULT_CONTRACT[1]
MNP_CONTRACT_DID = "did:web:gov-mnp.etzhayyim.com:law:municipal-government-act"

MNP_CITIES = [
    ("city:saipan", "Saipan", "Saipan", None, 48220, "https://www.cnmi-gov.mp/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# MRT (no CONTRACTS entry)
# ---------------------------------------------------------------------------
MRT_CONTRACT = DEFAULT_CONTRACT[1]
MRT_CONTRACT_DID = "did:web:gov-mrt.etzhayyim.com:law:municipal-government-act"

MRT_CITIES = [
    ("city:nouakchott", "نواكشوط", "Nouakchott", None, 1205000, "https://www.mauritania.mr/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# NZL (no CONTRACTS entry)
# ---------------------------------------------------------------------------
NZL_CONTRACT = DEFAULT_CONTRACT[1]
NZL_CONTRACT_DID = "did:web:gov-nzl.etzhayyim.com:law:municipal-government-act"

NZL_CITIES = [
    ("city:wellington", "Wellington", "Wellington", None, 215400, "https://www.wellington.govt.nz/", "capital", "capital-district"),
    ("city:auckland", "Auckland", "Auckland", None, 1657200, "https://www.aucklandcouncil.govt.nz/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PLW (no CONTRACTS entry)
# ---------------------------------------------------------------------------
PLW_CONTRACT = DEFAULT_CONTRACT[1]
PLW_CONTRACT_DID = "did:web:gov-plw.etzhayyim.com:law:municipal-government-act"

PLW_CITIES = [
    ("city:ngerulmud", "Ngerulmud", "Ngerulmud", None, 391, "https://www.palaugov.pw/", "capital", "capital-district"),
    ("city:koror", "Koror", "Koror", None, 11754, "https://www.koror.gov.pw/", "city", "capital-district"),
]

# ---------------------------------------------------------------------------
# PNG (no CONTRACTS entry)
# ---------------------------------------------------------------------------
PNG_CONTRACT = DEFAULT_CONTRACT[1]
PNG_CONTRACT_DID = "did:web:gov-png.etzhayyim.com:law:municipal-government-act"

PNG_CITIES = [
    ("city:port-moresby", "Port Moresby", "Port Moresby", None, 364125, "https://www.ncdc.gov.pg/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# PRI (no CONTRACTS entry)
# ---------------------------------------------------------------------------
PRI_CONTRACT = DEFAULT_CONTRACT[1]
PRI_CONTRACT_DID = "did:web:gov-pri.etzhayyim.com:law:municipal-government-act"

PRI_CITIES = [
    ("city:san-juan", "San Juan", "San Juan", None, 318441, "https://www.sanjuanciudadcapital.com/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SLB (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SLB_CONTRACT = DEFAULT_CONTRACT[1]
SLB_CONTRACT_DID = "did:web:gov-slb.etzhayyim.com:law:municipal-government-act"

SLB_CITIES = [
    ("city:honiara", "Honiara", "Honiara", None, 82000, "https://www.hcc.gov.sb/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SLE (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SLE_CONTRACT = DEFAULT_CONTRACT[1]
SLE_CONTRACT_DID = "did:web:gov-sle.etzhayyim.com:law:municipal-government-act"

SLE_CITIES = [
    ("city:freetown", "Freetown", "Freetown", None, 1055964, "https://www.fcc.gov.sl/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SOM (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SOM_CONTRACT = DEFAULT_CONTRACT[1]
SOM_CONTRACT_DID = "did:web:gov-som.etzhayyim.com:law:municipal-government-act"

SOM_CITIES = [
    ("city:mogadishu", "Muqdisho", "Mogadishu", None, 2587183, "https://www.mogadishucity.gov.so/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SSD (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SSD_CONTRACT = DEFAULT_CONTRACT[1]
SSD_CONTRACT_DID = "did:web:gov-ssd.etzhayyim.com:law:municipal-government-act"

SSD_CITIES = [
    ("city:juba", "Juba", "Juba", None, 400000, "https://www.goss.org/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# STP (no CONTRACTS entry)
# ---------------------------------------------------------------------------
STP_CONTRACT = DEFAULT_CONTRACT[1]
STP_CONTRACT_DID = "did:web:gov-stp.etzhayyim.com:law:municipal-government-act"

STP_CITIES = [
    ("city:sao-tome", "São Tomé", "São Tomé", None, 90000, "https://www.presidencia.st/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SUR (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SUR_CONTRACT = DEFAULT_CONTRACT[1]
SUR_CONTRACT_DID = "did:web:gov-sur.etzhayyim.com:law:municipal-government-act"

SUR_CITIES = [
    ("city:paramaribo", "Paramaribo", "Paramaribo", None, 241000, "https://www.sr.gov.sr/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# SYC (no CONTRACTS entry)
# ---------------------------------------------------------------------------
SYC_CONTRACT = DEFAULT_CONTRACT[1]
SYC_CONTRACT_DID = "did:web:gov-syc.etzhayyim.com:law:municipal-government-act"

SYC_CITIES = [
    ("city:victoria", "Victoria", "Victoria", None, 26450, "https://www.gov.sc/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TLS (no CONTRACTS entry)
# ---------------------------------------------------------------------------
TLS_CONTRACT = DEFAULT_CONTRACT[1]
TLS_CONTRACT_DID = "did:web:gov-tls.etzhayyim.com:law:municipal-government-act"

TLS_CITIES = [
    ("city:dili", "Dili", "Dili", None, 222323, "https://www.mof.gov.tl/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TON (no CONTRACTS entry)
# ---------------------------------------------------------------------------
TON_CONTRACT = DEFAULT_CONTRACT[1]
TON_CONTRACT_DID = "did:web:gov-ton.etzhayyim.com:law:municipal-government-act"

TON_CITIES = [
    ("city:nukualofa", "Nukuʻalofa", "Nuku'alofa", None, 23658, "https://www.gov.to/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# TUV (no CONTRACTS entry)
# ---------------------------------------------------------------------------
TUV_CONTRACT = DEFAULT_CONTRACT[1]
TUV_CONTRACT_DID = "did:web:gov-tuv.etzhayyim.com:law:municipal-government-act"

TUV_CITIES = [
    ("city:funafuti", "Funafuti", "Funafuti", None, 6025, "https://www.tuvalu.tv/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# VUT (no CONTRACTS entry)
# ---------------------------------------------------------------------------
VUT_CONTRACT = DEFAULT_CONTRACT[1]
VUT_CONTRACT_DID = "did:web:gov-vut.etzhayyim.com:law:municipal-government-act"

VUT_CITIES = [
    ("city:port-vila", "Port-Vila", "Port Vila", None, 53000, "https://www.vanuatu.gov.vu/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# WSM (no CONTRACTS entry)
# ---------------------------------------------------------------------------
WSM_CONTRACT = DEFAULT_CONTRACT[1]
WSM_CONTRACT_DID = "did:web:gov-wsm.etzhayyim.com:law:municipal-government-act"

WSM_CITIES = [
    ("city:apia", "Apia", "Apia", None, 37391, "https://www.samoagovt.ws/", "capital", "capital-district"),
]

# ---------------------------------------------------------------------------
# HTI already done above
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Master data map: cc -> list of municipality tuples + contract info
# tuple format: (path, name, nameEn, adminCode, population, website, municipalType, parentPath)
# ---------------------------------------------------------------------------
MUNICIPALITY_DATA = {
    "jpn": {
        "records": JPN_DESIGNATED + JPN_SPECIAL_WARDS + JPN_CAPITALS,
        "contract": JPN_CONTRACT,
        "contractDid": JPN_CONTRACT_DID,
    },
    "usa": {
        "records": USA_CAPITALS,
        "contract": USA_CONTRACT,
        "contractDid": USA_CONTRACT_DID,
    },
    "deu": {
        "records": DEU_CAPITALS,
        "contract": DEU_CONTRACT,
        "contractDid": DEU_CONTRACT_DID,
    },
    "fra": {
        "records": FRA_CAPITALS,
        "contract": FRA_CONTRACT,
        "contractDid": FRA_CONTRACT_DID,
    },
    "gbr": {
        "records": GBR_CITIES,
        "contract": GBR_CONTRACT,
        "contractDid": GBR_CONTRACT_DID,
    },
    "ita": {
        "records": ITA_CAPITALS,
        "contract": ITA_CONTRACT,
        "contractDid": ITA_CONTRACT_DID,
    },
    "can": {
        "records": CAN_CITIES,
        "contract": CAN_CONTRACT,
        "contractDid": CAN_CONTRACT_DID,
    },
    "aus": {
        "records": AUS_CAPITALS,
        "contract": AUS_CONTRACT,
        "contractDid": AUS_CONTRACT_DID,
    },
    "kor": {
        "records": KOR_CAPITALS,
        "contract": KOR_CONTRACT,
        "contractDid": KOR_CONTRACT_DID,
    },
    "ind": {
        "records": IND_CAPITALS,
        "contract": IND_CONTRACT,
        "contractDid": IND_CONTRACT_DID,
    },
    "bra": {
        "records": BRA_CAPITALS,
        "contract": BRA_CONTRACT,
        "contractDid": BRA_CONTRACT_DID,
    },
    "chn": {
        "records": CHN_CITIES,
        "contract": CHN_CONTRACT,
        "contractDid": CHN_CONTRACT_DID,
    },
    "rus": {
        "records": RUS_CITIES,
        "contract": RUS_CONTRACT,
        "contractDid": RUS_CONTRACT_DID,
    },
    "mex": {
        "records": MEX_CITIES,
        "contract": MEX_CONTRACT,
        "contractDid": MEX_CONTRACT_DID,
    },
    "sau": {
        "records": SAU_CITIES,
        "contract": SAU_CONTRACT,
        "contractDid": SAU_CONTRACT_DID,
    },
    "tur": {
        "records": TUR_CITIES,
        "contract": TUR_CONTRACT,
        "contractDid": TUR_CONTRACT_DID,
    },
    "arg": {
        "records": ARG_CITIES,
        "contract": ARG_CONTRACT,
        "contractDid": ARG_CONTRACT_DID,
    },
    "zaf": {
        "records": ZAF_CITIES,
        "contract": ZAF_CONTRACT,
        "contractDid": ZAF_CONTRACT_DID,
    },
    "idn": {
        "records": IDN_CITIES,
        "contract": IDN_CONTRACT,
        "contractDid": IDN_CONTRACT_DID,
    },
    # --- New entries ---
    "esp": {"records": ESP_CITIES, "contract": ESP_CONTRACT, "contractDid": ESP_CONTRACT_DID},
    "nld": {"records": NLD_CITIES, "contract": NLD_CONTRACT, "contractDid": NLD_CONTRACT_DID},
    "bel": {"records": BEL_CITIES, "contract": BEL_CONTRACT, "contractDid": BEL_CONTRACT_DID},
    "che": {"records": CHE_CITIES, "contract": CHE_CONTRACT, "contractDid": CHE_CONTRACT_DID},
    "aut": {"records": AUT_CITIES, "contract": AUT_CONTRACT, "contractDid": AUT_CONTRACT_DID},
    "pol": {"records": POL_CITIES, "contract": POL_CONTRACT, "contractDid": POL_CONTRACT_DID},
    "swe": {"records": SWE_CITIES, "contract": SWE_CONTRACT, "contractDid": SWE_CONTRACT_DID},
    "nor": {"records": NOR_CITIES, "contract": NOR_CONTRACT, "contractDid": NOR_CONTRACT_DID},
    "dnk": {"records": DNK_CITIES, "contract": DNK_CONTRACT, "contractDid": DNK_CONTRACT_DID},
    "fin": {"records": FIN_CITIES, "contract": FIN_CONTRACT, "contractDid": FIN_CONTRACT_DID},
    "prt": {"records": PRT_CITIES, "contract": PRT_CONTRACT, "contractDid": PRT_CONTRACT_DID},
    "grc": {"records": GRC_CITIES, "contract": GRC_CONTRACT, "contractDid": GRC_CONTRACT_DID},
    "cze": {"records": CZE_CITIES, "contract": CZE_CONTRACT, "contractDid": CZE_CONTRACT_DID},
    "hun": {"records": HUN_CITIES, "contract": HUN_CONTRACT, "contractDid": HUN_CONTRACT_DID},
    "rou": {"records": ROU_CITIES, "contract": ROU_CONTRACT, "contractDid": ROU_CONTRACT_DID},
    "ukr": {"records": UKR_CITIES, "contract": UKR_CONTRACT, "contractDid": UKR_CONTRACT_DID},
    "bgr": {"records": BGR_CITIES, "contract": BGR_CONTRACT, "contractDid": BGR_CONTRACT_DID},
    "hrv": {"records": HRV_CITIES, "contract": HRV_CONTRACT, "contractDid": HRV_CONTRACT_DID},
    "srb": {"records": SRB_CITIES, "contract": SRB_CONTRACT, "contractDid": SRB_CONTRACT_DID},
    "svk": {"records": SVK_CITIES, "contract": SVK_CONTRACT, "contractDid": SVK_CONTRACT_DID},
    "svn": {"records": SVN_CITIES, "contract": SVN_CONTRACT, "contractDid": SVN_CONTRACT_DID},
    "alb": {"records": ALB_CITIES, "contract": ALB_CONTRACT, "contractDid": ALB_CONTRACT_DID},
    "bih": {"records": BIH_CITIES, "contract": BIH_CONTRACT, "contractDid": BIH_CONTRACT_DID},
    "mkd": {"records": MKD_CITIES, "contract": MKD_CONTRACT, "contractDid": MKD_CONTRACT_DID},
    "geo": {"records": GEO_CITIES, "contract": GEO_CONTRACT, "contractDid": GEO_CONTRACT_DID},
    "est": {"records": EST_CITIES, "contract": EST_CONTRACT, "contractDid": EST_CONTRACT_DID},
    "ltu": {"records": LTU_CITIES, "contract": LTU_CONTRACT, "contractDid": LTU_CONTRACT_DID},
    "lva": {"records": LVA_CITIES, "contract": LVA_CONTRACT, "contractDid": LVA_CONTRACT_DID},
    "isl": {"records": ISL_CITIES, "contract": ISL_CONTRACT, "contractDid": ISL_CONTRACT_DID},
    "lux": {"records": LUX_CITIES, "contract": LUX_CONTRACT, "contractDid": LUX_CONTRACT_DID},
    "cyp": {"records": CYP_CITIES, "contract": CYP_CONTRACT, "contractDid": CYP_CONTRACT_DID},
    "irl": {"records": IRL_CITIES, "contract": IRL_CONTRACT, "contractDid": IRL_CONTRACT_DID},
    "qat": {"records": QAT_CITIES, "contract": QAT_CONTRACT, "contractDid": QAT_CONTRACT_DID},
    "kwt": {"records": KWT_CITIES, "contract": KWT_CONTRACT, "contractDid": KWT_CONTRACT_DID},
    "omn": {"records": OMN_CITIES, "contract": OMN_CONTRACT, "contractDid": OMN_CONTRACT_DID},
    "jor": {"records": JOR_CITIES, "contract": JOR_CONTRACT, "contractDid": JOR_CONTRACT_DID},
    "lbn": {"records": LBN_CITIES, "contract": LBN_CONTRACT, "contractDid": LBN_CONTRACT_DID},
    "irn": {"records": IRN_CITIES, "contract": IRN_CONTRACT, "contractDid": IRN_CONTRACT_DID},
    "irq": {"records": IRQ_CITIES, "contract": IRQ_CONTRACT, "contractDid": IRQ_CONTRACT_DID},
    "syr": {"records": SYR_CITIES, "contract": SYR_CONTRACT, "contractDid": SYR_CONTRACT_DID},
    "yem": {"records": YEM_CITIES, "contract": YEM_CONTRACT, "contractDid": YEM_CONTRACT_DID},
    "pak": {"records": PAK_CITIES, "contract": PAK_CONTRACT, "contractDid": PAK_CONTRACT_DID},
    "bgd": {"records": BGD_CITIES, "contract": BGD_CONTRACT, "contractDid": BGD_CONTRACT_DID},
    "lka": {"records": LKA_CITIES, "contract": LKA_CONTRACT, "contractDid": LKA_CONTRACT_DID},
    "npl": {"records": NPL_CITIES, "contract": NPL_CONTRACT, "contractDid": NPL_CONTRACT_DID},
    "mmr": {"records": MMR_CITIES, "contract": MMR_CONTRACT, "contractDid": MMR_CONTRACT_DID},
    "tha": {"records": THA_CITIES, "contract": THA_CONTRACT, "contractDid": THA_CONTRACT_DID},
    "vnm": {"records": VNM_CITIES, "contract": VNM_CONTRACT, "contractDid": VNM_CONTRACT_DID},
    "phl": {"records": PHL_CITIES, "contract": PHL_CONTRACT, "contractDid": PHL_CONTRACT_DID},
    "mys": {"records": MYS_CITIES, "contract": MYS_CONTRACT, "contractDid": MYS_CONTRACT_DID},
    "sgp": {"records": SGP_CITIES, "contract": SGP_CONTRACT, "contractDid": SGP_CONTRACT_DID},
    "khm": {"records": KHM_CITIES, "contract": KHM_CONTRACT, "contractDid": KHM_CONTRACT_DID},
    "lao": {"records": LAO_CITIES, "contract": LAO_CONTRACT, "contractDid": LAO_CONTRACT_DID},
    "zwe": {"records": ZWE_CITIES, "contract": ZWE_CONTRACT, "contractDid": ZWE_CONTRACT_DID},
    "ken": {"records": KEN_CITIES, "contract": KEN_CONTRACT, "contractDid": KEN_CONTRACT_DID},
    "tza": {"records": TZA_CITIES, "contract": TZA_CONTRACT, "contractDid": TZA_CONTRACT_DID},
    "nga": {"records": NGA_CITIES, "contract": NGA_CONTRACT, "contractDid": NGA_CONTRACT_DID},
    "eth": {"records": ETH_CITIES, "contract": ETH_CONTRACT, "contractDid": ETH_CONTRACT_DID},
    "gha": {"records": GHA_CITIES, "contract": GHA_CONTRACT, "contractDid": GHA_CONTRACT_DID},
    "cmr": {"records": CMR_CITIES, "contract": CMR_CONTRACT, "contractDid": CMR_CONTRACT_DID},
    "sen": {"records": SEN_CITIES, "contract": SEN_CONTRACT, "contractDid": SEN_CONTRACT_DID},
    "ago": {"records": AGO_CITIES, "contract": AGO_CONTRACT, "contractDid": AGO_CONTRACT_DID},
    "cod": {"records": COD_CITIES, "contract": COD_CONTRACT, "contractDid": COD_CONTRACT_DID},
    "uga": {"records": UGA_CITIES, "contract": UGA_CONTRACT, "contractDid": UGA_CONTRACT_DID},
    "moz": {"records": MOZ_CITIES, "contract": MOZ_CONTRACT, "contractDid": MOZ_CONTRACT_DID},
    "mdg": {"records": MDG_CITIES, "contract": MDG_CONTRACT, "contractDid": MDG_CONTRACT_DID},
    "rwa": {"records": RWA_CITIES, "contract": RWA_CONTRACT, "contractDid": RWA_CONTRACT_DID},
    "civ": {"records": CIV_CITIES, "contract": CIV_CONTRACT, "contractDid": CIV_CONTRACT_DID},
    "bfa": {"records": BFA_CITIES, "contract": BFA_CONTRACT, "contractDid": BFA_CONTRACT_DID},
    "mli": {"records": MLI_CITIES, "contract": MLI_CONTRACT, "contractDid": MLI_CONTRACT_DID},
    "ner": {"records": NER_CITIES, "contract": NER_CONTRACT, "contractDid": NER_CONTRACT_DID},
    "tcd": {"records": TCD_CITIES, "contract": TCD_CONTRACT, "contractDid": TCD_CONTRACT_DID},
    "gin": {"records": GIN_CITIES, "contract": GIN_CONTRACT, "contractDid": GIN_CONTRACT_DID},
    "tgo": {"records": TGO_CITIES, "contract": TGO_CONTRACT, "contractDid": TGO_CONTRACT_DID},
    "ben": {"records": BEN_CITIES, "contract": BEN_CONTRACT, "contractDid": BEN_CONTRACT_DID},
    "nam": {"records": NAM_CITIES, "contract": NAM_CONTRACT, "contractDid": NAM_CONTRACT_DID},
    "bwa": {"records": BWA_CITIES, "contract": BWA_CONTRACT, "contractDid": BWA_CONTRACT_DID},
    "lso": {"records": LSO_CITIES, "contract": LSO_CONTRACT, "contractDid": LSO_CONTRACT_DID},
    "swz": {"records": SWZ_CITIES, "contract": SWZ_CONTRACT, "contractDid": SWZ_CONTRACT_DID},
    "mwi": {"records": MWI_CITIES, "contract": MWI_CONTRACT, "contractDid": MWI_CONTRACT_DID},
    "zmb": {"records": ZMB_CITIES, "contract": ZMB_CONTRACT, "contractDid": ZMB_CONTRACT_DID},
    "col": {"records": COL_CITIES, "contract": COL_CONTRACT, "contractDid": COL_CONTRACT_DID},
    "ven": {"records": VEN_CITIES, "contract": VEN_CONTRACT, "contractDid": VEN_CONTRACT_DID},
    "per": {"records": PER_CITIES, "contract": PER_CONTRACT, "contractDid": PER_CONTRACT_DID},
    "chl": {"records": CHL_CITIES, "contract": CHL_CONTRACT, "contractDid": CHL_CONTRACT_DID},
    "ecu": {"records": ECU_CITIES, "contract": ECU_CONTRACT, "contractDid": ECU_CONTRACT_DID},
    "bol": {"records": BOL_CITIES, "contract": BOL_CONTRACT, "contractDid": BOL_CONTRACT_DID},
    "pry": {"records": PRY_CITIES, "contract": PRY_CONTRACT, "contractDid": PRY_CONTRACT_DID},
    "ury": {"records": URY_CITIES, "contract": URY_CONTRACT, "contractDid": URY_CONTRACT_DID},
    "pan": {"records": PAN_CITIES, "contract": PAN_CONTRACT, "contractDid": PAN_CONTRACT_DID},
    "cri": {"records": CRI_CITIES, "contract": CRI_CONTRACT, "contractDid": CRI_CONTRACT_DID},
    "gtm": {"records": GTM_CITIES, "contract": GTM_CONTRACT, "contractDid": GTM_CONTRACT_DID},
    "hnd": {"records": HND_CITIES, "contract": HND_CONTRACT, "contractDid": HND_CONTRACT_DID},
    "slv": {"records": SLV_CITIES, "contract": SLV_CONTRACT, "contractDid": SLV_CONTRACT_DID},
    "nic": {"records": NIC_CITIES, "contract": NIC_CONTRACT, "contractDid": NIC_CONTRACT_DID},
    "dom": {"records": DOM_CITIES, "contract": DOM_CONTRACT, "contractDid": DOM_CONTRACT_DID},
    "cub": {"records": CUB_CITIES, "contract": CUB_CONTRACT, "contractDid": CUB_CONTRACT_DID},
    "jam": {"records": JAM_CITIES, "contract": JAM_CONTRACT, "contractDid": JAM_CONTRACT_DID},
    "guy": {"records": GUY_CITIES, "contract": GUY_CONTRACT, "contractDid": GUY_CONTRACT_DID},
    "kaz": {"records": KAZ_CITIES, "contract": KAZ_CONTRACT, "contractDid": KAZ_CONTRACT_DID},
    "uzb": {"records": UZB_CITIES, "contract": UZB_CONTRACT, "contractDid": UZB_CONTRACT_DID},
    "tkm": {"records": TKM_CITIES, "contract": TKM_CONTRACT, "contractDid": TKM_CONTRACT_DID},
    "kgz": {"records": KGZ_CITIES, "contract": KGZ_CONTRACT, "contractDid": KGZ_CONTRACT_DID},
    "tjk": {"records": TJK_CITIES, "contract": TJK_CONTRACT, "contractDid": TJK_CONTRACT_DID},
    "arm": {"records": ARM_CITIES, "contract": ARM_CONTRACT, "contractDid": ARM_CONTRACT_DID},
    "aze": {"records": AZE_CITIES, "contract": AZE_CONTRACT, "contractDid": AZE_CONTRACT_DID},
    "blr": {"records": BLR_CITIES, "contract": BLR_CONTRACT, "contractDid": BLR_CONTRACT_DID},
    "afg": {"records": AFG_CITIES, "contract": AFG_CONTRACT, "contractDid": AFG_CONTRACT_DID},
    "dza": {"records": DZA_CITIES, "contract": DZA_CONTRACT, "contractDid": DZA_CONTRACT_DID},
    "egy": {"records": EGY_CITIES, "contract": EGY_CONTRACT, "contractDid": EGY_CONTRACT_DID},
    "isr": {"records": ISR_CITIES, "contract": ISR_CONTRACT, "contractDid": ISR_CONTRACT_DID},
    "mar": {"records": MAR_CITIES, "contract": MAR_CONTRACT, "contractDid": MAR_CONTRACT_DID},
    "sdn": {"records": SDN_CITIES, "contract": SDN_CONTRACT, "contractDid": SDN_CONTRACT_DID},
    "mng": {"records": MNG_CITIES, "contract": MNG_CONTRACT, "contractDid": MNG_CONTRACT_DID},
    "prk": {"records": PRK_CITIES, "contract": PRK_CONTRACT, "contractDid": PRK_CONTRACT_DID},
    "pse": {"records": PSE_CITIES, "contract": PSE_CONTRACT, "contractDid": PSE_CONTRACT_DID},
    "twn": {"records": TWN_CITIES, "contract": TWN_CONTRACT, "contractDid": TWN_CONTRACT_DID},
    "tun": {"records": TUN_CITIES, "contract": TUN_CONTRACT, "contractDid": TUN_CONTRACT_DID},
    "xkx": {"records": XKX_CITIES, "contract": XKX_CONTRACT, "contractDid": XKX_CONTRACT_DID},
    "bdi": {"records": BDI_CITIES, "contract": BDI_CONTRACT, "contractDid": BDI_CONTRACT_DID},
    "bhs": {"records": BHS_CITIES, "contract": BHS_CONTRACT, "contractDid": BHS_CONTRACT_DID},
    "blz": {"records": BLZ_CITIES, "contract": BLZ_CONTRACT, "contractDid": BLZ_CONTRACT_DID},
    "brn": {"records": BRN_CITIES, "contract": BRN_CONTRACT, "contractDid": BRN_CONTRACT_DID},
    "btn": {"records": BTN_CITIES, "contract": BTN_CONTRACT, "contractDid": BTN_CONTRACT_DID},
    "caf": {"records": CAF_CITIES, "contract": CAF_CONTRACT, "contractDid": CAF_CONTRACT_DID},
    "cog": {"records": COG_CITIES, "contract": COG_CONTRACT, "contractDid": COG_CONTRACT_DID},
    "com": {"records": COM_CITIES, "contract": COM_CONTRACT, "contractDid": COM_CONTRACT_DID},
    "cpv": {"records": CPV_CITIES, "contract": CPV_CONTRACT, "contractDid": CPV_CONTRACT_DID},
    "dji": {"records": DJI_CITIES, "contract": DJI_CONTRACT, "contractDid": DJI_CONTRACT_DID},
    "eri": {"records": ERI_CITIES, "contract": ERI_CONTRACT, "contractDid": ERI_CONTRACT_DID},
    "fji": {"records": FJI_CITIES, "contract": FJI_CONTRACT, "contractDid": FJI_CONTRACT_DID},
    "gmb": {"records": GMB_CITIES, "contract": GMB_CONTRACT, "contractDid": GMB_CONTRACT_DID},
    "gnb": {"records": GNB_CITIES, "contract": GNB_CONTRACT, "contractDid": GNB_CONTRACT_DID},
    "gnq": {"records": GNQ_CITIES, "contract": GNQ_CONTRACT, "contractDid": GNQ_CONTRACT_DID},
    "hti": {"records": HTI_CITIES, "contract": HTI_CONTRACT, "contractDid": HTI_CONTRACT_DID},
    "kir": {"records": KIR_CITIES, "contract": KIR_CONTRACT, "contractDid": KIR_CONTRACT_DID},
    "lbr": {"records": LBR_CITIES, "contract": LBR_CONTRACT, "contractDid": LBR_CONTRACT_DID},
    "lca": {"records": LCA_CITIES, "contract": LCA_CONTRACT, "contractDid": LCA_CONTRACT_DID},
    "mco": {"records": MCO_CITIES, "contract": MCO_CONTRACT, "contractDid": MCO_CONTRACT_DID},
    "mdv": {"records": MDV_CITIES, "contract": MDV_CONTRACT, "contractDid": MDV_CONTRACT_DID},
    "mnp": {"records": MNP_CITIES, "contract": MNP_CONTRACT, "contractDid": MNP_CONTRACT_DID},
    "mrt": {"records": MRT_CITIES, "contract": MRT_CONTRACT, "contractDid": MRT_CONTRACT_DID},
    "nzl": {"records": NZL_CITIES, "contract": NZL_CONTRACT, "contractDid": NZL_CONTRACT_DID},
    "plw": {"records": PLW_CITIES, "contract": PLW_CONTRACT, "contractDid": PLW_CONTRACT_DID},
    "png": {"records": PNG_CITIES, "contract": PNG_CONTRACT, "contractDid": PNG_CONTRACT_DID},
    "pri": {"records": PRI_CITIES, "contract": PRI_CONTRACT, "contractDid": PRI_CONTRACT_DID},
    "slb": {"records": SLB_CITIES, "contract": SLB_CONTRACT, "contractDid": SLB_CONTRACT_DID},
    "sle": {"records": SLE_CITIES, "contract": SLE_CONTRACT, "contractDid": SLE_CONTRACT_DID},
    "som": {"records": SOM_CITIES, "contract": SOM_CONTRACT, "contractDid": SOM_CONTRACT_DID},
    "ssd": {"records": SSD_CITIES, "contract": SSD_CONTRACT, "contractDid": SSD_CONTRACT_DID},
    "stp": {"records": STP_CITIES, "contract": STP_CONTRACT, "contractDid": STP_CONTRACT_DID},
    "sur": {"records": SUR_CITIES, "contract": SUR_CONTRACT, "contractDid": SUR_CONTRACT_DID},
    "syc": {"records": SYC_CITIES, "contract": SYC_CONTRACT, "contractDid": SYC_CONTRACT_DID},
    "tls": {"records": TLS_CITIES, "contract": TLS_CONTRACT, "contractDid": TLS_CONTRACT_DID},
    "ton": {"records": TON_CITIES, "contract": TON_CONTRACT, "contractDid": TON_CONTRACT_DID},
    "tuv": {"records": TUV_CITIES, "contract": TUV_CONTRACT, "contractDid": TUV_CONTRACT_DID},
    "vut": {"records": VUT_CITIES, "contract": VUT_CONTRACT, "contractDid": VUT_CONTRACT_DID},
    "wsm": {"records": WSM_CITIES, "contract": WSM_CONTRACT, "contractDid": WSM_CONTRACT_DID},
}

# ---------------------------------------------------------------------------
# Helper: get contract for a cc
# ---------------------------------------------------------------------------
def get_contract_tuple(cc):
    return CONTRACTS.get(cc, DEFAULT_CONTRACT)


def make_contract_did(cc, slug):
    return f"did:web:gov-{cc}.etzhayyim.com:law:{slug}"


def make_parent_did(cc, parent_path):
    return f"did:web:gov-{cc}.etzhayyim.com:{parent_path}"


def build_municipality_record(cc, row, contract_name, contract_did):
    path, name, name_en, admin_code, population, website, municipal_type, parent_path = row

    tags = ["cofog:01", "municipality", "l6", municipal_type]

    rec = {
        "path": path,
        "name": name,
        "nameEn": name_en,
        "population": population,
        "website": website,
        "contract": contract_name,
        "contractDid": contract_did,
        "parentPath": parent_path,
        "parentDid": make_parent_did(cc, parent_path),
        "orgTier": "municipality",
        "municipalType": municipal_type,
        "countryCode": cc,
        "tags": tags,
    }

    if admin_code is not None:
        rec["adminCode"] = admin_code

    # Reorder to match spec schema order
    ordered = {}
    for key in ["path", "name", "nameEn", "adminCode", "population", "website",
                "contract", "contractDid", "parentPath", "parentDid",
                "orgTier", "municipalType", "countryCode", "tags"]:
        if key in rec:
            ordered[key] = rec[key]

    return ordered


def build_contract_record(cc, contract_tuple):
    name, name_en, slug, legal_basis, effective_date, url = contract_tuple
    contract_did = make_contract_did(cc, slug)
    gov_level = CONTRACT_GOVLEVEL.get(cc, "municipality")
    tags = ["local-government", cc, "law"]

    return {
        "contractDid": contract_did,
        "contractSlug": slug,
        "name": name,
        "nameEn": name_en,
        "legalBasis": legal_basis,
        "effectiveDate": effective_date,
        "url": url,
        "govLevel": gov_level,
        "cofogCode": "01",
        "countryCode": cc,
        "tags": tags,
    }


def write_ndjson(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    # Determine data/gov/ base path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is in tools/, data is at ../data/gov/
    base_dir = os.path.join(script_dir, "..", "data", "gov")
    base_dir = os.path.normpath(base_dir)

    if not os.path.isdir(base_dir):
        print(f"ERROR: {base_dir} not found. Run from etzhayyim-project-states/ directory.", file=sys.stderr)
        sys.exit(1)

    # Collect all existing country dirs
    country_dirs = sorted([
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and len(d) == 3 and d.isalpha()
    ])

    print(f"Found {len(country_dirs)} country directories under {base_dir}")

    contract_count = 0
    municipality_count = 0
    municipality_records_total = 0
    skipped = []

    for cc in country_dirs:
        cc_dir = os.path.join(base_dir, cc)

        # ----- contract.ndjson -----
        contract_tuple = get_contract_tuple(cc)
        contract_rec = build_contract_record(cc, contract_tuple)
        contract_path = os.path.join(cc_dir, "contract.ndjson")
        write_ndjson(contract_path, [contract_rec])
        contract_count += 1

        # ----- municipality.ndjson -----
        # Skip jpn if municipality.ndjson already exists
        muni_path = os.path.join(cc_dir, "municipality.ndjson")
        if cc == "jpn" and os.path.exists(muni_path):
            skipped.append(cc)
            continue

        if cc not in MUNICIPALITY_DATA:
            # No municipality data for this cc
            continue

        data = MUNICIPALITY_DATA[cc]
        records = data["records"]
        contract_name = data["contract"]
        contract_did = data["contractDid"]

        # Deduplicate by path
        seen_paths = set()
        muni_records = []
        for row in records:
            path = row[0]
            if path in seen_paths:
                print(f"  WARNING: duplicate path {path} in {cc}, skipping duplicate")
                continue
            seen_paths.add(path)
            muni_records.append(build_municipality_record(cc, row, contract_name, contract_did))

        write_ndjson(muni_path, muni_records)
        municipality_count += 1
        municipality_records_total += len(muni_records)
        print(f"  {cc}: wrote {len(muni_records)} municipality records")

    print()
    print("=== Summary ===")
    print(f"contract.ndjson files written : {contract_count}")
    print(f"municipality.ndjson files written: {municipality_count}")
    print(f"Total municipality records       : {municipality_records_total}")
    if skipped:
        print(f"Skipped (already exists)        : {', '.join(skipped)}")


if __name__ == "__main__":
    main()
