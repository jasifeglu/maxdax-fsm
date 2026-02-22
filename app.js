const revenueData = [
  { month: "Jan", amount: 12800 },
  { month: "Feb", amount: 14900 },
  { month: "Mar", amount: 17650 },
  { month: "Apr", amount: 16320 },
  { month: "May", amount: 18990 },
  { month: "Jun", amount: 21400 }
];

const technicians = [
  { name: "Ava Stone", completed: 64, resolution: "3.2h", csat: "95%", utilization: 86 },
  { name: "Mason Lee", completed: 58, resolution: "3.9h", csat: "92%", utilization: 78 },
  { name: "Nora Patel", completed: 71, resolution: "2.8h", csat: "97%", utilization: 91 },
  { name: "Liam Chen", completed: 49, resolution: "4.1h", csat: "89%", utilization: 74 }
];

const pendingPayments = [
  { label: "0-15 Days", value: 18400, color: "#2563eb" },
  { label: "16-30 Days", value: 11250, color: "#0ea5e9" },
  { label: "31-60 Days", value: 7960, color: "#f59e0b" },
  { label: "61+ Days", value: 4350, color: "#dc2626" }
];

const ticketStatus = [
  { status: "Open", count: 48, color: "#f59e0b" },
  { status: "In Progress", count: 73, color: "#2563eb" },
  { status: "Resolved", count: 152, color: "#10b981" },
  { status: "On Hold", count: 19, color: "#ef4444" }
];

const currency = (value) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

function renderRevenue() {
  const chart = document.getElementById("revenue-chart");
  const totalEl = document.getElementById("total-revenue");
  const max = Math.max(...revenueData.map((item) => item.amount));
  const total = revenueData.reduce((sum, item) => sum + item.amount, 0);
  totalEl.textContent = currency(total);

  chart.innerHTML = revenueData
    .map((item) => {
      const height = Math.round((item.amount / max) * 180) + 20;
      return `
        <div class="bar-group">
          <div class="bar" style="height:${height}px" title="${currency(item.amount)}"></div>
          <small>${item.month}</small>
          <strong>${currency(item.amount)}</strong>
        </div>
      `;
    })
    .join("");
}

function renderTechnicians() {
  const table = document.getElementById("tech-table");
  table.innerHTML = `
    <div class="tech-row tech-head">
      <span>Technician</span>
      <span>Completed</span>
      <span>Resolution</span>
      <span>Utilization</span>
    </div>
    ${technicians
      .map(
        (tech) => `
      <div class="tech-row">
        <div>
          <strong>${tech.name}</strong><br />
          <small>CSAT ${tech.csat}</small>
        </div>
        <span class="metric-pill">${tech.completed}</span>
        <span>${tech.resolution}</span>
        <div>
          <div class="utilization-track"><div class="utilization-fill" style="width:${tech.utilization}%"></div></div>
          <small>${tech.utilization}%</small>
        </div>
      </div>`
      )
      .join("")}
  `;
}

function renderPayments() {
  const ring = document.getElementById("payment-ring");
  const list = document.getElementById("payment-list");
  const total = pendingPayments.reduce((sum, entry) => sum + entry.value, 0);
  let current = 0;

  const gradientStops = pendingPayments
    .map((entry) => {
      const start = (current / total) * 360;
      current += entry.value;
      const end = (current / total) * 360;
      return `${entry.color} ${start}deg ${end}deg`;
    })
    .join(", ");

  ring.style.background = `conic-gradient(${gradientStops})`;

  list.innerHTML = pendingPayments
    .map(
      (entry) => `
      <li>
        <span><i class="dot" style="background:${entry.color}"></i>${entry.label}</span>
        <strong>${currency(entry.value)}</strong>
      </li>
    `
    )
    .join("");
}

function renderTicketStatus() {
  const container = document.getElementById("ticket-status");
  const max = Math.max(...ticketStatus.map((item) => item.count));

  container.innerHTML = ticketStatus
    .map(
      (item) => `
    <div class="status-row">
      <strong>${item.status}</strong>
      <div class="status-track">
        <div class="status-fill" style="width:${Math.round((item.count / max) * 100)}%; background:${item.color}"></div>
      </div>
      <span>${item.count} tickets</span>
    </div>
  `
    )
    .join("");
}

renderRevenue();
renderTechnicians();
renderPayments();
renderTicketStatus();
