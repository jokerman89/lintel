# Prioriterad åtgärdslista

Förslag efter granskning av main `28061e4`, 2026-09-20. Inga produktändringar är genomförda.
Varje kort nedan är ett sammanhållet resultat. Vid implementation delas det i korta, verifierbara
deluppgifter enligt ADR0026; exekvering och oberoende granskning sker per arbetspaket.
Kortnumren är granskningsförslag, inte en parallell ersättningsbacklog för senare godkänd plan.

**Bevarandeprincip, uttryckligen bekräftad av användaren:** optimera, rätta och berika.
Alla värdefulla funktioner, användningsfall och specialistmetoder ska finnas kvar. En
sammanslagning måste först visa vart varje sådant värde tar vägen och verifiera det efteråt.
Ett valbart paket ska vara lätt att upptäcka och använda. Ofärdig funktion ska få en
utvecklingsväg. Borttagning är bara en kandidat när eget värde saknas eller en fullständig
ersättning är bevisad; ingen sådan borttagning är beslutad här. Färre filer är inget mål.

## Först: korrekt beslutsgrund och skydd för befintligt arbete

### A01 — Ta bort osäkra kör- och återställningsrecept

**Prioritet:** P1. **Beroenden:** inga. **Belägg:** CP-01/02/13, AG-01, RU-07.

Ersätt `eval` i kontextladdning med literal sökvägs-/globhantering. Ge snapshot/restore en
testad hjälpare med normaliserade, ägda sökvägar och verifierad kopia. Isolera bisect och
refaktoreringsförsök; rollback får bara omfatta egna ändringar och godkänt återställningsläge.
URL-listor måste skilja exakt värd från uttrycklig wildcard och kontrollera omdirigeringar.

**Klart när:** syntetiska fall med mellanslag, metatecken, gamla snapshots, annan användares
ändringar, avbruten återställning och sibling-domäner bevarar data och respekterar vald gräns.

### A02 — Gör obligatoriska kontroller omöjliga att räkna bort

**Prioritet:** P1. **Beroenden:** fastställ kontrollkontraktet tillsammans med A07.
**Belägg:** WF-01/08, AG-03/04/11, CP-08.

Separera obligatoriskt/advisory, tillämpligt/ej tillämpligt, godkänt/underkänt/ej verifierat och
fel vid kontroll. Ett obligatoriskt fel ska stoppa oavsett snittpoäng eller antal andra gröna
kontroller. Rätta konkreta fel i regelverksrollerna och kräv källa, version och tillämplighet.
Behåll smak- och förbättringspoäng som rådgivning, separat från godkännandet.

**Klart när:** ett ensamt obligatoriskt fel, normaltext med 3,5:1 kontrast, saknad browser,
noll körda tester och okänd policy aldrig blir verifierat grönt. Rådgivande avvikelser får inte
automatiskt behandlas som obligatoriska krav. Eventuella undantag härleds från faktisk policy.

### A03 — Bind review och leverans till exakt samma innehåll

**Prioritet:** P1. **Beroenden:** inga för läsarbuggar; A08 för gemensam arbetsreferens.
**Belägg:** WF-02, AG-15, RU-01.

En review ska ange bas, revision, ändrat innehåll inklusive valda okommittade/nya filer,
uppgifts-/paket-ID, täckning och oberoende granskare. Senaste relevanta underkännande ska
gälla framför äldre klartecken. SHIP ska läsa detta bevis och köra granskande QA; en senare
fix ogiltigförklarar berörda resultat. Tid sedan senaste test ersätter inte innehållsidentitet.

**Klart när:** ett ändrat arbetsdokument, ny fil, ändrad konfiguration eller ett senare
underkännande stoppar återanvändning av gammalt klartecken; oförändrade relevanta indata kan
återanvända bevis. Substantiell review förblir oberoende enligt ADR0026.

### A04 — Rätta hjälparnas argument och felreturer

**Prioritet:** P2. **Beroenden:** inga. **Belägg:** RU-04/11.

Rätta ADR-hjälparens argumenthantering och updaterns borttappade felkod. Kontrollera att
dokumenterade anrop går att köra och att underprocessens fel styr rätt fallback/resultat.
Behåll ADR-spårbarhet, multi-host-uppdatering och användbara återställningsvägar.

