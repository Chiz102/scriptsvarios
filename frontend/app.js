const API_URL = 'http://localhost:5000/api';

// Estado global de la aplicación
const state = {
    currentUser: null,
    tasks: [],
    currentView: 'tasks',
    editingTask: null
};

// Elementos DOM
const dom = {
    authContainer: document.getElementById('authContainer'),
    appContainer: document.getElementById('appContainer'),
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),
    authTabs: document.querySelectorAll('.auth-tab'),
    userUsername: document.getElementById('userUsername'),
    logoutBtn: document.getElementById('logoutBtn'),
    taskList: document.getElementById('taskList'),
    newTaskBtn: document.getElementById('newTaskBtn'),
    taskModal: document.getElementById('taskModal'),
    taskForm: document.getElementById('taskForm'),
    cancelTaskBtn: document.getElementById('cancelTaskBtn'),
    searchInput: document.getElementById('searchInput'),
    statusFilter: document.getElementById('statusFilter'),
    priorityFilter: document.getElementById('priorityFilter'),
    categoryFilter: document.getElementById('categoryFilter'),
    views: {
        tasks: document.getElementById('tasksView'),
        calendar: document.getElementById('calendarView'),
        reports: document.getElementById('reportsView')
    }
};

// Inicialización de FullCalendar
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: state.tasks.map(task => ({
            id: task.id,
            title: task.title,
            start: task.due_date,
            backgroundColor: getStatusColor(task.status),
            borderColor: getStatusColor(task.status)
        })),
        eventClick: function(info) {
            const task = state.tasks.find(t => t.id === parseInt(info.event.id));
            if (task) {
                showTaskDetails(task);
            }
        }
    });
    calendar.render();
}

// Inicialización de gráficos
function initializeCharts() {
    // Gráfico de categorías
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    categoryChart = new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Gráfico de productividad
    const productivityCtx = document.getElementById('productivityChart').getContext('2d');
    productivityChart = new Chart(productivityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Tareas Completadas',
                data: [],
                borderColor: '#7B68EE',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Funciones de utilidad
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function isOverdue(dateString) {
    if (!dateString) return false;
    return new Date(dateString) < new Date();
}

function getStatusColor(status) {
    const colors = {
        'pending': '#FFC107',
        'in_progress': '#17A2B8',
        'completed': '#28A745'
    };
    return colors[status] || '#6C757D';
}

// Funciones de renderizado
function renderTask(task) {
    const taskElement = document.createElement('div');
    taskElement.className = `task-item ${task.status === 'completed' ? 'completed' : ''}`;
    taskElement.innerHTML = `
        <div class="task-header">
            <div class="task-title-container">
                <h5 class="task-title">${task.title}</h5>
                <span class="priority-badge priority-${task.priority}">
                    <i class="fas fa-flag"></i> ${task.priority}
                </span>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="updateTaskStatus(${task.id}, '${task.status === 'completed' ? 'pending' : 'completed'}')">
                    <i class="fas ${task.status === 'completed' ? 'fa-undo' : 'fa-check'}"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        <p class="task-description">${task.description || 'Sin descripción'}</p>
        <div class="task-meta">
            <span class="task-status status-${task.status}">${task.status}</span>
            ${task.category ? `
                <span class="category-badge">
                    <i class="fas fa-folder"></i> ${task.category}
                </span>
            ` : ''}
            ${task.due_date ? `
                <span class="due-date ${isOverdue(task.due_date) ? 'overdue' : ''}">
                    <i class="fas fa-clock"></i> ${formatDate(task.due_date)}
                </span>
            ` : ''}
            ${task.estimated_hours ? `
                <span class="hours-badge">
                    <i class="fas fa-hourglass-half"></i> ${task.estimated_hours}h
                </span>
            ` : ''}
        </div>
    `;
    return taskElement;
}

function renderTasks() {
    const filteredTasks = filterTasks(state.tasks);
    dom.taskList.innerHTML = filteredTasks.map(task => renderTask(task)).join('');
}

// Funciones de reportes
async function loadReports() {
    try {
        // Calcular estadísticas de las tareas actuales
        const stats = calculateTaskStatistics(state.tasks);
        renderSummaryCards(stats);
        updateCategoryChart(stats);
        updateProductivityChart(stats);
        renderTimeTrackingTable(stats);
    } catch (error) {
        console.error('Error loading reports:', error);
        showNotification('Error al cargar los reportes', 'error');
    }
}

function calculateTaskStatistics(tasks) {
    const now = new Date();
    const stats = {
        total_tasks: tasks.length,
        completed_tasks: tasks.filter(t => t.status === 'completed').length,
        in_progress_tasks: tasks.filter(t => t.status === 'in_progress').length,
        pending_tasks: tasks.filter(t => t.status === 'pending').length,
        overdue_tasks: tasks.filter(t => t.status !== 'completed' && new Date(t.due_date) < now).length,
        completion_rate: 0,
        categories: {},
        productivity_trend: {},
        time_tracking: []
    };

    // Calcular tasa de completitud
    if (stats.total_tasks > 0) {
        stats.completion_rate = (stats.completed_tasks / stats.total_tasks) * 100;
    }

    // Agrupar por categoría
    tasks.forEach(task => {
        if (!stats.categories[task.category]) {
            stats.categories[task.category] = {
                total: 0,
                completed: 0
            };
        }
        stats.categories[task.category].total++;
        if (task.status === 'completed') {
            stats.categories[task.category].completed++;
        }
    });

    // Calcular tendencia de productividad (últimos 7 días)
    const last7Days = Array.from({length: 7}, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - i);
        return date.toISOString().split('T')[0];
    }).reverse();

    last7Days.forEach(date => {
        stats.productivity_trend[date] = tasks.filter(task => 
            task.status === 'completed' && 
            task.completed_date && 
            task.completed_date.startsWith(date)
        ).length;
    });

    // Preparar datos de seguimiento de tiempo
    stats.time_tracking = tasks.map(task => ({
        title: task.title,
        estimated_hours: task.estimated_hours || 0,
        actual_hours: task.actual_hours || 0,
        difference: (task.actual_hours || 0) - (task.estimated_hours || 0)
    })).sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference));

    return stats;
}

