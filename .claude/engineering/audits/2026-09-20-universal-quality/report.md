# Lintel: helhetsgranskning och väg till Universal

2026-09-20 · main `28061e434be455ca02f135b73244eaf4f73f3a69` · endast granskning.

## Bedömning

Lintel har en användbar grund: en sammanhängande utvecklingscykel, företagsprofiler,
explicita arbetskartor, korta verifierbara deluppgifter, arbetspaket, oberoende review,
bestående handoffs och återanvändbar specialistkunskap. Den grunden ska bevaras.

Problemet är att delarna inte genomgående delar samma kontrakt. Publika ingångar har blivit
Copilot-orienterade, många instruktioner förutsätter Claude-verktyg och vissa funktioner
beskrivs som färdiga fast den verkliga integrationsvägen saknas. Lintel kan därför ställa
många frågor och producera många dokument utan att säkert bära samma krav, profil och
verifieringsbevis genom hela uppgiften.

**Rekommendationen är en Universal-kärna med tunna, verifierade klientadapters, följd av
riktade rättningar och fördjupning av befintliga förmågor.** Ett helt nytt runtime-system
behövs inte för att börja lösa problemen. Copilot-stödet ska fortsätta vara värdefullt,
liksom Claude-stödet; produktens identitet och gemensamma arbetsmetod ska vara Universal.

Användaren har uttryckligen förtydligat att värde ska bevaras. Ingen funktion har tagits bort
under granskningen. Sammanslagning betyder ett gemensamt ansvar med bibehållna användningsfall
och djup. Valbara paket ska vara tillgängliga, begripliga och underhållna. En ofärdig men
värdefull förmåga ska få en utvecklingsväg. Ingen borttagning är beslutad.

## Vad som granskats

| Område | Täckning och metod |
|---|---|
| Hela main-trädet | 771 spårade filer och cirka 95 430 textrader inventerade. Inventering betyder inte att varje historisk rad eller datasetpost har genomlästs. |
| Skills | Samtliga 126 kanoniska SKILL.md, 21 524 rader, fullständigt lästa. Varje skill har en egen bedömning och rekommendation. |
| Agents | Samtliga 69 rollinstruktioner, 7 798 rader, fullständigt lästa. Dispatch, mandat, bevis, exempel och överlapp jämförda. |
| Gemensam logik | Fördjupad granskning av packs, tillstånd, routing, arbetskartor, reviews, hjälpare, installerare, hooks, schema- och testkontrakt. Runtime-rapporten anger exakt lästäckning. |
| Dokumentation | Aktuell arkitektur, entryfiler, publika start-/enterprise-/klientguider, relevanta koncept, beslut, precedence och CI-/testbeskrivningar. Historiska planer och arkiv användes selektivt för status/proveniens. |
| Andra harnesses | Avgränsad semantisk jämförelse av pinnade versioner av gstack, Superpowers, GSD Core och ECC. Ingen fullständig revision av deras repo eller bevisad historisk regression från okänd importversion. |
| Klienter | Daterad kontroll mot officiella källor för stora CLI-, desktop-, IDE- och cloud-ytor; ingen ny komplett installations-/körmatris. |
| Swarm | Separat granskning av ännu ointegrerade `codex/swarming-work` på `275a354`, inte sammanblandad med main. |

Tre oberoende granskningsspår läste skills/agents, följt av avgränsade spår för runtime,
upstreams och swarm. Koordinatorn läste gemensamma kontrakt och körde syntetiska kontroller.
Slutunderlaget har granskats separat och preciserats; resultat dokumenteras i [verifieringsunderlaget](verification.md).

## Viktigaste fynden och deras följd

1. **Universal är inte konsekvent genomfört.** README/startguide sätter Copilot främst,
   medan DEFINE, reviewer- och browserflöden fortfarande använder specifika klientnamn
   och verktyg som krav. En fungerande klient kan därför nekas en förmåga den har.
   Adaptern måste skiljas från den gemensamma metoden. RT-01/02, WF-03, CP-03, AG-06.
2. **Reviewbevis kan avse annat innehåll.** Commitbaserad diff missar valda okommittade
   ändringar; SHIP saknar ett genomgående krav på samma granskade innehåll. Äldre testpass
   återanvänds också på tidsgrund. Det behövs en beviskedja från exakt arbete till leverans.
   WF-02, AG-15 och runtimegranskningen.
