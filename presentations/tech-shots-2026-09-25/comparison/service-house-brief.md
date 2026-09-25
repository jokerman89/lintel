# Service House: the dinner shift

Build a polished, responsive restaurant operations mockup for a manager running a busy
dinner service. It is a local-first web app, not a static landing page. The four work
areas are **Menu**, **Orders**, **Inventory**, and **Reports**. A basket and checkout
are available in Menu. Use original design, typography and CSS; no external services,
accounts, real customer data, paid assets, backend or image downloads are needed.

## Fixed contracts

`fixture.json` is the initial state; amounts are integer cents and displayed in USD
with two decimals. All six dishes, IDs, categories, prices, allergens and stock values
must match. `selectors.json` specifies stable `data-testid` hooks on visible, usable
UI controls. These hooks do not replace accessible names, labels or real interactions.
The implementation technology is your choice; the supplied Node static server is a
working starting point. `npm start` must honor `PORT`, listen on 127.0.0.1, and serve
the app. Keep the server running at completion. No artificial wait or time padding.

## Acceptance requirements

Each requirement is scored independently. All weigh 3 points except K16 and K25,
which weigh 5: **100 possible points**. Tests use fresh browser storage per scenario.

| ID | Required observable behavior |
|---|---|
| K01 | The app loads with a visible Service House heading and no uncaught browser errors. |
| K02 | Four accessible navigation controls switch between Menu, Orders, Inventory and Reports without leaving the app. |
| K03 | Menu initially displays all six fixture dishes with the correct names. |
| K04 | Search is case-insensitive, trims outer whitespace, matches dish names, and clearing restores matching items. |
| K05 | The category select has values `all`, `starters`, `mains`, `drinks` and filters correctly. |
| K06 | The Vegan only checkbox filters out bread and pasta; search, category and vegan filters combine with AND. |
| K07 | Zero-stock pasta is visibly Sold out and its add control is disabled; the other dishes can be added. |
| K08 | Every dish displays its exact fixture price with two decimal places. |
| K09 | Adding a dish creates one basket row; repeated adds increment that row rather than duplicating it. |
| K10 | Basket quantity is an editable integer from 1 to available stock (maximum 20); zero, negative, fractional, nonnumeric and excess values cannot produce an invalid order. Invalid edits leave the last valid quantity and display a visible error. |
| K11 | Removing a basket row removes its contribution; removing the last row shows a meaningful empty basket. |
| K12 | Subtotal is the sum of each price times quantity, without floating-point currency drift. |
| K13 | Applying `KITCHEN10` discounts subtotal by 10%, rounded to the nearest cent. An invalid code shows `discount-error` and clears the discount; applying an empty code clears it without an error. |
| K14 | Tax is 10% of discounted subtotal, rounded to nearest cent; total is discounted subtotal plus tax. Two soups and a lemonade with KITCHEN10 total $21.29 (subtotal $21.50, discount $2.15, tax $1.94). |
| K15 | Checkout rejects an empty basket, a blank/whitespace customer name, and tables outside integer 1-30. It shows an actionable `checkout-error` and creates no ticket. |
| K16 | A valid checkout creates exactly one queued ticket, with sequential ID T001 onward, customer, table, dish quantities and correct total; basket and discount are cleared. |
| K17 | Optional order notes are displayed verbatim as text on the ticket, never interpreted as HTML. Customer names must also be rendered as text. |
| K18 | A queued ticket has Start cooking; clicking it moves to cooking and offers Mark ready. Status is visible and exposed in `data-status`. |
| K19 | Mark ready moves cooking to ready. Ready/cancelled tickets have no enabled advance or cancel action. |
| K20 | Queued or cooking tickets can be cancelled exactly once, remain visible as cancelled, and restore their reserved stock exactly once. |
| K21 | Stock is reserved only on successful checkout, not when adding to the basket. Inventory and Menu stock agree after submission. |
| K22 | An order cannot exceed current stock. Ordering all eight soups makes soup Sold out; no ninth soup can be ordered until restocked/cancelled. |
| K23 | Inventory shows all six stock counts; a labeled restock input per item adds an integer 1-99. Zero, negative, fractional and over-99 amounts show `stock-error` without changing stock. |
| K24 | Each dish exposes its allergens as text, or explicitly None. Vegan status is visible, not color-only. |
| K25 | A reload preserves orders, statuses, stock and basket; a completed checkout is not duplicated. Store client state locally. |
| K26 | Reports show noncancelled order count, cancelled count and revenue from ready tickets only. Cancelled/queued/cooking tickets contribute no revenue. |
| K27 | Export CSV downloads all tickets with header `ticket,customer,table,status,total`; total is decimal dollars without a currency sign. Escape quotes, commas and newlines correctly. |
| K28 | An unmatched menu search and a fresh Orders view show clear empty states, not blank space or an error. |
| K29 | Theme toggle switches `document.documentElement.dataset.theme` between `light` and `dark`, visibly changes colors, and survives reload. |
| K30 | At a 390x844 viewport there is no horizontal document overflow; navigation, basket and checkout remain reachable and usable. |
| K31 | Navigation, search, quantity/checkout/restock inputs and buttons have accessible names; native keyboard focus is visible and controls work without a pointer. |
| K32 | Reset demo requires confirmation through a visible `confirm-reset` button. Cancelling leaves state intact; confirming restores fixture stock, empty orders/basket and zero report values. |

## Control details

Use `menu-{id}` for each menu card and `add-{id}` for its add button.
Use `cart-{id}`, `qty-{id}` (a labeled input), and `remove-{id}` per basket row.
Category and vegan controls are a native select and checkbox. Navigation controls may
be buttons or links. Keep total hooks on elements containing only a formatted amount.
Use `ticket-T001` and so on for ticket containers, with `data-status` on that container.
Ticket action buttons have exactly the accessible names in `selectors.json`.
Stock count hooks contain just the integer. Restock controls add, not replace, stock.
The reset confirmation has a **Cancel** control as well as **Reset demo** confirmation.
Error text can be designed freely but must be visible and useful.

## Definition of done

The app is running, every workflow is implemented, mobile and keyboard use work,
and the results match these requirements. Do not access an external grader or
copy a reference implementation. Report any requirement you could not finish.
This task is deliberately broad; a five-minute baseline is a calibration target,
not an instruction to delay completion.