function renderSummaryCards(stats) {
    const summaryReport = document.getElementById('summaryReport');
    summaryReport.innerHTML = `
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-value">${stats.total_tasks}</span>
                <span class="stat-label">Total Tasks</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.completed_tasks}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.in_progress_tasks}</span>
                <span class="stat-label">In Progress</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.pending_tasks}</span>
                <span class="stat-label">Pending</span>
            </div>
            <div class="stat-item ${stats.overdue_tasks > 0 ? 'warning' : ''}">
                <span class="stat-value">${stats.overdue_tasks}</span>
                <span class="stat-label">Overdue</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${stats.completion_rate.toFixed(1)}%</span>
                <span class="stat-label">Completion Rate</span>
            </div>
        </div>
    `;
}

function updateCategoryChart(stats) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Destruir el gráfico existente si hay uno
    if (window.categoryChart instanceof Chart) {
        window.categoryChart.destroy();
    }

    const categories = Object.keys(stats.categories);
    const categoryData = categories.map(cat => stats.categories[cat].total);
    const completedData = categories.map(cat => stats.categories[cat].completed);

    window.categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Total Tasks',
                    data: categoryData,
                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Completed Tasks',
                    data: completedData,
                    backgroundColor: 'rgba(34, 197, 94, 0.5)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateProductivityChart(stats) {
    const ctx = document.getElementById('productivityChart').getContext('2d');
    
    // Destruir el gráfico existente si hay uno
    if (window.productivityChart instanceof Chart) {
        window.productivityChart.destroy();
    }

    const dates = Object.keys(stats.productivity_trend);
    const completedTasks = dates.map(date => stats.productivity_trend[date]);

    window.productivityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(date => formatDate(date)),
            datasets: [{
                label: 'Completed Tasks',
                data: completedTasks,
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderTimeTrackingTable(stats) {
    const tbody = document.getElementById('timeTrackingTable');
    tbody.innerHTML = stats.time_tracking.map(task => `
        <tr class="${Math.abs(task.difference) > 2 ? 'highlight' : ''}">
            <td>${task.title}</td>
            <td>${task.estimated_hours}h</td>
            <td>${task.actual_hours}h</td>
            <td class="${task.difference > 0 ? 'over-time' : task.difference < 0 ? 'under-time' : ''}">${
                task.difference > 0 ? '+' : ''}${task.difference.toFixed(1)}h</td>
        </tr>
    `).join('');
}

// Funciones de API
async function fetchTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);
        state.tasks = await response.json();
        renderTasks();
        
        // Actualizar calendario si está visible
        if (state.currentView === 'calendar' && calendar) {
            calendar.removeAllEvents();
            calendar.addEventSource(state.tasks.map(task => ({
                id: task.id,
                title: task.title,
                start: task.due_date,
                backgroundColor: getStatusColor(task.status),
                borderColor: getStatusColor(task.status)
            })));
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
        showNotification('Error al cargar las tareas', 'error');
    }
}

