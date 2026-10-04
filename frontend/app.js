const rows = document.getElementById("docRows");
const detail = document.getElementById("detail");
let selectedId = null;

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
}

async function loadDocs() {
  const res = await fetch("/documents");
  const docs = await res.json();
  rows.innerHTML = docs.map(d => `
    <tr>
      <td>${d.id}</td>
      <td>${esc(d.filename)}</td>
      <td>${esc(d.vendor || "-")}</td>
      <td>${d.total != null ? "$" + Number(d.total).toLocaleString() : "-"}</td>
      <td><span class="badge ${d.risk_level || "unknown"}">${d.risk_level ? d.risk_level + " (" + d.risk_score + ")" : "-"}</span></td>
      <td class="st-${d.status}">${d.status}</td>
      <td><button class="small" onclick="showDoc(${d.id})">View</button></td>
    </tr>`).join("");
  if (selectedId) showDoc(selectedId, false);
}

async function showDoc(id, scroll = true) {
  selectedId = id;
  const d = await (await fetch("/documents/" + id)).json();
  const t = d.trace || {};
  detail.style.display = "block";
  document.getElementById("detailTitle").textContent = `#${d.id} ${d.filename} (${d.status})`;

  let actions = "";
  if (d.status === "pending_approval") {
    actions = `<button class="approve" onclick="decide(${d.id}, 'approve')">Approve</button>
               <button class="reject" onclick="decide(${d.id}, 'reject')">Reject</button>`;
  } else if (d.decided_by) {
    actions = `<em>Decided by ${esc(d.decided_by)} at ${esc(d.decided_at)}</em>`;
  }
  document.getElementById("actions").innerHTML = actions;

  const steps = [];
  if (t.decision_reason) steps.push(["Decision", t.decision_reason]);
  if (t.error) steps.push(["Error", t.error]);
  if (t.guardrail) steps.push(["1. Guardrail Agent", JSON.stringify(t.guardrail, null, 2)]);
  if (t.extraction) steps.push(["2. Extraction Agent", JSON.stringify(t.extraction, null, 2)]);
  if (t.compliance) steps.push(["3. Compliance Agent", JSON.stringify(t.compliance, null, 2)]);
  if (t.risk) steps.push(["4. Risk Agent", JSON.stringify(t.risk, null, 2)]);
  if (t.email) steps.push(["5. Communication Agent (drafted email)", t.email.subject + "\n\n" + t.email.body]);

  document.getElementById("detailBody").innerHTML =
    steps.map(s => `<div class="step"><h3>${s[0]}</h3><pre>${esc(s[1])}</pre></div>`).join("");
  if (scroll) detail.scrollIntoView({behavior: "smooth"});
}

async function decide(id, action) {
  const res = await fetch(`/documents/${id}/${action}`, {method: "POST"});
  if (!res.ok) alert((await res.json()).detail);
  loadDocs();
}

document.getElementById("uploadBtn").onclick = async () => {
  const file = document.getElementById("fileInput").files[0];
  const msg = document.getElementById("uploadMsg");
  if (!file) { msg.textContent = " Choose a PDF first."; return; }
  const form = new FormData();
  form.append("file", file);
  msg.textContent = " Uploading...";
  const res = await fetch("/upload", {method: "POST", body: form});
  if (!res.ok) { msg.textContent = " " + (await res.json()).detail; return; }
  const out = await res.json();
  msg.textContent = ` Processing document #${out.id}. This takes about 30 seconds.`;
  selectedId = out.id;
  loadDocs();
};

loadDocs();
setInterval(loadDocs, 4000);