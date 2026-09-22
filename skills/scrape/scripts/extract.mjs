// component: browser-selector-extraction
// implements: ADR-0028
// intent: .claude/plans/universal-implementation/packages/P11.md
// constraints: parsed selector data and owned browser reads; no network, YAML or code evaluation
// last_intent_review: 2026-09-22
import { isDeepStrictEqual } from 'node:util';

export function validateSchema(schema) {
  if (!schema || !Array.isArray(schema.fields) || !schema.fields.length || Object.keys(schema).some(x => x !== 'fields')) {
    throw new Error('Schema needs a nonempty fields list');
  }
  const names = new Set();
  return schema.fields.map(field => {
    if (!field || typeof field.name !== 'string' || !field.name.trim() || names.has(field.name)
      || typeof field.selector !== 'string' || !field.selector.trim()
      || (field.multi !== undefined && typeof field.multi !== 'boolean')
      || (field.transform !== undefined && !['trim', 'text', 'number_extract'].includes(field.transform))
      || Object.keys(field).some(x => !['name', 'selector', 'multi', 'transform'].includes(x))) {
      throw new Error('Invalid or duplicate field; require name, selector, boolean multi and a known transform');
    }
    names.add(field.name);
    return { ...field, transform: field.transform ?? 'trim', multi: field.multi ?? false };
  });
}

function transform(text, kind) {
  if (kind === 'text') return text;
  if (kind === 'trim') return text.trim();
  const numbers = text.match(/[+-]?\d+(?:\.\d+)?/g);
  if (numbers?.length !== 1 || /\d[,\s]\d/.test(text)) throw new Error('Ambiguous numeric field; specify a locale-aware method instead');
  const value = Number(numbers[0]);
  if (!Number.isFinite(value)) throw new Error('Numeric field is not finite');
  return value;
}

export async function extractPage(browser, schema) {
  const fields = validateSchema(schema);
  const result = { url: null, fields: {}, errors: [], ok: false };
  for (const field of fields) {
    const state = await browser.read(field.selector);
    if (result.url !== null && result.url !== state.url) throw new Error('Page changed during extraction');
    result.url = state.url;
    try {
      if (!state.elements.length) throw new Error('Selector matched no elements');
      if (!field.multi && state.elements.length !== 1) throw new Error('Single selector matched multiple elements');
      const values = state.elements.map(element => transform(element.text, field.transform));
      Object.defineProperty(result.fields, field.name, {
        value: field.multi ? values : values[0], enumerable: true, configurable: true,
      });
    } catch (error) {
      Object.defineProperty(result.fields, field.name, {
        value: field.multi ? [] : null, enumerable: true, configurable: true,
      });
      result.errors.push({ field: field.name, reason: error.message });
    }
  }
  result.ok = result.errors.length === 0;
  return result;
}

export function diffRecords(previous, current) {
  const index = records => {
    if (!Array.isArray(records)) throw new Error('Prior/current results must be arrays');
    const result = new Map();
    for (const record of records) {
      if (!record || typeof record.url !== 'string' || !record.url || result.has(record.url)) {
        throw new Error('Every result needs one unique URL');
      }
      result.set(record.url, record);
    }
    return result;
  };
  const before = index(previous);
  const after = index(current);
  return {
    added: [...after.keys()].filter(url => !before.has(url)),
    removed: [...before.keys()].filter(url => !after.has(url)),
    changed: [...after.keys()].filter(url => before.has(url) && !isDeepStrictEqual(before.get(url), after.get(url))),
  };
}
