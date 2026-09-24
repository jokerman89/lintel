/* One filtered view is the source for every rendered value and CSV export.
   Local synthetic data only; customer selection is not authorization. */
(() => {
  'use strict';
  const statuses = ['New', 'Investigating', 'Resolved'];
  const severities = ['Critical', 'High', 'Normal'];
  const customers = ['Northwind', 'Contoso'];
  const columns = ['id', 'customer', 'subject', 'status', 'severity', 'createdAt'];
  const byId = id => document.getElementById(id);
  const controls = Object.fromEntries(['customer', 'status', 'severity', 'search', 'start', 'end'].map(id => [id, byId(id)]));
  let sourceError = '';
  let records = [];
  let current = [];
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }
  function key(status) { return status.toLowerCase(); }
  try {
    if (!Array.isArray(window.TICKETS)) throw new Error('Ticket data is unavailable.');
    const seen = new Set();
    records = window.TICKETS.map(ticket => {
      if (!ticket || columns.some(c => typeof ticket[c] !== 'string') || !ticket.id || seen.has(ticket.id) || !customers.includes(ticket.customer) || !statuses.includes(ticket.status) || !severities.includes(ticket.severity) || !Number.isFinite(Date.parse(ticket.createdAt))) {
        throw new Error('Ticket data contains an invalid or duplicate record.');
      }
      seen.add(ticket.id);
      const utc = new Date(ticket.createdAt).toISOString();
      return {...ticket, day: utc.slice(0, 10), utc};
    });
  } catch (error) {
    sourceError = error.message + ' Check tickets.js and reload the page.';
  }
  function validate() {
    if (sourceError) return sourceError;
    for (const id of ['start', 'end']) {
      const input = controls[id];
      const value = input.value;
      const parsed = value ? new Date(value + 'T00:00:00Z') : null;
      if (!input.validity.valid || (value && (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value))) return 'Enter a valid date using a four-digit year.';
    }
    if (controls.start.value && controls.end.value && controls.start.value > controls.end.value) return 'The From date must be on or before the Through date.';
    if (!customers.includes(controls.customer.value)) return 'Select a pilot customer.';
    return '';
  }
  function matches(ticket) {
    const query = controls.search.value.trim().toLowerCase();
    return ticket.customer === controls.customer.value &&
      (!controls.status.value || ticket.status === controls.status.value) &&
      (!controls.severity.value || ticket.severity === controls.severity.value) &&
      (!query || ticket.id.toLowerCase().includes(query) || ticket.subject.toLowerCase().includes(query)) &&
      (!controls.start.value || ticket.day >= controls.start.value) &&
      (!controls.end.value || ticket.day <= controls.end.value);
  }
  function drawTrend(rows) {
    const groups = new Map();
    rows.forEach(ticket => groups.set(ticket.day, (groups.get(ticket.day) || 0) + 1));
    const trend = byId('trend');
    trend.replaceChildren();
    if (!groups.size) { trend.append(element('p', 'No matching ticket arrivals', 'chart-empty')); return; }
    const max = Math.max(...groups.values());
    [...groups].sort(([a], [b]) => a.localeCompare(b)).forEach(([date, count]) => {
      const day = element('div', undefined, 'day');
      day.dataset.date = date; day.dataset.count = count;
      day.setAttribute('aria-label', date + ': ' + count + (count === 1 ? ' ticket' : ' tickets'));
      const space = element('div', undefined, 'bar-space');
      const bar = element('div', undefined, 'bar');
      bar.style.height = (count / max * 102) + 'px';
      bar.append(element('span', count, 'bar-count'));
      space.append(bar);
      const label = element('time', date.slice(5).replace('-', '/'), 'day-label');
      label.dateTime = date; label.title = date + ' UTC';
      day.append(space, label); trend.append(day);
    });
  }
  function drawStatuses(rows) {
    const breakdown = byId('breakdown'); const stack = byId('status-stack');
    breakdown.replaceChildren(); stack.replaceChildren();
    statuses.forEach(status => {
      const count = rows.filter(ticket => ticket.status === status).length;
      const percent = rows.length ? count / rows.length * 100 : 0;
      const segment = element('span', undefined, 'status-segment ' + key(status));
      segment.style.width = percent + '%'; if (count) stack.append(segment);
      const row = element('div', undefined, 'status-row');
      row.dataset.status = status; row.dataset.count = count;
      row.append(element('span', undefined, 'dot ' + key(status)), element('span', status), element('strong', count), element('small', Number(percent.toFixed(1)) + '%'));
      breakdown.append(row);
    });
  }
  function cell(label) {
    const td = element('td'); td.append(element('span', label, 'mobile-label')); return td;
  }
  function drawTickets(rows) {
    const body = byId('ticket-rows'); body.replaceChildren();
    const fragment = document.createDocumentFragment();
    rows.forEach(ticket => {
      const tr = element('tr'); tr.dataset.ticketId = ticket.id;
      const subject = element('td');
      subject.append(element('span', ticket.id, 'ticket-id'), element('span', ticket.subject, 'subject'));
      const status = cell('Status');
      const pill = element('span', undefined, 'status-pill ' + key(ticket.status) + '-pill');
      pill.append(element('span', undefined, 'dot ' + key(ticket.status)), element('span', ticket.status)); status.append(pill);
      const severity = cell('Severity'); severity.append(element('span', ticket.severity, 'severity ' + key(ticket.severity)));
      const created = cell('Created · UTC');
      const time = element('time', ticket.day + ' · ' + ticket.utc.slice(11, 16), 'created'); time.dateTime = ticket.createdAt; created.append(time);
      tr.append(subject, status, severity, created); fragment.append(tr);
    });
    body.append(fragment); byId('empty-state').hidden = rows.length > 0;
  }
  function render() {
    const error = validate();
    byId('filter-error').textContent = error; byId('filter-error').hidden = !error;
    controls.start.setAttribute('aria-invalid', String(Boolean(error && !sourceError)));
    controls.end.setAttribute('aria-invalid', String(Boolean(error && !sourceError)));
    current = error ? [] : records.filter(matches);
    byId('export').disabled = Boolean(error);
    const active = current.filter(ticket => ticket.status !== 'Resolved').length;
    byId('total-count').textContent = current.length;
    byId('active-count').textContent = active;
    byId('resolved-count').textContent = current.length - active;
    byId('result-count').textContent = current.length;
    byId('customer-name').textContent = controls.customer.value;
    byId('view-summary').textContent = error ? 'Correct the error to view tickets' : current.length + ' matching tickets · ' + active + ' active';
    drawTrend(current); drawStatuses(current); drawTickets(current);
  }
  function csvCell(value) {
    let text = String(value);
    if (/^\s*[=+\-@]/u.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"', '""') + '"';
  }
  byId('export').addEventListener('click', () => {
    if (validate()) return;
    const csv = [columns, ...current.map(ticket => columns.map(column => ticket[column]))].map(row => row.map(csvCell).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}));
    const link = element('a'); link.href = url;
    link.download = controls.customer.value.toLowerCase() + '-support-tickets.csv';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  byId('clear').addEventListener('click', () => {
    ['status', 'severity', 'search', 'start', 'end'].forEach(id => { controls[id].value = ''; }); render();
  });
  Object.values(controls).forEach(control => control.addEventListener('input', render));
  render();
})();

