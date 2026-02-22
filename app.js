const technicians = [
  { id: 't1', name: 'Alex Kim', status: 'Available' },
  { id: 't2', name: 'Rita Patel', status: 'Installation' },
  { id: 't3', name: 'Jordan Lee', status: 'Offline' },
  { id: 't4', name: 'Sam Rivera', status: 'Available' }
];

const jobs = [
  { id: 'j1', title: 'Fiber install - 24 Oak St', date: '2026-02-03', technicianId: 't2' },
  { id: 'j2', title: 'Router replacement - 91 Pine Ave', date: '2026-02-05', technicianId: 't1' },
  { id: 'j3', title: 'Service activation - 210 Lake Dr', date: '2026-02-14', technicianId: '' },
  { id: 'j4', title: 'New line setup - 15 River Rd', date: '2026-02-19', technicianId: 't4' },
  { id: 'j5', title: 'Signal check - 45 Meadow Ln', date: '2026-02-24', technicianId: '' }
];

const statusOptions = ['Available', 'Installation', 'Offline'];
let viewDate = new Date(2026, 1, 1);

const techContainer = document.getElementById('technicians');
const jobsContainer = document.getElementById('jobs');
const monthLabel = document.getElementById('monthLabel');
const calendar = document.getElementById('calendar');

function techNameById(id) {
  return technicians.find((t) => t.id === id)?.name || 'Unassigned';
}

function renderTechnicians() {
  techContainer.innerHTML = '';

  technicians.forEach((tech) => {
    const card = document.createElement('article');
    card.className = 'tech-card';

    const h3 = document.createElement('h3');
    h3.textContent = tech.name;

    const badge = document.createElement('span');
    badge.className = `status-badge status-${tech.status.toLowerCase()}`;
    badge.textContent = tech.status;

    const statusSelect = document.createElement('select');
    statusOptions.forEach((status) => {
      const option = document.createElement('option');
      option.value = status;
      option.textContent = status;
      option.selected = status === tech.status;
      statusSelect.append(option);
    });

    statusSelect.addEventListener('change', (event) => {
      tech.status = event.target.value;
      renderTechnicians();
      renderCalendar();
      renderJobs();
    });

    card.append(h3, badge, statusSelect);
    techContainer.append(card);
  });
}

function renderJobs() {
  jobsContainer.innerHTML = '';
  const template = document.getElementById('jobTemplate');

  jobs
    .slice()
    .sort((a, b) => a.date.localeCompare(b.date))
    .forEach((job) => {
      const node = template.content.firstElementChild.cloneNode(true);
      node.querySelector('.job-title').textContent = job.title;
      node.querySelector('.job-date').textContent = new Date(job.date).toLocaleDateString();

      const select = node.querySelector('.job-tech-select');
      const unassigned = document.createElement('option');
      unassigned.value = '';
      unassigned.textContent = 'Unassigned';
      select.append(unassigned);

      technicians.forEach((tech) => {
        const option = document.createElement('option');
        option.value = tech.id;
        option.textContent = `${tech.name} (${tech.status})`;
        if (tech.id === job.technicianId) option.selected = true;
        select.append(option);
      });

      select.addEventListener('change', (event) => {
        job.technicianId = event.target.value;
        renderJobs();
        renderCalendar();
      });

      jobsContainer.append(node);
    });
}

function renderCalendar() {
  calendar.innerHTML = '';
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  dayNames.forEach((day) => {
    const header = document.createElement('div');
    header.className = 'day-name';
    header.textContent = day;
    calendar.append(header);
  });

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  monthLabel.textContent = viewDate.toLocaleString(undefined, { month: 'long', year: 'numeric' });

  const first = new Date(year, month, 1);
  const firstWeekday = first.getDay();
  const gridStart = new Date(year, month, 1 - firstWeekday);

  for (let i = 0; i < 42; i += 1) {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + i);
    const isoDate = date.toISOString().slice(0, 10);

    const cell = document.createElement('div');
    cell.className = 'day-cell';
    if (date.getMonth() !== month) cell.classList.add('other-month');

    const num = document.createElement('div');
    num.className = 'day-num';
    num.textContent = date.getDate();

    const dayJobs = document.createElement('div');
    dayJobs.className = 'day-jobs';

    jobs
      .filter((job) => job.date === isoDate)
      .forEach((job) => {
        const jobNode = document.createElement('div');
        const tech = technicians.find((t) => t.id === job.technicianId);
        jobNode.className = 'day-job';
        jobNode.innerHTML = `<strong>${job.title}</strong><small>${techNameById(job.technicianId)}${tech ? ` • ${tech.status}` : ''}</small>`;
        dayJobs.append(jobNode);
      });

    cell.append(num, dayJobs);
    calendar.append(cell);
  }
}

document.getElementById('prevMonth').addEventListener('click', () => {
  viewDate = new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1);
  renderCalendar();
});

document.getElementById('nextMonth').addEventListener('click', () => {
  viewDate = new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1);
  renderCalendar();
});

renderTechnicians();
renderJobs();
renderCalendar();