3. **Obligatoriska fel kan döljas bakom grönt.** Compliance använder felantal, design
   använder poängtrösklar och flera kontroller saknar tydligt ”ej verifierat”. Ett obligatoriskt
   underkänt krav kan inte kompenseras av andra poäng. WF-01/08, AG-03/04, CP-08.
4. **Profilens effekt är inte stabil genom alla steg.** Utan ett stabilt sessions-ID kan
   två verktygsskal ladda olika företagsprofiler. Fel i obligatorisk policy kan falla tillbaka
   till neutral/advisory; detta är delvis dokumenterat och behöver ett medvetet nytt
   enterprisekontrakt. Design- och engineeringläsare använder dessutom olika källor.
   RT-03/04, WF-06, CP-07/12.
5. **Arbetet byter ibland karta mitt i flödet.** ANALYZE/CAPTURE/budgetering följer inte
   alltid samma valda spec-/task-källor som PLAN/BUILD/REVIEW. CYCLE:s beskrivna ordning
   riskerar dubbla startfaser och bortfiltrerad historik. RT-06, WF-04/05/11.
6. **Vissa instruktioner är konkret osäkra eller overksamma.** Kontextladdning använder
   `eval`, safe-install beskriver opålitlig snapshotstädning och utredarroller har otillräckligt
   avgränsad återställning. Valbara hooks/vaultverktyg kan ladda kod från målrepot,
   och privat synk kan använda gammal remote trots nytt val eller forget. Dessa två
   avgränsade risker har egna högprioriterade kort, A25–A26. Andra lokala markörer sägs styra klienter/modellkapacitet utan
   verklig konsument. CP-01/02/04/05, AG-01/12, RU-02/03.
7. **Specialistdjupet är ojämnt.** Design-dna har faktisk återanvändbar metod och data;
   andra förmågor lägger större vikt vid processform än vid svåra val, praktiskt genomförande
   och verifierad artefakt. Dokumentdelar är uttryckligen planerade och ska bedömas som det.
   CP-06/08/09/18, WF-07, AG-08/13.
8. **Testerna bevisar mindre än vissa produktpåståenden.** Många formtester är användbara
   men mäter strängar, metadata och form. De bevisar inte att en modell fullföljer arbetet,
   att en företagsprofil skapar värde eller att alla desktopklienter fungerar. RT-07, WF-13,
   CP-14. Det finns också verkliga beteendetester att bygga vidare på.

Detaljer, exakta rader, verifiering och begränsningar finns i [workflow](reviews/workflow.json),
[capabilities](reviews/capabilities.json), [agents](reviews/agents.json),
[runtime](reviews/runtime.json) och [koordinatorns fynd](reviews/coordinator.md).
Fynd kan överlappa; deras antal summeras därför inte till ett påstått antal oberoende fel.

## Vilka skills och agents behöver vad?

| Bedömning | Skills | Agents |
|---|---:|---:|
| Stark metod/kontrakt | 18 | 23 |
| Blandad kvalitet | 71 | 40 |
| Svag i nuvarande instruktion/kontrakt | 32 | 6 |
| Uttryckligen planerad förmåga | 5 | 0 |

Detta är kvalitativa granskningsbedömningar, inte uppmätta framgångsprocent eller en lista
över funktioner att kasta. En stark roll kan behöva förbättrad adapter eller ett gemensamt
resultatformat. En svag skill kan ha ett mycket värdefullt syfte som behöver byggas färdigt.

- **Behåll och stärk:** hybridplanering och arbetskartor; oberoende granskning; bounded
  research/utforskning; checkpoint/återstart; kataloggenerering; design-dna; domänkunskap
  i arkitektur, data, säkerhet, drift och testning.
- **Fördjupa:** DEFINE:s situationsanpassade frågor, specialistmodulernas konkreta beslut,
  review/QA:s verkliga bevis, formatkunskap och återställningsvägar.
- **Samordna med bevarad funktion:** alternativa planeringsingångar, kontextfamiljen,
  diagnostik, lektionsflödet, browserfamiljen och vissa överlappande agentroller.
- **Färdigställ avsiktligt:** dokumentrenderers, frågepreferenser och Brief Forge har
  identifierade vägar framåt; deras ofärdiga mekanik ska inte räknas som verifierat stöd.