**Klart när:** dokumenterade titel-/statusanrop fungerar i tomt och befintligt testrepo;
en misslyckad uppdatering ger korrekt fallback eller tydligt misslyckat resultat.

### A25 — Kör endast betrodd implementation från installerad källa

**Prioritet:** P1. **Beroenden:** inga. **Belägg:** RU-02.

Vissa valbara domänhooks och vault-init laddar en exekverbar resolver från målrepot.
Flytta all sådan kodupplösning till verifierad plugin-/installationskälla och läs projektets
konfiguration som data. Bevara domänkontroller och vaultintegrationen. Detta är en spärr
före aktivering av de berörda vilande hookarna, inte ett påstående om standardaktivering.

**Klart när:** en syntetisk resolver i målrepot aldrig exekveras av installerad hook eller
vaultverktyg, medan vald projekt-/företagskonfiguration fortfarande påverkar rätt beslut.

### A26 — Bind privat synk till rätt, uttryckligen aktiverad destination

**Prioritet:** P1. **Beroenden:** inga. **Belägg:** RU-03.

Behåll synk av privata roller och lärdomar. Låt setup, verklig Git-origin och push/pull dela
samma verifierade destinationsbindning. Ett nytt URL-val får inte lämna föregående remote
aktiv bakom ett nytt konfigurationsvärde. Forget ska stoppa framtida synk och bevara lokalt
innehåll. Identifiera projekt stabilt så att likadana katalognamn inte skriver över varandra.

**Klart när:** två lokala testremotes bevisar korrekt byte, avstängd synk efter forget och
bevarat innehåll för två projekt med samma basnamn. Testet behöver ingen extern publicering.

## Gemensam kärna: Universal, profil och arbete

### A05 — Återställ Universal som produktens identitet

**Prioritet:** P1. **Beroenden:** A06 anger vad som får utlovas.
**Belägg:** RT-01/08, AG-02/05, WF-06.

Skriv om README, startguide, enterprise-adoption, arkitekturens ingångar och leveranskrav
kring den gemensamma arbetsmetoden. Lägg installation och klientdetaljer i likvärdiga
adapterguider. Behåll Copilot-kitet. Ta bort företagskontakter och godtyckliga vendor-,
retention- och venture-antaganden ur neutral kärna. Följ den gemensamma genererade
sessionskällan enligt ADR0025; en gammal ADR upphör inte att gälla enbart för att kod avviker.

**Klart när:** en ny användare förstår värdet före klientvalet; alla produktlöften pekar på
verklig implementation eller märkt begränsning. Historiska beslut är tydligt historiska.
Ingen stor flytt av `.claude/` behövs för detta resultat.

### A06 — Inför en sanningsenlig klient- och kapabilitetsmodell

**Prioritet:** P1. **Beroenden:** inga för inventering; verifiering sker i A24.
**Belägg:** RT-02, WF-03, CP-03/04, AG-06; [klientunderlag](client-sources.md).

Skilj CLI, desktop, IDE och cloud även inom samma produktfamilj. Beskriv neutral operation
och adapter för frågor, planering, verktyg, browser, delegation, isolering, minne och hooks.
Registrera både leverantörsförmåga, levererad Lintel-integration och faktiskt testat scenario.
Använd tillgängliga verktyg i sessionen; vanliga samtalsfrågor är en giltig frågeväg.

**Klart när:** inget arbetsflöde dör enbart för att `AskUserQuestion` heter något annat.
Saknad oberoende reviewer ger en ärlig blockerad överlämning, inte falskt oberoende rollspel.
Saknade API:er för pluginstyrning ger ”stöds inte”, inte påhittade `.disabled`-kontroller.

### A07 — Gör den effektiva företagsprofilen stabil och spårbar

**Prioritet:** P1. **Beroenden:** A06 för session/adapter; samordna A02.
**Belägg:** RT-03/04/10, WF-06, CP-07/12, AG-05.

Lös profil och arv strukturerat, dokumentera repo-/företags-/användarprecedens och visa källa
för effektiva värden. Fäst profilidentitet och innehåll över verktygsanrop, agents och återstart.
Skilj neutral första användning från misslyckad laddning av obligatorisk företagspolicy.
Nuvarande advisory-nödfallback är dokumenterad; ändringen kräver ett uttryckligt uppdaterat
kontrakt, inte en tyst omtolkning. Separera paketschema från publik produktversion.

