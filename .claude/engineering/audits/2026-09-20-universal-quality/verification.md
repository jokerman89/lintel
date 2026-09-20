# Verifiering och begränsningar

Datum 2026-09-20. Baseline main `28061e434be455ca02f135b73244eaf4f73f3a69`.
Isolerad gren `codex/universal-audit-20260920`. Inga produktfixar eller main-ändringar.

## Faktiskt genomförda kontroller

- Alla 771 spårade filer inventerade, totalt cirka 95 430 textrader. Full lästäckning hävdas
  för de 126 skillinstruktionerna och 69 agentinstruktionerna, inte varje historisk fil/data-rad.
- Exakt inventariematchning mot `skills/*/SKILL.md` och `agents/**/*.md`: inga luckor eller
  dubbletter. Radantal matchar 21 524 respektive 7 798. Alla tre huvudgranskningars lokala
  evidenssökvägar och angivna radnummer validerade mot baseline.
- Syntetiska profil-, state- och routingkontroller körda i ignorerad separat testdata under
  audit-worktree. Inga verkliga företagsprofiler eller privata auditloggar användes.
- Två icke-skrivande designkontroller utförda av capabilitygranskaren: producerade och lästa
  reviewnycklar har tomt snitt; en statisk validator rapporterar inga fel/varningar för
  test-HTML med `#aaa` på `#fff`. Det senare visar en täckningsgräns, inte i sig ett löfte
  från validatorn att full kontrastanalys implementerats.
- Aktuella klientpåståenden kontrollerade mot officiella källor, dokumenterade i
  [klientunderlaget](client-sources.md). Upstreamjämförelsen använder pinnade revisioner
  och kör inga av upstreamprojektens installationsskript.

## Reproducerade utfall från koordinatorn

Körningen använde den granskade baselinens Bash-hjälpare och syntetiska kataloger.
Sessions-ID:na nedan är processberoende exempel från körningen.

```text
PACK_SESSION_WITHOUT_HOST_ID
loaded=company mode=hard session=1252-1266
loaded=other mode=advisory session=1252-1321
CYCLE_MARKER_ORDER
phase: CYCLE
ROUTER_READ_ONLY_INTENT
request=review the fix without changing code intent=fix workflow=/li:cycle --mode hotfix confidence=high
request=research deployment options only intent=deploy workflow=/li:cycle --from SHIP confidence=high
request=review the release plan intent=ship workflow=/li:cycle --from SHIP confidence=high
NO_VALID_PACK_FALLBACK
resolved_mode=advisory exit=0
```

Testförutsättningar och tolkning:

1. Två nya Bash-processer utan `LINTEL_SESSION_ID`/`CLAUDE_SESSION_ID`, aktiv packpekare
   ändrad mellan anrop. Varje process laddar då sin egen profil. Resolverns dokumentation
   ålägger klienten att ge ett stabilt ID; fyndet är bristande adapterkoppling.
2. SENSE och SCOPE loggades före CYCLE-markören enligt skillens beskrivna ordning.
   `state_cycle_segment` visar då enbart CYCLE. Detta är ett mekaniskt ordningstest,
   inte en full körning av ett LLM-styrt utvecklingsflöde.
3. Routern kördes med de tre strängarna ovan. Resultaten är rekommendationer; testen visar
   felklassificerad avsikt, inte att något faktiskt byggdes eller driftsattes utan lov.
4. `_default/pack.yaml` innehöll ogiltig syntetisk data. Resolvern skrev diagnostik men
   returnerade `advisory` och framgång. Nödfallbacken är dokumenterad och måste ändras
   uttryckligen om obligatorisk företagspolicy ska förbli ett olöst fel.

Den körda reproduktionskoden finns i [probes.sh](probes.sh). Den är granskningsunderlag,
inte en ny produkttestsvit eller ett installationsskript. Kör endast från den avsedda
audit-baselinen; skriptet skriver enbart syntetiska fixtures under `.claude/runtime/universal-probes`.

## Övriga reviewbevis

- Runtimegranskaren redovisar egen lästäckning, konkreta helper-/hook-fynd, statiska
  käll-/kontrollflödesbelägg samt föreslagna framtida reproduktionsfixtures och ej utförda operationer i [runtime.json](reviews/runtime.json).
- Den ointegrerade swarmgrenen granskas med separata in-memory-fixtures och tydlig
  branchreferens i [swarm.md](reviews/swarm.md). Resultaten gäller inte main-koden.
- Varje skill-/agentfynd redovisar om det är statisk analys, ett sökbaserat frånvaropåstående,
  en aritmetisk motexempelanalys, ett körbart prov eller extern källverifiering.

## Inte genomfört

Ingen full testsuite kördes för denna rapport. Ingen modellbenchmark, betald agentevaluering,
komplett klientinstallationsmatris, verklig document-rendering eller enterpriseproduktionstest
genomfördes. Tidigare 109 lokala tester och historisk CI gäller tidigare leverans och används
inte som färska kvalitetsbevis här. Kvalitetsklasserna är granskningsbedömningar, inte statistik
över modellers resultat. Rapporterna pekar ut vad implementationens tester behöver bevisa.

## Slutkontroll

Den separata [oberoende slutgranskningen](reviews/independent-synthesis.md) är genomförd.
Koordinatorn har rättat prioriteringen av kodkälla/privat synkdestination, preciseringen av
statiska belägg kontra framtida fixtures, designpoängens beskrivning, två lärdomsrubriker
och ett mindre formateringsfel. Bevarandeprincipen och hybridbeslutet är uttryckligen kvar.

JSON- och inventarievalidering, lokala rapportlänkar, radreferenser och `git diff --check`
har kontrollerats. Rapportkatalogen innehåller fullständig skill-/agentförteckning och en
bevarandekarta för samtliga 76 ändrade Swarming-filer. Ursprungligt checkout är fortfarande
rent. Slutgranskningens godkännande avser granskningsunderlaget, inte att produktfynden är fixade.