De två ursprungliga ”retire”-kandidaterna betyder inte att användarvärdet ska försvinna:
`perf-mode` bör få ärlig resurs-/budgetrådgivning i stället för en markör som påstås höja
modellkapaciteten; `v4-migrate` bör behålla sin historiska återställningsväg under rätt
versionsstyrd ingång. Fullständig ersättning och fortsatt åtkomst ska visas före en förändring.

Varje namn, bedömning, motivering och belägg finns i [alla 126 skills](skills-inventory.md)
och [alla 69 agents](agents-inventory.md). Dessa listor är mer användbara för implementation
än en godtycklig målsiffra för hur många filer som ska bli kvar.

## Den röda tråden

**Användarens avsikt → effektiv företags-/projektprofil → krav och accepterade beslut →
vald arbetskarta → korta deluppgifter i sammanhållna arbetspaket → rätt specialistarbete →
oberoende review av exakt resultat → verifierad leverans → lärdom och återstart.**

Varje övergång ska veta vilket arbete den gäller, vilka krav och begränsningar som följer med,
vad som faktiskt observerats och vem som ansvarar för nästa steg. Det kräver ett fåtal
gemensamma kontrakt, inte fler fristående processlager. Skillens roll är att bidra med
användbar metod och beslut; hjälparens roll är att göra mekaniken tillförlitlig.

Behåll ADR0026: korta 2–5-minutersdeluppgifter gör arbete kontrollerbart, medan paket ger
effektiv sammanhållen exekvering och granskning. Starta inte en ny agent eller samma
godkännandeceremoni för varje liten deluppgift. Bevara oberoende review för substantiella ändringar.

En profil skapar enterprise-värde när den ändrar ett relevant beslut: exempelvis tillåtna
beroenden, datagränser, driftsmodell, riskkrav, granskningsbevis eller faktisk artefaktidentitet.
Den ska också kunna minska onödig process för låg-risk-arbete. Att bara ändra tonfall eller
lägga till fler dokument är inte tillräckligt. A24 föreslår jämförbara syntetiska profilfall
och mätning per accepterat resultat.

## Lärdomar från andra harnesses

Jämförelsen gäller metoder, kontrakt och användbara exempel. Det går inte att fastslå exakt
vad en historisk omskrivning tappat utan en känd importrevision. Dagens pinnade upstreams
ger däremot konkreta mönster att pröva: gstack för observerbara QA-bevis och djupa checklistor,
Superpowers för tydliga plan-/reviewpaket, GSD för återstart och skillnad mellan utfört och
verifierat, samt ECC för verkliga host-/hookkontrakt. Detta är överföringsförslag, inte bevis
på att ett helt upstreamflöde är bättre för Lintel.

Behåll Lintels styrkor: neutral företagsprofil, deklarerade behörighetsgränser, Spec Kit-mappning,
auktoritativa repoartefakter och hybridpaket. Kopiera inte startupantaganden, klientbundna
processer eller all upstream-ceremoni. Se [jämförelsen med källrevisioner](reviews/upstream.md).

## Prioritering och leveransgräns

[Åtgärdslistan](action-plan.md) innehåller 26 avgränsade resultat med beroenden och kriterier
för att vara klara. Börja med osäkra recept, falska klartecken, reviewidentitet och bekräftade
runtimefel, inklusive kodkälla och privat synkdestination. Leverera därefter en sammanhängande Universal-kärna med fungerande profilvärde
och återstart. Bygg ut design, browser och dokument som verifierade kedjor utan att tappa
befintlig specialistkunskap.

Hela Swarming-grenens arbete ska bevaras så långt det är genomförbart, enligt användarens
uttryckliga förtydligande. Även klienter utan parallella agents ska få fungerande stöd för
uppdelning, briefs, status, validering och överlämning. [Filvis bevarandeplan](swarm-preservation.md)
omfattar samtliga 76 ändrade filer. Grenen kräver egen reconciliation med aktuell
main och hybridbeslutet. Dess brister är inte fel som redan finns i main. Se
[swarmgranskningen](reviews/swarm.md).

Granskningen ändrar endast rapporter och kontinuitetsanteckningar i en isolerad arbetsgren.
Inga produktfunktioner, privata profiler, klientinstallationer eller main har ändrats.
Ingen färsk full testsuite, betald modellbenchmark eller komplett klientmatris har körts;
tidigare CI-resultat räknas inte som bevis för dessa rekommendationer.
