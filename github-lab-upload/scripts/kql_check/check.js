// Usage: cd scripts/kql_check && npm install && node check.js
// - detections/*.kql: SYNTAX only (real table schemas are not loaded).
// - SC-200/lab-queries/*.datatable.kql: SYNTAX + SEMANTIC (self-contained: schema is embedded via datatable).
// This does NOT execute queries and is NOT a substitute for running them in a real workspace.
const fs = require('fs'), path = require('path');
require('@kusto/language-service-next/bridge.js');
require('@kusto/language-service-next/Kusto.Language.Bridge.js');
const K = Kusto.Language;
const root = path.resolve(__dirname, '..', '..');
const list = (d) => fs.readdirSync(d).filter(f => f.endsWith('.kql')).map(f => path.join(d, f));
let problems = 0;
const dirs = [path.join(root, 'detections'), path.join(root, 'SC-200', 'lab-queries'), path.join(root, 'SC-200', 'article-lab', 'queries'), path.join(root, 'SC-200', 'article-lab', 'datatable')].filter(d => fs.existsSync(d));
for (const f of dirs.flatMap(list)) {
  const text = fs.readFileSync(f, 'utf8');
  const learner = f.endsWith('.datatable.kql');
  const code = learner ? K.KustoCode.ParseAndAnalyze(text) : K.KustoCode.Parse(text);
  const diags = code.GetDiagnostics(); const msgs = [];
  for (let i = 0; i < diags.Count; i++) msgs.push(diags.getItem(i).Message);
  console.log((msgs.length ? 'ISSUES ' : 'OK     ') + path.relative(root, f) + (msgs.length ? ' :: ' + msgs.join(' | ') : ''));
  problems += msgs.length;
}
console.log('TOTAL_ISSUES=' + problems);
process.exit(problems ? 1 : 0);
