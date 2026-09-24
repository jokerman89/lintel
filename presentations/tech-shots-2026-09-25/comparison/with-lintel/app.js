/*
 * component: support-dashboard
 * intent: spec.md
 * constraints: synthetic local pilot; no authentication or tenant isolation
 * last_intent_review: 2026-09-20
 */
(() => {
  'use strict';
  const statuses = ['New', 'Investigating', 'Resolved'];
  const severities = ['Critical', 'High', 'Normal'];
  const customers = ['Northwind', 'Contoso'];
  const columns = ['id', 'customer', 'subject', 'status', 'severity', 'createdAt'];
  const colors = { New: '#8b76d7', Investigating: '#c79a43', Resolved: '#64a78c' };
  const statusClass = { New: 'new', Investigating: 'investigating', Resolved: 'resolved' };
  const byId = id => document.getElementById(id);
  const fields = Object.fromEntries(['customer', 'status', 'severity', 'search', 'start', 'end'].map(id => [id, byId(id)]));
  const formatDay = day => new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', timeZone: 'UTC' }).format(new Date(day));
  let tickets = [];
  let filtered = [];
  let loadError = '';

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }

  // Validate the entire source before showing totals, rather than silently losing records.
  try {
    if (!Array.isArray(window.TICKETS)) throw new Error('Ticket data is unavailable.');
    const ids = new Set();
    tickets = window.TICKETS.map(ticket => {
      if (!ticket || !columns.every(key => typeof ticket[key] === 'string') || !ticket.id || ids.has(ticket.id) || !customers.includes(ticket.customer) || !statuses.includes(ticket.status) || !severities.includes(ticket.severity) || !Number.isFinite(Date.parse(ticket.createdAt))) {
        throw new Error('Ticket data contains an invalid or duplicate record.');
      }
      ids.add(ticket.id);
      const timestamp = Date.parse(ticket.createdAt);
      return { ...ticket, timestamp, utcDay: new Date(timestamp).toISOString().slice(0, 10) };
    });
  } catch (error) {
    loadError = `${error.message} Restore tickets.js and reload to continue.`;
  }

  function currentView() {
    const values = Object.fromEntries(Object.entries(fields).map(([key, input]) => [key, input.value]));
    let error = loadError;
    if (!error && (!fields.start.validity.valid || !fields.end.validity.valid)) error = 'Enter valid start and end dates, or leave them blank.';
    if (!error && values.start && values.end && values.start > values.end) error = 'The start date must be on or before the end date. Adjust the dates or clear filters.';
    if (!error && (!customers.includes(values.customer) || (values.status && !statuses.includes(values.status)) || (values.severity && !severities.includes(values.severity)))) error = 'Choose a valid customer, status and severity.';
    const query = values.search.trim().toLowerCase();
    const rows = error ? [] : tickets.filter(ticket =>
      ticket.customer === values.customer &&
      (!values.status || ticket.status === values.status) &&
      (!values.severity || ticket.severity === values.severity) &&
      (!query || `${ticket.id} ${ticket.subject}`.toLowerCase().includes(query)) &&
      (!values.start || ticket.utcDay >= values.start) &&
      (!values.end || ticket.utcDay <= values.end)
    ).sort((a, b) => b.timestamp - a.timestamp || a.id.localeCompare(b.id));
    return { rows, values, error };
  }

  function renderTrend(rows) {
    const days = new Map();
    rows.forEach(ticket => days.set(ticket.utcDay, (days.get(ticket.utcDay) || 0) + 1));
    const trend = byId('trend');
    trend.replaceChildren();
    if (!days.size) {
      trend.append(element('p', 'No matching ticket arrivals', 'trend-empty'));
      return;
    }
    const maximum = Math.max(...days.values());
    [...days.entries()].sort(([a], [b]) => a.localeCompare(b)).forEach(([day, count]) => {
      const group = element('div', undefined, 'day');
      group.dataset.date = day;
      group.dataset.count = count;
      group.setAttribute('role', 'listitem');
      group.setAttribute('aria-label', `${day}: ${count} ${count === 1 ? 'ticket' : 'tickets'}`);
      const bar = element('div', undefined, 'day-bar');
      bar.style.height = `${count / maximum * 96}px`;
      bar.setAttribute('aria-hidden', 'true');
      group.append(element('span', count, 'day-count'), bar, element('span', formatDay(day), 'day-date'));
      trend.append(group);
    });
  }

  function renderBreakdown(rows) {
    const breakdown = byId('breakdown');
    breakdown.replaceChildren();
    statuses.forEach(status => {
      const count = rows.filter(ticket => ticket.status === status).length;
      const row = element('div', undefined, 'status-row');
      row.dataset.status = status;
      row.dataset.count = count;
      row.style.setProperty('--status-color', colors[status]);
      row.setAttribute('role', 'listitem');
      const name = element('span', undefined, 'status-name');
      const dot = element('i', undefined, 'status-dot');
      dot.setAttribute('aria-hidden', 'true');
      name.append(dot, document.createTextNode(status));
      const track = element('div', undefined, 'status-track');
      track.setAttribute('aria-hidden', 'true');
      const fill = element('div', undefined, 'status-fill');
      fill.style.width = `${rows.length ? count / rows.length * 100 : 0}%`;
      track.append(fill);
      row.append(name, element('span', count, 'status-number'), track);
      breakdown.append(row);
    });
  }

  function renderTickets(rows) {
    const body = byId('ticket-rows');
    body.replaceChildren();
    rows.forEach(ticket => {
      const row = element('tr');
      row.dataset.ticketId = ticket.id;
      const status = element('td');
      status.append(element('span', ticket.status, `badge ${statusClass[ticket.status]}`));
      const severity = element('td');
      severity.append(element('span', ticket.severity, `severity ${ticket.severity.toLowerCase()}`));
      const created = element('td', `${formatDay(ticket.utcDay)} ${ticket.utcDay.slice(0, 4)}`, 'created');
      created.title = `Original timestamp: ${ticket.createdAt}`;
      row.append(element('td', ticket.id), element('td', ticket.subject, 'subject'), status, severity, created);
      body.append(row);
    });
    byId('empty-state').hidden = rows.length !== 0;
    byId('result-count').textContent = rows.length;
  }

  function render() {
    const { rows, values, error } = currentView();
    filtered = rows;
    byId('filter-error').textContent = error;
    byId('filter-error').hidden = !error;
    byId('export').disabled = Boolean(error);
    fields.start.setAttribute('aria-invalid', String(Boolean(error && !loadError)));
    fields.end.setAttribute('aria-invalid', String(Boolean(error && !loadError)));
    byId('total-count').textContent = rows.length;
    byId('active-count').textContent = rows.filter(ticket => ticket.status === 'New' || ticket.status === 'Investigating').length;
    byId('critical-count').textContent = rows.filter(ticket => ticket.severity === 'Critical').length;
    byId('resolved-count').textContent = rows.filter(ticket => ticket.status === 'Resolved').length;
    const dateRange = values.start || values.end ? `${values.start || 'Beginning'} → ${values.end || 'Present / future'} · UTC` : 'All creation dates';
    byId('view-summary').textContent = error ? 'View unavailable — correct the issue below your filters.' : `${values.customer} · ${rows.length} matching ${rows.length === 1 ? 'ticket' : 'tickets'} · ${dateRange}`;
    renderTrend(rows);
    renderBreakdown(rows);
    renderTickets(rows);
  }

  // Quoting handles CSV syntax; the apostrophe separately neutralizes spreadsheet formulas.
  function csvCell(value) {
    let safe = String(value);
    if (/^\s*[=+\-@]/u.test(safe)) safe = `'${safe}`;
    return `"${safe.replace(/"/g, '""')}"`;
  }

  byId('export').addEventListener('click', () => {
    const lines = [columns, ...filtered.map(ticket => columns.map(column => ticket[column]))];
    const csv = lines.map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n';
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = element('a');
    link.href = url;
    link.download = `${fields.customer.value.toLowerCase()}-tickets.csv`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    byId('export-message').textContent = `Exported ${filtered.length} tickets for ${fields.customer.value}.`;
  });
  Object.values(fields).forEach(input => {
    input.addEventListener('input', render);
    input.addEventListener('change', render);
  });
  byId('clear').addEventListener('click', () => {
    ['status', 'severity', 'search', 'start', 'end'].forEach(key => { fields[key].value = ''; });
    render();
  });
  render();
})();