**Klart när:** ett profilbyte mitt i arbetet upptäcks; en trasig obligatorisk profil förblir
ett olöst krav. Ett syntetiskt företag kan se vilka plan-, teknik-, kontroll- och designbeslut
dess profil ändrar. Hemligheter och kundinnehåll behövs inte i den publika testsviten.

### A08 — Låt samma arbetskarta följa hela livscykeln

**Prioritet:** P1/P2. **Beroenden:** inga för mekaniska rättningar.
**Belägg:** RT-05/06, WF-04/05/11/12, CP-16.

Bevara användarens operation separat från ämnet: ”granska releaseplanen” är review.
Skapa cykelidentitet innan fasloggning och kör varje fas en gång. Låt ANALYZE, CAPTURE,
budgetering och återstart använda samma valda arbetskarta som PLAN/BUILD/REVIEW. Bevara
Spec Kit-ID:n och ursprunglig backlog. Läs verkligt ADR-format och håll försenat arbete synligt.

**Klart när:** läsavsikt stannar läsande, två initiativ inte blandas, externa uppgifter uppdateras
på rätt plats och en avbruten cykel kan återtas utan dubbla faser eller förlorad historik.

### A09 — Gör specialistmoduler till tydliga beslut och handoffs

**Prioritet:** P2. **Beroenden:** A02/06/08.
**Belägg:** WF-07/08, AG-08/10.

Behåll domänkunskapen i TA/DA/SC/DH/TQ. Ersätt oklar shell-liknande pseudokod med ett
uttryckligt agentägt protokoll: indata, checkpoint, ägare, resultat, verifiering och återstart.
Fördjupa varje domän med konkreta felmekanismer, genomarbetade exempel, beslutskriterier
och vanliga falsklarm; läs dessa resurser när uppgiften kräver dem. Hjälpare ska göra mekaniska saker. Upptäck moduler i installerad källa och använd giltiga
filnamn på Windows. Ett gemensamt resultatkuvert ska bära krav/revision/bevis, inte en ny backlog.

**Klart när:** en full körning och en avbruten loop producerar de artefakter nästa steg behöver;
en saknad eller underkänd obligatorisk domän kan inte döljas i snittet. Ingen ny scheduler krävs.

### A10 — Förenkla intake och alternativa arbetsflöden

**Prioritet:** P2. **Beroenden:** A06/08.
**Belägg:** WF-05/06; inventoryrader för DEFINE, office-hours, autoplan och plan-tune.

Styr frågor efter beslut som saknas, uppgiftstyp och risk. Företagsmigrering, underhåll och
research ska inte automatiskt få en startupintervju. Gör autoplan/plan-and-build/review-and-ship
till tydliga sammansättningar över samma kärna. Flytta venture-linsen till valbart läge/paket.
Behåll plan-tune vilande tills inställningarna har verkliga läsare.

**Klart när:** samma indata ger samma arbetsartefakter och godkännandestatus oavsett ingång;
redan besvarade frågor och given behörighet återanvänds. Kort arbete får proportionerlig process.

## Skills och agents: mer användbar kunskap, färre parallella kontrakt

### A11 — Bygg om kontextfamiljen kring faktisk kapacitet

**Prioritet:** P2 efter A01. **Beroenden:** A06/08.
**Belägg:** CP-05/16, WF-11, AG-12.

Samla warm/save/restore/budget/cool bakom gemensamma läsare och tydliga lägen. Använd verkligt
rapporterad kapacitet där den finns, annars märk uppskattningen. Arkivering och framtida
läsexkludering frigör inte redan skickad kontext. Ersätt perf-modes oriktiga kapacitetslöfte med ärlig resursrådgivning; bevara dess användbara budget-/diagnostikavsikt och anropsväg.
Behåll det fungerande, ägarmedvetna checkpointstödet.

**Klart när:** okänd kapacitet förblir okänd; återstart läser rätt avgränsade underlag och visar
källor. Rapporter skiljer diskstädning, arbetsmängd, förbrukade tokens och modellens kontext.

### A12 — Låt installerare och livscykelhjälpare äga sina mutationer

