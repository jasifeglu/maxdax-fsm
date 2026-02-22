const technicians = [];

const technicianForm = document.getElementById('technician-form');
const skillsForm = document.getElementById('skills-form');
const jobForm = document.getElementById('job-form');

const skillTechSelect = document.getElementById('skill-tech');
const jobTechSelect = document.getElementById('job-tech');
const dashboardTechSelect = document.getElementById('dashboard-tech');

const statusList = document.getElementById('status-list');
const assignedJobs = document.getElementById('assigned-jobs');
const jobDetailsView = document.getElementById('job-details-view');
const dashboardCredentials = document.getElementById('dashboard-credentials');

function generateUsername(name) {
  const slug = name.toLowerCase().trim().replace(/\s+/g, '.');
  const suffix = Math.floor(Math.random() * 900 + 100);
  return `${slug}${suffix}`;
}

function generatePassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$';
  return Array.from({ length: 10 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

function addTechnician(name, status) {
  technicians.push({
    id: crypto.randomUUID(),
    name,
    status,
    credentials: {
      username: generateUsername(name),
      password: generatePassword()
    },
    skills: [],
    jobs: []
  });
  render();
}

function renderSelectOptions() {
  const options = technicians
    .map((tech) => `<option value="${tech.id}">${tech.name}</option>`)
    .join('');

  [skillTechSelect, jobTechSelect, dashboardTechSelect].forEach((select) => {
    select.innerHTML = options || '<option value="">No technicians</option>';
    select.disabled = technicians.length === 0;
  });
}

function renderStatusList() {
  statusList.innerHTML = technicians.length
    ? technicians
        .map(
          (tech) =>
            `<p><strong>${tech.name}</strong> <span class="badge">${tech.status}</span><br/><span class="muted">Skills: ${
              tech.skills.length ? tech.skills.join(', ') : 'None assigned'
            }</span></p>`
        )
        .join('')
    : '<p class="muted">No technicians added yet.</p>';
}

function renderDashboard() {
  const selectedId = dashboardTechSelect.value || technicians[0]?.id;
  const technician = technicians.find((tech) => tech.id === selectedId);

  if (!technician) {
    dashboardCredentials.textContent = 'Select a technician to view credentials and jobs.';
    assignedJobs.innerHTML = '<li class="muted">No jobs available.</li>';
    jobDetailsView.textContent = 'Select a job to see details.';
    return;
  }

  dashboardCredentials.innerHTML = `<strong>Generated Login</strong><br/>Username: ${technician.credentials.username}<br/>Password: ${technician.credentials.password}`;

  if (technician.jobs.length === 0) {
    assignedJobs.innerHTML = '<li class="muted">No assigned jobs.</li>';
    jobDetailsView.textContent = 'Select a job to see details.';
    jobDetailsView.classList.add('muted');
    return;
  }

  assignedJobs.innerHTML = technician.jobs
    .map((job, index) => `<li class="job-item" data-index="${index}">${job.title}</li>`)
    .join('');

  assignedJobs.querySelectorAll('.job-item').forEach((item) => {
    item.addEventListener('click', () => {
      assignedJobs.querySelectorAll('.job-item').forEach((node) => node.classList.remove('active'));
      item.classList.add('active');
      const idx = Number(item.dataset.index);
      const job = technician.jobs[idx];
      jobDetailsView.classList.remove('muted');
      jobDetailsView.textContent = `Title: ${job.title}\nDetails: ${job.details}`;
    });
  });

  const firstItem = assignedJobs.querySelector('.job-item');
  if (firstItem) {
    firstItem.click();
  }
}

function render() {
  renderSelectOptions();
  renderStatusList();
  renderDashboard();
}

technicianForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const name = document.getElementById('tech-name').value.trim();
  const status = document.getElementById('tech-status').value;
  if (!name) return;

  addTechnician(name, status);
  technicianForm.reset();
  document.getElementById('tech-status').value = 'Available';
});

skillsForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const technician = technicians.find((tech) => tech.id === skillTechSelect.value);
  const skillName = document.getElementById('skill-name').value.trim();
  if (!technician || !skillName) return;

  if (!technician.skills.includes(skillName)) {
    technician.skills.push(skillName);
  }

  skillsForm.reset();
  render();
});

jobForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const technician = technicians.find((tech) => tech.id === jobTechSelect.value);
  const title = document.getElementById('job-title').value.trim();
  const details = document.getElementById('job-details').value.trim();
  if (!technician || !title || !details) return;

  technician.jobs.push({ title, details });
  technician.status = 'On Job';
  jobForm.reset();
  render();
});

dashboardTechSelect.addEventListener('change', renderDashboard);

addTechnician('Taylor Morgan', 'Available');
technicians[0].skills.push('Electrical Diagnostics');
technicians[0].jobs.push({
  title: 'Repair breaker panel',
  details: 'Client: North Plaza\nPriority: High\nETA: Today 14:00\nNotes: Bring insulated tools.'
});
technicians[0].status = 'On Job';

render();
