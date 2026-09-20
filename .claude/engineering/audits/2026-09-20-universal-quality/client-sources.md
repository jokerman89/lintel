# Universal: klienter, stöd och verifiering

Kontrollerat 2026-09-20 mot officiell dokumentation och Lintel main `28061e4`.
Detta är ett underlag för stödmodellen, inte ett intyg om genomförda installationer.
Leverantörens funktion, Lintels adapter och ett faktiskt verifierat scenario är tre olika saker.

| Familj och ytor som måste särskiljas | Officiellt underlag | Konsekvens för Lintel |
|---|---|---|
| Claude Code CLI och Claude Code i desktop | [Desktop](https://code.claude.com/docs/en/desktop) delar motor och mycket konfiguration med CLI, men gränssnitt och vissa integrationsvägar skiljer sig. [Subagents](https://code.claude.com/docs/en/sub-agents) har egna verktygs- och minneskontrakt. | Återanvänd befintligt stöd, verifiera respektive yta. Claude-namn på verktyg hör hemma i adaptern. |
| Codex CLI, desktop-app och IDE | [Skills](https://learn.chatgpt.com/docs/build-skills) använder progressiv laddning; [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) är en separat konfigurerad funktion. | Befintligt plugin och faktisk delegation i denna session är användbar grund, men bevisar inte att alla Lintel-roller installeras och körs korrekt i alla ytor. Skillkatalogens storlek behöver hållas hanterbar. |
| GitHub Copilot CLI, desktop-app, VS Code och cloud agent | [Desktop-appen](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app) bygger på CLI och har separata organisationspolicyer. [Anpassning](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app) omfattar skills, plugins och agentval. [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) beskriver skillformatet. | Behåll det portabla Copilot-kitet som adapter. Lägg till appen uttryckligen. Installerat kit, tillåtna funktioner och verifierat arbetsflöde ska redovisas separat. |
| Cursor CLI, editor/desktop och cloud | [Subagents](https://prod.cursor.com/docs/subagents) finns på dessa ytor med skilda exekveringsmiljöer. | Ersätt antagandet att sekventiell rollspelning är enda väg. Kontrollera faktisk delegation och isolering; påstå inte oberoende review när den saknas. |
| Gemini CLI | [Subagents](https://geminicli.com/docs/core/subagents/) och [extensionformat](https://geminicli.com/docs/extensions/reference/) beskriver native skills och agentstöd; mognadsstatus kan skilja mellan vägar. | Den nuvarande manuella/noll-delegationsbeskrivningen behöver omprövas mot version och faktiskt installerad adapter. |
| Google Antigravity CLI, IDE och separat desktop-app | [Översikt](https://www.antigravity.google/docs/overview) skiljer ytorna; [skills](https://www.antigravity.google/docs/skills?tab=ide) stöds över dem. | En egen stödpost, inte ett antagande att Gemini CLI-installationen täcker alla Google-ytor. |
| OpenCode terminal, IDE och desktop | [Produktytor](https://opencode.ai/en/), [skills](https://opencode.ai/docs/skills) och [agents](https://opencode.ai/docs/agents/) beskriver native förmågor. | Befintligt instruktionstillägg är inte full adaptertäckning. Verifiera upptäckt, delegation, frågor, verktyg och återstart separat. |
| Factory Droid CLI, Factory App och webb/cloud | [Produktytor](https://docs.factory.ai/) omfattar en desktop-app. [Plugins](https://docs.factory.ai/harness/plugins) och [subagents](https://docs.factory.ai/harness/subagents) har dokumenterade kontrakt och begränsningar. | Ersätt generellt ”inga subagents” med versions- och adapterbaserad information. Kontrollera bland annat vilka verktyg underagenter får använda. |
| Kiro CLI, desktop-IDE och webb | [Skills](https://kiro.dev/docs/skills/) skiljer projekt-/global tillgänglighet och argumentexpansion mellan ytor. [Subagents](https://kiro.dev/docs/custom-agents/subagents/) skiljer egna roller från inbyggda. | Lägg till en egen adapterpost. Delad motor betyder inte samma discovery, behörighet eller subagentfunktion på alla ytor. Befintliga specifikationer ska behålla sin auktoritet. |
| Windsurf/Cascade, Devin Desktop/Local och Devin CLI | Den tidigare Windsurf-skillguiden omdirigerar till [Cascade skills i Devin Desktop](https://docs.devin.ai/desktop/cascade/skills), som uttryckligen skiljer Cascades discovery från Devin Local/CLI; [CLI-skillkontraktet](https://docs.devin.ai/cli/extensibility/skills/overview) beskriver den senare vägen. | Inventera faktisk agentmotor och yta, inklusive olika anropssätt. Gör inte ett generellt stödantagande utifrån gammalt produktnamn. |
| JetBrains Junie CLI och Junie i IDE | [Agent skills](https://junie.jetbrains.com/docs/agent-skills.html) beskriver skills på båda ytorna samt konfigurerad upptäckt/aktivering. | En egen adapter-/verifieringspost; inga Lintel-körningar på Junie har utförts i denna granskning. |
| Övriga klienter, inklusive befintliga Cline/Continue/Aider-poster | Ingen ny fullständig klientcertifiering genomfördes i denna granskning. | Behåll en ärlig portabel grundväg; inventera klienterna individuellt när stöd görs till ett produktlöfte. En samlingsrad får inte antyda likvärdig förmåga. |

## Rekommenderat kontrakt

Behåll en gemensam arbetsmetod och tunna adapters. För varje klient/yta behöver katalogen
ange upptäckt och anrop av skills, instruktioner och roller; fil/shell/browser-operationer;
frågor och tillstånd; delegation och isolering; minne/återstart; samt verklig hook- och
policyintegration. Dessa egenskaper är oberoende och bör inte döljas i en enda ”full/manual”-etikett.

Varje stödpost ska ha klientversion, Lintel-version, datum, testscenario, observerat resultat
och kvarvarande begränsning. Funktioner upptäckta i den aktuella sessionen väger tyngre än
en gammal hårdkodad produktlista. Att ett verktyg finns betyder fortfarande inte att en
viss operation är tillåten.

Verifiera först ett litet gemensamt scenario: starta i ett nytt konsumentrepo, välj en syntetisk
företagsprofil, planera med korta deluppgifter och sammanhållna arbetspaket, bygg inom given
behörighet, granska rätt innehåll oberoende och återuppta från samma arbetskarta. Lägg sedan
till negativa fall för saknat verktyg, policyfel, ändrat innehåll och avbruten session.

Universal betyder att samma avsikt, krav och bevis följer arbetet. Det innebär inte identiska
hookar, säkerhetspolicyer eller bakgrundsprocesser i alla produkter. Obligatoriska
organisationskontroller måste fortsatt vara separat konfigurerade och verifierade i plattform/CI.

## Avgränsning

Officiella sidor ovan lästes under granskningen. Inga nya klienter installerades, inga privata
konton eller profiler öppnades och ingen full klientmatris kördes. Leverantörsuppgifter är
daterad källverifiering; föreslagen Lintel-täckning är en rekommendation som behöver testas.