**Prioritet:** P2 efter A01. **Beroenden:** A06/07.
**Belägg:** CP-02/04/12/16, RU-06/07/08/11.

Gör scaffold, pack-switch, profile-switch, migration, update och återställning till tunna
anrop till verifierade hjälpare. Håll installationskälla, installerad data och målrepo åtskilda.
Skydda användarägt innehåll, kontrollera felreturer och ange verklig avinstallationsgräns.

**Klart när:** nyinstallation, uppdatering, avbrott och återställning i ett separat konsumentrepo
bevarar lokala anpassningar. Ett lyckat meddelande motsvarar observerad ändring i rätt klient.

### A13 — Samla observation och lärande kring riktiga händelser

**Prioritet:** P2. **Beroenden:** A08/12.
**Belägg:** CP-10/11/16, WF-10, RU-09/10/12; privat synk hanteras i A26.

En producent-/konsumentschema ska styra hook- och reviewloggar. Skilj installerat, registrerat,
observerat och faktiskt verifierat. Gör learn/surface/promote till en gemensam livscykel med
L-NNN-ID och konfigurerad destination. Integrera freeze i skrivvägar eller märk den som
rådgivande. Dra inte slutsatsen ”död” eller ”frisk” från ofullständiga loggar.

**Klart när:** händelser kan läsas tillbaka, en promoverad lektion kan hittas igen och
en fryst yta hanteras korrekt av BUILD/QA på de klienter där skydd utlovas.

### A14 — Reparera designkedjan innan den byggs ut

**Prioritet:** P2. **Beroenden:** A02/06/07/08.
**Belägg:** CP-06/07/15, AG-03/07/10.

Behåll design-dna och accepterad profilprecedens. Använd ett gemensamt designschema genom
brief, spec, renderer och review. Reparera dimensionsnycklar och argumentmappning. Låt
ingen extra animation, CSS-only och ingen shader vara fullvärdiga beslut. Uppdatera
versionsberoende katalogråd från källor och gör befintligt projekts teknikval styrande.

**Klart när:** en statisk sida och en app går från brief till körbar artefakt och verifierad
review; samma profil påverkar båda. Design kräver inte extra bibliotek för att fylla ett schema.

### A15 — Gör dokumentproduktion formatspecifik och verifierbar

**Prioritet:** P2/P3. **Beroenden:** A02/06/07/14 där design delas.
**Belägg:** CP-08/09/18, AG-13.

Dela fakta, källor och narrativ avsikt; använd formatets egna metoder för text, layout och QA.
Ta bort 40-ordsbegränsningen som universell sektionmodell. Rendera dokument/slides, räkna om
kalkylblad och kontrollera redigerbarhet där det utlovas. PDF/XLSX/Visio ska få en konkret väg till fungerande metod och adapter; märk dem
planerade tills den vägen är verifierad. Återanvändbar hantverkskunskap hör i skillen;
kundens innehåll skapas separat.

**Klart när:** ett längre underlag behåller sitt resonemang; varje levererad sida/slide eller
beräkning har rätt sorts kontroll. Saknad renderer ger ett tydligt ofärdigt resultat.

### A16 — Samla browserberoenden bakom verkliga operationer

**Prioritet:** P2. **Beroenden:** A06 och A01 för URL-hantering.
**Belägg:** CP-03/08/13.

Samordna browse, managed-browser, cookies, scrape och make-pdf med preview/design/QA.
Använd klientens faktiska browserstöd när det finns; beskriv öppna/läsa/agera/skärmbild/utskrift
och sessionsägande. Anta inte att en profilkatalog innebär att en browsermotor är installerad.

**Klart när:** en tillåten läsning, en UI-interaktion och en utskrift fungerar i testmiljö,
med tydligt bevis och begränsning. Inloggning och sessioner följer användarens valda yta.

### A17 — Ge varje agent en tydlig, portabel uppgift

**Prioritet:** P2 efter A01/02. **Beroenden:** A06/08/09.
**Belägg:** AG-06/08/09/10/14/15; samtliga 69 inventoryrader.

