const API = "/gateway/api/v1";
const POLL_INTERVAL_MS = 3000;
const POLL_MAX_ATTEMPTS = 100; // ~5 minutes

async function loadServices() {
  const container = document.getElementById("services");
  container.textContent = "Loading...";
  const response = await fetch(`${API}/services`);
  const list = await response.json();

  container.textContent = "";
  for (const entry of list) {
    container.appendChild(buildCard(entry));
  }
}

async function loadActivity() {
  const tbody = document.querySelector("#activity-table tbody");
  const response = await fetch(`${API}/audit?limit=20`);
  const entries = await response.json();

  tbody.textContent = "";
  if (entries.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = "No calls yet.";
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }

  for (const entry of entries) {
    const row = document.createElement("tr");
    const time = new Date(entry.timestamp).toLocaleTimeString();
    const statusCell = document.createElement("td");
    statusCell.textContent = entry.status_code;
    statusCell.className = entry.status_code >= 400 ? "bad" : "ok";
    for (const text of [time, entry.service, entry.kind]) {
      const cell = document.createElement("td");
      cell.textContent = text;
      row.appendChild(cell);
    }
    row.appendChild(statusCell);
    const latencyCell = document.createElement("td");
    latencyCell.textContent = `${entry.latency_ms} ms`;
    row.appendChild(latencyCell);
    tbody.appendChild(row);
  }
}

function buildCard(entry) {
  const card = document.createElement("section");
  card.className = "card";

  const title = document.createElement("h2");
  title.textContent = entry.name;

  const badge = document.createElement("span");
  badge.className = `badge ${entry.health}`;
  badge.textContent = entry.health;
  title.appendChild(badge);

  const description = document.createElement("p");
  description.textContent = entry.description;

  const textarea = document.createElement("textarea");
  textarea.rows = 6;
  textarea.value = JSON.stringify(entry.query_example, null, 2);

  const sendButton = document.createElement("button");
  sendButton.textContent = "Send";

  const output = document.createElement("pre");
  output.className = "output";

  sendButton.addEventListener("click", () => send(entry.name, textarea, sendButton, output));

  card.append(title, description, textarea, sendButton, output);
  return card;
}

async function send(name, textarea, button, out) {
  let payload;
  try {
    payload = JSON.parse(textarea.value);
  } catch (err) {
    setOutput(out, `Invalid JSON: ${err.message}`, true);
    return;
  }

  button.disabled = true;
  setOutput(out, "Sending...", false);
  try {
    const response = await fetch(`${API}/services/${name}/query`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) {
      renderError(body, out);
    } else {
      render(name, body.data, out);
    }
  } finally {
    button.disabled = false;
    loadActivity();
  }
}

function setOutput(out, text, isError) {
  out.textContent = text;
  out.classList.toggle("error", isError);
}

function renderError(body, out) {
  // Gateway-level errors (unknown service, unreachable) come back flat
  // ({error_code, message}); errors relayed from a reachable downstream
  // service are nested under `data`. Try both shapes.
  const errorPayload = body && body.data ? body.data : body;
  const code = errorPayload && errorPayload.error_code ? errorPayload.error_code : "error";
  const message = errorPayload && errorPayload.message ? errorPayload.message : "Request failed.";
  setOutput(out, `[${code}] ${message}`, true);
}

function render(name, data, out) {
  if (data && data.job_id) {
    poll(name, data.job_id, out);
  } else if (data && data.answer) {
    // Reports render as preformatted text for now; a markdown renderer can
    // replace this if the console ever needs richer formatting.
    const sources = Array.isArray(data.sources) ? `\n\nSources:\n${data.sources.join("\n")}` : "";
    setOutput(out, data.answer + sources, false);
  } else {
    setOutput(out, JSON.stringify(data, null, 2), false);
  }
}

async function poll(name, jobId, out) {
  const log = [];
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    const response = await fetch(`${API}/services/${name}/jobs/${jobId}`);
    const body = await response.json();

    loadActivity();
    if (!response.ok) {
      renderError(body, out);
      return;
    }

    const status = body.data.status;
    if (log[log.length - 1] !== status) {
      log.push(status);
    }

    if (status === "done" || status === "failed") {
      const report = body.data.report || body.data.error || "(no output)";
      setOutput(out, `${log.join(" -> ")}\n\n${report}`, status === "failed");
      return;
    }

    setOutput(out, `${log.join(" -> ")}\n`, false);
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
  out.textContent += "\nStill running -- send another request to poll again.";
}

document.getElementById("refresh").addEventListener("click", () => {
  loadServices();
  loadActivity();
});
loadServices();
loadActivity();