async function createTask(taskData) {
    try {
        const response = await fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData),
        });
        if (response.ok) {
            await fetchTasks();
            document.getElementById('taskForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('taskModal')).hide();
            showNotification('Tarea creada exitosamente', 'success');
        } else {
            throw new Error('Error al crear la tarea');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showNotification('Error al crear la tarea', 'error');
    }
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        const task = state.tasks.find(t => t.id === taskId);
        if (!task) return;

        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ...task, status: newStatus }),
        });
        if (response.ok) {
            await fetchTasks();
            showNotification('Estado de tarea actualizado', 'success');
        } else {
            throw new Error('Error al actualizar la tarea');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showNotification('Error al actualizar la tarea', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta tarea?')) return;

    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            await fetchTasks();
            showNotification('Tarea eliminada exitosamente', 'success');
        } else {
            throw new Error('Error al eliminar la tarea');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error al eliminar la tarea', 'error');
    }
}

// Funciones de UI
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function handleTagInput(event) {
    if (event.key === 'Enter' && event.target.value.trim()) {
        const tag = event.target.value.trim();
        tags.add(tag);
        updateTagsDisplay();
        event.target.value = '';
    }
}

function updateTagsDisplay() {
    const container = document.querySelector('.tags-container');
    container.innerHTML = '';
    tags.forEach(tag => {
        const tagElement = document.createElement('span');
        tagElement.className = 'tag';
        tagElement.innerHTML = `
            ${tag}
            <i class="fas fa-times remove-tag" onclick="removeTag('${tag}')"></i>
        `;
        container.appendChild(tagElement);
    });
}

function removeTag(tag) {
    tags.delete(tag);
    updateTagsDisplay();
}

function switchView(viewName) {
    Object.values(dom.views).forEach(view => view.style.display = 'none');
    dom.views[viewName].style.display = 'block';
    state.currentView = viewName;

    if (viewName === 'calendar') {
        loadCalendarTasks();
    } else if (viewName === 'reports') {
        loadReports();
    }
}

// Funciones de autenticación
async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const user = await response.json();
        state.currentUser = user;
        localStorage.setItem('user', JSON.stringify(user));
        showApp();
        loadTasks();
    } catch (error) {
        alert(error.message);
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const user = await response.json();
        state.currentUser = user;
        localStorage.setItem('user', JSON.stringify(user));
        showApp();
        loadTasks();
    } catch (error) {
        alert(error.message);
    }
}

function logout() {
    state.currentUser = null;
    localStorage.removeItem('user');
    showAuth();
}

function showAuth() {
    dom.authContainer.style.display = 'flex';
    dom.appContainer.style.display = 'none';
}

function showApp() {
    dom.authContainer.style.display = 'none';
    dom.appContainer.style.display = 'flex';
    dom.userUsername.textContent = state.currentUser.username;
}

// Funciones de tareas
async function loadTasks() {
    try {
        const response = await fetch(`/api/tasks?user_id=${state.currentUser.id}`);
        state.tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

async function createTask(taskData) {
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...taskData,
                user_id: state.currentUser.id
            })
        });

        const newTask = await response.json();
        state.tasks.push(newTask);
        renderTasks();
        closeTaskModal();
    } catch (error) {
        console.error('Error creating task:', error);
    }
}