Neutralisera verktygsnamn och modellval i rollkärnan genom adapterkontrakt; ändra ADR0012
uttryckligen där det behövs. Ange indata, beslut, eget ansvar, leverans och verifiering.
Rätta cirkeln mellan DemoNarratorJunior och DemoNarrativeArc. Pröva sammanslagningar som
SBOMAuditor/DependencyAuditor och LatencyAnalyzer/PerformanceAnalyzer som lägen med bevarat djup.
Behåll verkliga skillnader, exempelvis migrationsplanerare kontra auktoriserad utförare.

**Klart när:** dispatch och mottagande roll är överens; roller kan anropas från en tom session
utan cirkulära förkrav. Reviewroller reparerar inte egna fynd och oberoende sammanhang bevaras.

### A18 — Avgränsa neutral kärna och valbara specialistpaket

**Prioritet:** P2/P3. **Beroenden:** A05/07/17.
**Belägg:** WF-06, AG-04/05, CP-18; per-item-rekommendationer.

Behåll utvecklingscykel, arbetskarta, profilupplösning, verifiering och återstart i kärnan.
Gör frontend/design, dokument, kundkommunikation och regelverk till sammanhållna valbara
förmågepaket när deras beroenden motiverar det. Företagsidentitet/policy är en separat overlay.
En generell säkerhetsgrund förblir del av kärnan.

**Klart när:** ett konsumentrepo kan välja relevanta förmågor utan onödiga roller och prompts;
varje paket anger ansvarig källa, beroenden, mognad, input/output och ett fungerande scenario.
Ingen massradering görs enbart för att minska antalet filer.

### A19 — En katalog, tydliga anrop och rikare utvalda skills

**Prioritet:** P2/P3. **Beroenden:** A06/09/10/17/18.
**Belägg:** CP-17/18, WF-05; alla 126 inventoryrader.

Utgå från befintlig kataloggenerator. Samordna help/router/status/welcome och författande.
Routa med kompakt metadata och läs vald skill först därefter. Bevara bekanta alias vid
sammanslagning. En rik skill ska ha användbara val, ett genomarbetat exempel, fel-/återstartsväg
och verklig utdata; en tunn dispatcher behöver inte bli lång. Planerade utkast ska inte routas
som färdiga leveranser.

**Klart när:** användarens vanligaste avsikter har en tydlig ingång; exempel och negativa fall
visar att instruktionen förbättrar uppgiften. Varje föreslagen sammanslagning har migrationskarta.

### A20 — Bevara ursprung och inför begriplig versionskompatibilitet

**Prioritet:** P2. **Beroenden:** inga för inventering; A07/18 för slutligt kontrakt.
**Belägg:** RT-09/10, [upstreamjämförelse](reviews/upstream.md).

Rätta motstridiga ”original-only”-påståenden. Registrera källa, revision, licens/notiser,
lokala ändringar och vilka metoder som faktiskt återanvänds. Avför det arkiverade förslaget
om synonymbyte och likhetströskel som framtida kvalitetsmetod. Skilj produkt-, packschema-
och kapabilitetsversioner med tydlig uppgradering/migration.

**Klart när:** ett externt bidrag och ett företags-pack kan spåras och kompatibilitetsprövas;
språklig omskrivning används inte som bevis på kvalitet eller rättigheter.

### A21 — Håll Brief Forge och andra vilande funktioner ärligt vilande

**Prioritet:** P1 för farliga recept; P3 för eventuell senare aktivering.
**Beroenden:** A02/06/09/13. **Belägg:** WF-09, RU-05.

Ta bort löften om automatisk exekvering som inte finns. Innan eventuell aktivering: validera
och granska payload före loggning/utdata, minimera auditinnehåll, stöd exakt serialiserat
format och specificera vem som verkligen anropar mottagaren. Följ ADR0008.

**Klart när:** det planerade läget är tydligt; syntetiska otillåtna payloads lämnar varken
fullt auditinnehåll eller lyckat handoff. Aktivering är en egen beslutad och verifierad etapp.

## Integration och bevisat enterprise-värde

### A22 — Bevara och integrera hela Swarming-arbetet med genomförbart klientstöd

**Prioritet:** P2, separat från fel i main. **Beroenden:** A03/08/09.
**Belägg:** RT-11 och [separat swarmgranskning](reviews/swarm.md).

**Uttryckligt användarkrav:** hela grenens värdefulla arbete ska bevaras så långt det är
genomförbart. Följ [alla 76 ändrade filer och klienternas alternativa vägar](swarm-preservation.md).
Swarming är ett avsett resultat, inte en kandidat att ta bort eller skjuta upp på obestämd tid.

