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
    out.textContent = `Invalid JSON: ${err.message}`;
    return;
  }

  button.disabled = true;
  out.textContent = "Sending...";
  try {
    const response = await fetch(`${API}/services/${name}/query`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    const envelope = await response.json();
    if (envelope.status_code >= 400) {
      renderError(envelope.data, out);
    } else {
      render(name, envelope.data, out);
    }
  } finally {
    button.disabled = false;
  }
}

function renderError(data, out) {
  const code = data && data.error_code ? data.error_code : "error";
  const message = data && data.message ? data.message : "Request failed.";
  out.textContent = `[${code}] ${message}`;
}

function render(name, data, out) {
  if (data && data.job_id) {
    poll(name, data.job_id, out);
  } else if (data && data.answer) {
    // ponytail: report renders as preformatted text, upgrade to a markdown
    // renderer if the console ever needs richer formatting.
    const sources = Array.isArray(data.sources) ? `\n\nSources:\n${data.sources.join("\n")}` : "";
    out.textContent = data.answer + sources;
  } else {
    out.textContent = JSON.stringify(data, null, 2);
  }
}

async function poll(name, jobId, out) {
  const log = [];
  for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
    const response = await fetch(`${API}/services/${name}/jobs/${jobId}`);
    const envelope = await response.json();

    if (envelope.status_code >= 400) {
      renderError(envelope.data, out);
      return;
    }

    const status = envelope.data.status;
    if (log[log.length - 1] !== status) {
      log.push(status);
    }
    out.textContent = `${log.join(" -> ")}\n`;

    if (status === "done" || status === "failed") {
      const report = envelope.data.report || envelope.data.error || "(no output)";
      out.textContent += `\n${report}`;
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
  out.textContent += "\nStill running -- send another request to poll again.";
}

document.getElementById("refresh").addEventListener("click", loadServices);
loadServices();