async function updateTask(taskId, taskData) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });

        const updatedTask = await response.json();
        state.tasks = state.tasks.map(task => 
            task.id === updatedTask.id ? updatedTask : task
        );
        renderTasks();
        closeTaskModal();
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) return;

    try {
        await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        state.tasks = state.tasks.filter(task => task.id !== taskId);
        renderTasks();
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// Funciones de renderizado
function renderTasks() {
    const filteredTasks = filterTasks(state.tasks);
    dom.taskList.innerHTML = filteredTasks.map(task => renderTask(task)).join('');
}

function filterTasks(tasks) {
    const searchTerm = dom.searchInput.value.toLowerCase();
    const status = dom.statusFilter.value;
    const priority = dom.priorityFilter.value;
    const category = dom.categoryFilter.value;

    return tasks.filter(task => {
        const matchesSearch = task.title.toLowerCase().includes(searchTerm) ||
                            task.description.toLowerCase().includes(searchTerm);
        const matchesStatus = !status || task.status === status;
        const matchesPriority = !priority || task.priority === priority;
        const matchesCategory = !category || task.category === category;

        return matchesSearch && matchesStatus && matchesPriority && matchesCategory;
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Comprobar si hay un usuario en localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        state.currentUser = JSON.parse(savedUser);
        showApp();
        loadTasks();
    } else {
        showAuth();
    }

    // Auth event listeners
    dom.authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            dom.authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const form = tab.dataset.tab === 'login' ? dom.loginForm : dom.registerForm;
            const otherForm = tab.dataset.tab === 'login' ? dom.registerForm : dom.loginForm;
            form.style.display = 'flex';
            otherForm.style.display = 'none';
        });
    });

    dom.loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = e.target.loginEmail.value;
        const password = e.target.loginPassword.value;
        login(email, password);
    });

    dom.registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = e.target.registerUsername.value;
        const email = e.target.registerEmail.value;
        const password = e.target.registerPassword.value;
        register(username, email, password);
    });

    dom.logoutBtn.addEventListener('click', logout);

    // Task event listeners
    dom.newTaskBtn.addEventListener('click', () => {
        state.editingTask = null;
        dom.taskForm.reset();
        dom.taskModal.style.display = 'block';
    });

    dom.taskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const taskData = {
            title: e.target.taskTitle.value,
            description: e.target.taskDescription.value,
            status: e.target.taskStatus.value,
            priority: e.target.taskPriority.value,
            due_date: e.target.taskDueDate.value,
            category: e.target.taskCategory.value,
            estimated_hours: parseFloat(e.target.taskEstimatedHours.value) || 0,
            actual_hours: parseFloat(e.target.taskActualHours.value) || 0,
            tags: e.target.taskTags.value.split(',').map(tag => tag.trim()).filter(Boolean)
        };

        if (state.editingTask) {
            updateTask(state.editingTask.id, taskData);
        } else {
            createTask(taskData);
        }
    });

    // Filter event listeners
    dom.searchInput.addEventListener('input', renderTasks);
    dom.statusFilter.addEventListener('change', renderTasks);
    dom.priorityFilter.addEventListener('change', renderTasks);
    dom.categoryFilter.addEventListener('change', renderTasks);

    // View navigation
    document.querySelectorAll('[data-view]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewName = e.target.dataset.view;
            switchView(viewName);
        });
    });
});

// Modal functions
function closeTaskModal() {
    dom.taskModal.style.display = 'none';
    dom.taskForm.reset();
    state.editingTask = null;
}

function editTask(taskId) {
    const task = state.tasks.find(t => t.id === taskId);
    if (!task) return;

    state.editingTask = task;
    
    const form = dom.taskForm;
    form.taskTitle.value = task.title;
    form.taskDescription.value = task.description || '';
    form.taskStatus.value = task.status;
    form.taskPriority.value = task.priority;
    form.taskDueDate.value = task.due_date ? task.due_date.slice(0, 16) : '';
    form.taskCategory.value = task.category;
    form.taskEstimatedHours.value = task.estimated_hours;
    form.taskActualHours.value = task.actual_hours;
    form.taskTags.value = task.tags.join(', ');

    dom.taskModal.style.display = 'block';
}

// Close modal when clicking outside or on close button
dom.taskModal.addEventListener('click', (e) => {
    if (e.target === dom.taskModal) {
        closeTaskModal();
    }
});

document.querySelector('.close').addEventListener('click', closeTaskModal);
dom.cancelTaskBtn.addEventListener('click', closeTaskModal);

// Añadir estilos adicionales para los reportes
const style = document.createElement('style');
style.textContent = `
    .summary-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }

    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        background: var(--bg-color);
        border-radius: 0.5rem;
        transition: transform 0.2s ease;
    }

    .stat-item:hover {
        transform: translateY(-2px);
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
    }

    .stat-label {
        font-size: 0.875rem;
        color: var(--text-light);
        margin-top: 0.25rem;
    }

    .warning .stat-value {
        color: var(--warning-color);
    }

    .over-time {
        color: var(--danger-color);
    }

    .under-time {
        color: var(--success-color);
    }

    .highlight {
        background-color: rgba(var(--warning-color), 0.1);
    }

    .table {
        width: 100%;
        border-collapse: collapse;
    }

    .table th,
    .table td {
        padding: 0.75rem;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }

    .table th {
        font-weight: 600;
        color: var(--text-color);
        background-color: var(--bg-color);
    }

    .table tr:hover {
        background-color: var(--bg-color);
    }
`;
document.head.appendChild(style); 