Utgå från aktuell main, lös ADR0026-kollisionen, mappa korta deluppgifter till sammanhållna
exekverings-/reviewpaket och skydda koordinatorägda artefakter även från rapportundantag.
Behåll opt-in, isolerade skrivare, rapporter, oberoende review och återställbar samordning.

**Klart när:** den förenade grenen passerar både befintliga enterprise-/hybridfall och swarmfall,
inklusive avbrott, konflikter, scopebrott och saknad native delegation. Varje värdefull
branchändring har en spårbar hemvist; sekventiell/manuell samordning fungerar där parallellitet
saknas. Verkliga förluster eller olösta genomförbarhetskonflikter kräver uttryckligt beslut. Gamla branchskillnader
presenteras inte som regressioner i main.

### A23 — Lägg kvalitetstester där kontrakten möts

**Prioritet:** P1 som kvalitetsspärr; byggs tillsammans med varje berört kort.
**Beroenden:** respektive rättning ovan. **Belägg:** RT-07, WF-13, CP-14, AG-08.

Behåll användbara struktur- och hjälpartester. Lägg verkliga producent/konsumenttester för
profil, arbetskarta, resultat, review och återstart. Komplettera med ett litet urval agentkörda
utfallstester enligt ADR0021 när det beslutas; registrera klient, modell, indata, kostnadskälla
och observerat utfall. En textmatch är en textmatch, inte bevis på beteende.

**Klart när:** tester upptäcker fyndens negativa fall innan rättning och passerar efter rättning.
Ingen ”grön” suite får dölja ej körda klienter, tom testmängd eller saknad mänsklig/modelldom.

### A24 — Bevisa profilens värde med samma uppgift i olika företag

**Prioritet:** P1 för enterprise-löftet, efter fungerande kärna.
**Beroenden:** A02/03/06/07/08/23; relevanta specialistkort.

Kör en liten uppsättning identiska uppgifter med neutral profil och två syntetiska
företagsprofiler: exempelvis snabb intern produktutveckling och ett repo med strikta
ändrings-, data- och granskningskrav. Dokumentera vilka krav, lösningar, arbetspaket,
kontroller och artefakter som ändras och varför. Mät manuella ingripanden, missade krav,
omarbetning, tid och faktisk förbrukning per accepterat resultat.

**Klart när:** profilen ger rätt observerbar skillnad genom hela kedjan; mindre krävande
arbete får proportionerligt mindre process. Rapportera faktiska resultat och osäkerhet,
inte påhittade ROI-procent. Kör samma kärnscenario på prioriterade CLI- och desktop-ytor
innan respektive klient marknadsförs med verifierat stöd.

## Genomförandeordning och val

1. Rätta A01–A04 samt de separata P1-korten A25–A26 och avgränsa A21. Parallellt precisera A05–A08 och testfallen i A23.
2. Leverera en fungerande Universal-kärna med stabil profil, arbetskarta, oberoende review
   och kall återstart. Kör ett första A24-fall innan katalogen breddas.
3. Förbättra A09–A13 och A17 där de behövs av kärnfallet. Konsolidera med alias, små commits
   och ett oberoende reviewpaket per sammanhållet förändringsområde.
4. Leverera design/browser och dokument som egna verifierade vertikaler (A14–A16), sedan
   färdig paket-/katalogindelning A18–A20. A22 hålls som separat integrationsarbete.

**Rekommenderat arkitekturval:** gemensam kärna och tunna, verifierade adapters. En ren
dokumentationsändring går snabbare men lämnar trasiga kontrakt. Ett helt nytt universellt
runtime-/MCP-system kan centralisera mer men ger en stor migration innan något användarvärde
är bevisat. Befintliga hjälpare och kartor gör det mellersta alternativet mest proportionerligt.

Det krävs inget förutbestämt målantal skills eller agents. Rekommendationerna i inventarierna
är utgångspunkt; en sammanslagning godkänns när den bevarar användbar expertis, förenklar valet
och förbättrar eller bibehåller resultatet. Accepterade governance-/arkitekturbeslut ändras
uttryckligen i implementationens beslut, aldrig genom att bara skriva om historien.
