/**
 * PlanGenie - Frontend Application Logic
 * Vanilla JavaScript implementation with zero external framework dependencies.
 * Uses strict DOM manipulation with textContent to eliminate XSS risks.
 */

(function () {
  'use strict';

  // --- Application State ---
  const state = {
    currentEvent: null,
    savedEvents: [],
    config: null,
    activeTab: 'panelBudget',
    taskFilter: 'all',
    currencySymbol: '₹',
    currencyCode: 'INR'
  };

  // --- Currency Symbol Mapping ---
  const CURRENCY_SYMBOLS = {
    'INR': '₹',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'CAD': 'CA$',
    'AUD': 'AU$',
    'AED': 'AED',
    'SGD': 'S$'
  };

  // --- DOM Elements ---
  const elements = {
    // Nav & View Panels
    viewCreateEvent: document.getElementById('viewCreateEvent'),
    viewDashboard: document.getElementById('viewDashboard'),
    btnNavNewEvent: document.getElementById('btnNavNewEvent'),
    btnNavSavedEvents: document.getElementById('btnNavSavedEvents'),
    savedEventsCount: document.getElementById('savedEventsCount'),
    aiStatusText: document.getElementById('aiStatusText'),
    aiStatusNotice: document.getElementById('aiStatusNotice'),

    // Create Event Form
    formEventCreate: document.getElementById('formEventCreate'),
    btnGeneratePlan: document.getElementById('btnGeneratePlan'),
    eventCurrency: document.getElementById('eventCurrency'),
    eventDate: document.getElementById('eventDate'),

    // Dashboard Header
    dashCategoryBadge: document.getElementById('dashCategoryBadge'),
    dashAiSourceBadge: document.getElementById('dashAiSourceBadge'),
    dashboardEventTitle: document.getElementById('dashboardEventTitle'),
    dashDate: document.getElementById('dashDate'),
    dashLocation: document.getElementById('dashLocation'),
    dashGuests: document.getElementById('dashGuests'),
    dashBudgetTotal: document.getElementById('dashBudgetTotal'),
    dashPlanSummary: document.getElementById('dashPlanSummary'),
    btnPrintPlan: document.getElementById('btnPrintPlan'),
    btnDeleteEvent: document.getElementById('btnDeleteEvent'),

    // Dashboard Tabs
    tabBudget: document.getElementById('tabBudget'),
    tabTimeline: document.getElementById('tabTimeline'),
    tabVendors: document.getElementById('tabVendors'),
    tabIdeas: document.getElementById('tabIdeas'),
    tabTaskCount: document.getElementById('tabTaskCount'),
    tabVendorCount: document.getElementById('tabVendorCount'),
    tabIdeasCount: document.getElementById('tabIdeasCount'),

    // Tab Panels
    panelBudget: document.getElementById('panelBudget'),
    panelTimeline: document.getElementById('panelTimeline'),
    panelVendors: document.getElementById('panelVendors'),
    panelIdeas: document.getElementById('panelIdeas'),

    // Budget Tab Elements
    metricTotalBudget: document.getElementById('metricTotalBudget'),
    metricTotalAllocated: document.getElementById('metricTotalAllocated'),
    metricAllocPct: document.getElementById('metricAllocPct'),
    metricTotalActual: document.getElementById('metricTotalActual'),
    metricSpentPct: document.getElementById('metricSpentPct'),
    metricRemaining: document.getElementById('metricRemaining'),
    metricReserveNotice: document.getElementById('metricReserveNotice'),
    budgetProgressBar: document.getElementById('budgetProgressBar'),
    budgetProgressFill: document.getElementById('budgetProgressFill'),
    progressPctText: document.getElementById('progressPctText'),
    budgetWarningsContainer: document.getElementById('budgetWarningsContainer'),
    budgetTableBody: document.getElementById('budgetTableBody'),
    btnAddBudgetRow: document.getElementById('btnAddBudgetRow'),

    // Timeline Tab Elements
    timelineTasksList: document.getElementById('timelineTasksList'),
    btnAddTask: document.getElementById('btnAddTask'),
    filterButtons: [
      document.getElementById('btnFilterPendingTasks'),
      document.getElementById('btnFilterIncomplete'),
      document.getElementById('btnFilterCompleted')
    ],

    // Vendor Tab Elements
    vendorGrid: document.getElementById('vendorGrid'),
    btnAddVendor: document.getElementById('btnAddVendor'),

    // Ideas Tab Elements
    ideasGrid: document.getElementById('ideasGrid'),

    // Modals
    modalSavedEvents: document.getElementById('modalSavedEvents'),
    btnCloseSavedModal: document.getElementById('btnCloseSavedModal'),
    savedEventsListContainer: document.getElementById('savedEventsListContainer'),

    modalAddBudget: document.getElementById('modalAddBudget'),
    btnCloseAddBudget: document.getElementById('btnCloseAddBudget'),
    btnCancelAddBudget: document.getElementById('btnCancelAddBudget'),
    formAddBudget: document.getElementById('formAddBudget'),

    modalAddTask: document.getElementById('modalAddTask'),
    btnCloseAddTask: document.getElementById('btnCloseAddTask'),
    btnCancelAddTask: document.getElementById('btnCancelAddTask'),
    formAddTask: document.getElementById('formAddTask'),

    modalAddVendor: document.getElementById('modalAddVendor'),
    btnCloseAddVendor: document.getElementById('btnCloseAddVendor'),
    btnCancelAddVendor: document.getElementById('btnCancelAddVendor'),
    formAddVendor: document.getElementById('formAddVendor'),

    modalConfirm: document.getElementById('modalConfirm'),
    btnCloseConfirm: document.getElementById('btnCloseConfirm'),
    btnConfirmCancel: document.getElementById('btnConfirmCancel'),
    btnConfirmOk: document.getElementById('btnConfirmOk'),
    confirmMessageText: document.getElementById('confirmMessageText'),

    toastContainer: document.getElementById('toastContainer')
  };

  // --- Utility Helpers ---
  function formatMoney(amount, currencyCode) {
    const sym = CURRENCY_SYMBOLS[currencyCode] || currencyCode || '₹';
    const num = Math.round(Number(amount) || 0);
    return `${sym} ${num.toLocaleString()}`;
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function clearFormErrors() {
    document.querySelectorAll('.field-error').forEach(el => el.textContent = '');
  }

  function displayFormErrors(errors) {
    clearFormErrors();
    for (const [key, msg] of Object.entries(errors)) {
      const errEl = document.getElementById(`err_${key}`);
      if (errEl) {
        errEl.textContent = msg;
      } else {
        showToast(msg, 'error');
      }
    }
  }

  let confirmCallback = null;
  function showConfirm(message, onConfirm) {
    elements.confirmMessageText.textContent = message;
    confirmCallback = onConfirm;
    elements.modalConfirm.classList.add('active');
  }

  function hideConfirm() {
    elements.modalConfirm.classList.remove('active');
    confirmCallback = null;
  }

  // --- API Requests ---
  async function apiRequest(url, options = {}) {
    try {
      const defaultHeaders = { 'Content-Type': 'application/json' };
      options.headers = { ...defaultHeaders, ...options.headers };
      const res = await fetch(url, options);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Server error occurred.');
      }
      return data;
    } catch (err) {
      loggerError('API Error', err);
      throw err;
    }
  }

  function loggerError(context, err) {
    console.error(`[PlanGenie] ${context}:`, err);
  }

  // --- Initialization ---
  async function init() {
    // Set minimum date for event creation to today
    const todayStr = new Date().toISOString().split('T')[0];
    if (elements.eventDate) {
      elements.eventDate.min = todayStr;
      // Default to 45 days in future
      const defaultDate = new Date();
      defaultDate.setDate(defaultDate.getDate() + 45);
      elements.eventDate.value = defaultDate.toISOString().split('T')[0];
    }

    bindEvents();
    await loadAppConfig();
    await refreshSavedEvents();
  }

  async function loadAppConfig() {
    try {
      const res = await apiRequest('/api/config');
      state.config = res;
      if (res.ai_available) {
        elements.aiStatusText.textContent = `Live GenAI Planner Active (${res.ai_provider.toUpperCase()})`;
        elements.aiStatusNotice.style.backgroundColor = 'rgba(16, 185, 129, 0.15)';
        elements.aiStatusNotice.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        elements.aiStatusNotice.style.color = '#34d399';
      } else {
        elements.aiStatusText.textContent = 'Intelligent Rule-Based Planner Active (Offline Mode)';
        elements.aiStatusNotice.style.backgroundColor = 'rgba(99, 102, 241, 0.15)';
        elements.aiStatusNotice.style.borderColor = 'rgba(99, 102, 241, 0.4)';
        elements.aiStatusNotice.style.color = '#a5b4fc';
      }
    } catch (e) {
      elements.aiStatusText.textContent = 'Rule-Based Planning Engine Ready';
    }
  }

  async function refreshSavedEvents() {
    try {
      const res = await apiRequest('/api/events');
      if (res.success) {
        state.savedEvents = res.events || [];
        elements.savedEventsCount.textContent = state.savedEvents.length;
      }
    } catch (e) {
      loggerError('refreshSavedEvents', e);
    }
  }

  // --- Event Listeners ---
  function bindEvents() {
    // Navigation
    elements.btnNavNewEvent.addEventListener('click', showCreateEventView);
    elements.btnNavSavedEvents.addEventListener('click', openSavedEventsModal);
    elements.btnCloseSavedModal.addEventListener('click', () => elements.modalSavedEvents.classList.remove('active'));

    // Create Event Form
    elements.formEventCreate.addEventListener('submit', handleCreateEvent);
    elements.eventCurrency.addEventListener('change', (e) => {
      state.currencyCode = e.target.value;
      state.currencySymbol = CURRENCY_SYMBOLS[e.target.value] || '₹';
      updateCurrencyLabels();
    });

    // Dashboard Tabs
    elements.tabBudget.addEventListener('click', () => switchTab('panelBudget'));
    elements.tabTimeline.addEventListener('click', () => switchTab('panelTimeline'));
    elements.tabVendors.addEventListener('click', () => switchTab('panelVendors'));
    elements.tabIdeas.addEventListener('click', () => switchTab('panelIdeas'));

    // Dashboard Actions
    elements.btnPrintPlan.addEventListener('click', () => window.print());
    elements.btnDeleteEvent.addEventListener('click', handleDeleteCurrentEvent);

    // Modals Open/Close
    elements.btnAddBudgetRow.addEventListener('click', () => elements.modalAddBudget.classList.add('active'));
    elements.btnCloseAddBudget.addEventListener('click', () => elements.modalAddBudget.classList.remove('active'));
    elements.btnCancelAddBudget.addEventListener('click', () => elements.modalAddBudget.classList.remove('active'));
    elements.formAddBudget.addEventListener('submit', handleAddBudgetItem);

    elements.btnAddTask.addEventListener('click', () => {
      // Set default due date to event date or today
      const defaultDue = state.currentEvent ? state.currentEvent.event.event_date : '';
      document.getElementById('newTaskDueDate').value = defaultDue;
      elements.modalAddTask.classList.add('active');
    });
    elements.btnCloseAddTask.addEventListener('click', () => elements.modalAddTask.classList.remove('active'));
    elements.btnCancelAddTask.addEventListener('click', () => elements.modalAddTask.classList.remove('active'));
    elements.formAddTask.addEventListener('submit', handleAddTask);

    elements.btnAddVendor.addEventListener('click', () => elements.modalAddVendor.classList.add('active'));
    elements.btnCloseAddVendor.addEventListener('click', () => elements.modalAddVendor.classList.remove('active'));
    elements.btnCancelAddVendor.addEventListener('click', () => elements.modalAddVendor.classList.remove('active'));
    elements.formAddVendor.addEventListener('submit', handleAddVendor);

    // Confirmation dialog
    elements.btnCloseConfirm.addEventListener('click', hideConfirm);
    elements.btnConfirmCancel.addEventListener('click', hideConfirm);
    elements.btnConfirmOk.addEventListener('click', () => {
      if (confirmCallback) confirmCallback();
      hideConfirm();
    });

    // Timeline Filter Buttons
    elements.filterButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        elements.filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.taskFilter = btn.getAttribute('data-filter');
        renderTimelineTasks();
      });
    });

    // Close modals on clicking backdrop
    [elements.modalSavedEvents, elements.modalAddBudget, elements.modalAddTask, elements.modalAddVendor, elements.modalConfirm].forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
      });
    });
  }

  function updateCurrencyLabels() {
    document.querySelectorAll('.currencySymbol').forEach(el => {
      el.textContent = state.currencySymbol;
    });
  }

  function switchTab(panelId) {
    state.activeTab = panelId;
    [elements.panelBudget, elements.panelTimeline, elements.panelVendors, elements.panelIdeas].forEach(p => {
      p.style.display = p.id === panelId ? 'block' : 'none';
    });
    [elements.tabBudget, elements.tabTimeline, elements.tabVendors, elements.tabIdeas].forEach(btn => {
      const isTarget = btn.getAttribute('aria-controls') === panelId;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });
  }

  function showCreateEventView() {
    elements.viewCreateEvent.style.display = 'block';
    elements.viewDashboard.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showDashboardView() {
    elements.viewCreateEvent.style.display = 'none';
    elements.viewDashboard.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- Create Event Handler ---
  async function handleCreateEvent(e) {
    e.preventDefault();
    clearFormErrors();

    const selectedCategoryEl = document.querySelector('input[name="category"]:checked');
    const category = selectedCategoryEl ? selectedCategoryEl.value : 'wedding';
    const name = document.getElementById('eventName').value.trim();
    const eventDate = document.getElementById('eventDate').value;
    const location = document.getElementById('eventLocation').value.trim();
    const guests = document.getElementById('eventGuests').value;
    const budget = document.getElementById('eventBudget').value;
    const currency = document.getElementById('eventCurrency').value;

    const theme = document.getElementById('eventTheme').value.trim();
    const venueType = document.getElementById('eventVenueType').value;
    const priorities = document.getElementById('eventPriorities').value.trim();
    const dietary = document.getElementById('eventDietary').value.trim();
    const accessibility = document.getElementById('eventAccessibility').value.trim();
    const notes = document.getElementById('eventNotes').value.trim();

    // Client-side quick check
    const errors = {};
    if (!name) errors.name = 'Please enter an event name.';
    if (!eventDate) errors.event_date = 'Please select a valid event date.';
    if (!location) errors.location = 'Please enter a location.';
    if (!guests || Number(guests) < 1) errors.guests = 'Please specify guest count.';
    if (!budget || Number(budget) < 100) errors.budget = 'Please enter a valid budget (minimum 100).';

    if (Object.keys(errors).length > 0) {
      displayFormErrors(errors);
      return;
    }

    const payload = {
      name,
      category,
      event_date: eventDate,
      location,
      guests: Number(guests),
      budget: Number(budget),
      currency,
      theme,
      venue_type: venueType,
      priorities,
      dietary,
      accessibility,
      notes
    };

    // Show loading state
    elements.btnGeneratePlan.disabled = true;
    elements.btnGeneratePlan.querySelector('.btn-text').style.display = 'none';
    elements.btnGeneratePlan.querySelector('.btn-spinner').classList.remove('hidden');

    try {
      const res = await apiRequest('/api/events', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (res.success) {
        state.currentEvent = res.data;
        state.currencyCode = res.data.event.currency;
        state.currencySymbol = CURRENCY_SYMBOLS[state.currencyCode] || '₹';
        updateCurrencyLabels();
        
        await refreshSavedEvents();
        renderDashboard();
        showDashboardView();
        
        const sourceLabel = res.ai_source === 'live_genai' ? 'Live GenAI' : 'Intelligent Rule-Based Engine';
        showToast(`Event plan generated successfully via ${sourceLabel}!`, 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to generate event plan.', 'error');
    } finally {
      elements.btnGeneratePlan.disabled = false;
      elements.btnGeneratePlan.querySelector('.btn-text').style.display = 'inline-flex';
      elements.btnGeneratePlan.querySelector('.btn-spinner').classList.add('hidden');
    }
  }

  // --- Render Dashboard ---
  function renderDashboard() {
    if (!state.currentEvent) return;

    const ev = state.currentEvent.event;
    const budgetSummary = state.currentEvent.budget_summary;
    const tasks = state.currentEvent.tasks || [];
    const vendors = state.currentEvent.vendors || [];
    const ideas = state.currentEvent.ideas || [];

    // Header info
    elements.dashboardEventTitle.textContent = ev.name;
    elements.dashCategoryBadge.textContent = ev.category.toUpperCase();
    
    // AI source badge
    if (ev.ai_source === 'live_genai') {
      elements.dashAiSourceBadge.textContent = 'Live GenAI Plan';
      elements.dashAiSourceBadge.className = 'badge badge-ai';
    } else {
      elements.dashAiSourceBadge.textContent = 'Intelligent Fallback Engine';
      elements.dashAiSourceBadge.className = 'badge badge-cat';
    }

    elements.dashDate.textContent = ev.event_date;
    elements.dashLocation.textContent = ev.location;
    elements.dashGuests.textContent = `${ev.guests} Guests`;
    elements.dashBudgetTotal.textContent = formatMoney(ev.budget, ev.currency);
    elements.dashPlanSummary.textContent = ev.plan_summary || 'Comprehensive personalized event roadmap.';

    // Tab counters
    elements.tabTaskCount.textContent = tasks.length;
    elements.tabVendorCount.textContent = vendors.length;
    elements.tabIdeasCount.textContent = ideas.length;

    // Render Sub-Sections
    renderBudgetSection();
    renderTimelineTasks();
    renderVendors();
    renderIdeas();
  }

  // --- Render Budget Section ---
  function renderBudgetSection() {
    const summary = state.currentEvent.budget_summary;
    const items = state.currentEvent.budget || [];
    const currency = state.currentEvent.event.currency;

    elements.metricTotalBudget.textContent = formatMoney(summary.total_budget, currency);
    elements.metricTotalAllocated.textContent = formatMoney(summary.total_estimated, currency);
    elements.metricAllocPct.textContent = `${summary.allocation_pct}% allocated`;

    elements.metricTotalActual.textContent = formatMoney(summary.total_actual, currency);
    elements.metricSpentPct.textContent = `${summary.actual_utilization_pct}% utilized`;

    elements.metricRemaining.textContent = formatMoney(summary.remaining_balance, currency);
    elements.metricReserveNotice.textContent = `Unallocated reserve: ${formatMoney(summary.unallocated_reserve, currency)}`;

    // Highlight negative remaining balance
    if (summary.remaining_balance < 0) {
      elements.metricRemaining.style.color = '#ef4444';
    } else {
      elements.metricRemaining.style.color = '#f8fafc';
    }

    // Progress bar
    const utilPct = Math.min(100, Math.max(0, summary.utilization_pct));
    elements.budgetProgressFill.style.width = `${utilPct}%`;
    elements.progressPctText.textContent = `${summary.actual_utilization_pct}% spent of total budget`;

    if (summary.is_over_budget) {
      elements.budgetProgressFill.classList.add('over-budget');
    } else {
      elements.budgetProgressFill.classList.remove('over-budget');
    }

    // Warnings
    elements.budgetWarningsContainer.replaceChildren();
    if (summary.warnings && summary.warnings.length > 0) {
      elements.budgetWarningsContainer.style.display = 'block';
      const warningTitle = document.createElement('strong');
      warningTitle.textContent = 'Budget Alerts:';
      elements.budgetWarningsContainer.appendChild(warningTitle);
      
      const ul = document.createElement('ul');
      summary.warnings.forEach(w => {
        const li = document.createElement('li');
        li.textContent = w;
        ul.appendChild(li);
      });
      elements.budgetWarningsContainer.appendChild(ul);
    } else {
      elements.budgetWarningsContainer.style.display = 'none';
    }

    // Table rows
    elements.budgetTableBody.replaceChildren();
    items.forEach(item => {
      const tr = document.createElement('tr');

      // Category
      const tdCat = document.createElement('td');
      tdCat.style.fontWeight = '600';
      tdCat.textContent = item.category;
      tr.appendChild(tdCat);

      // Priority
      const tdPriority = document.createElement('td');
      const tag = document.createElement('span');
      tag.className = `priority-tag priority-${item.priority || 'medium'}`;
      tag.textContent = item.priority || 'essential';
      tdPriority.appendChild(tag);
      tr.appendChild(tdPriority);

      // Estimated
      const tdEst = document.createElement('td');
      tdEst.textContent = formatMoney(item.estimated_amount, currency);
      tr.appendChild(tdEst);

      // Actual Spent (Inline editable input)
      const tdAct = document.createElement('td');
      const actInput = document.createElement('input');
      actInput.type = 'number';
      actInput.min = '0';
      actInput.className = 'inline-edit-input';
      actInput.value = item.actual_amount;
      actInput.setAttribute('aria-label', `Actual spent for ${item.category}`);
      actInput.addEventListener('change', async (e) => {
        await handleUpdateBudgetActual(item.id, e.target.value);
      });
      tdAct.appendChild(actInput);
      tr.appendChild(tdAct);

      // Notes / Details
      const tdNotes = document.createElement('td');
      tdNotes.className = 'card-desc';
      tdNotes.textContent = item.notes || '—';
      tr.appendChild(tdNotes);

      // Delete action
      const tdActions = document.createElement('td');
      tdActions.style.textAlign = 'center';
      const btnDel = document.createElement('button');
      btnDel.className = 'btn btn-ghost btn-sm';
      btnDel.setAttribute('aria-label', `Delete category ${item.category}`);
      btnDel.textContent = '✕';
      btnDel.addEventListener('click', () => {
        showConfirm(`Delete category "${item.category}"?`, () => handleDeleteBudgetItem(item.id));
      });
      tdActions.appendChild(btnDel);
      tr.appendChild(tdActions);

      elements.budgetTableBody.appendChild(tr);
    });
  }

  async function handleUpdateBudgetActual(itemId, newActual) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/budget/${itemId}`, {
        method: 'PATCH',
        body: JSON.stringify({ actual_amount: Number(newActual) })
      });
      if (res.success) {
        state.currentEvent.budget = res.budget_items;
        state.currentEvent.budget_summary = res.budget_summary;
        renderBudgetSection();
        showToast('Actual expense updated.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to update expense.', 'error');
    }
  }

  async function handleAddBudgetItem(e) {
    e.preventDefault();
    if (!state.currentEvent) return;

    const category = document.getElementById('newBudgetCat').value.trim();
    const est = document.getElementById('newBudgetEst').value || 0;
    const priority = document.getElementById('newBudgetPriority').value;
    const notes = document.getElementById('newBudgetNotes').value.trim();

    if (!category) return;

    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/budget`, {
        method: 'POST',
        body: JSON.stringify({
          category,
          estimated_amount: Number(est),
          actual_amount: 0,
          priority,
          notes
        })
      });

      if (res.success) {
        state.currentEvent.budget = res.budget_items;
        state.currentEvent.budget_summary = res.budget_summary;
        renderBudgetSection();
        elements.modalAddBudget.classList.remove('active');
        elements.formAddBudget.reset();
        showToast('Budget category added.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to add budget category.', 'error');
    }
  }

  async function handleDeleteBudgetItem(itemId) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/budget/${itemId}`, {
        method: 'DELETE'
      });
      if (res.success) {
        state.currentEvent.budget = res.budget_items;
        state.currentEvent.budget_summary = res.budget_summary;
        renderBudgetSection();
        showToast('Budget category deleted.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete budget item.', 'error');
    }
  }

  // --- Render Timeline Tasks ---
  function renderTimelineTasks() {
    const tasks = state.currentEvent.tasks || [];
    elements.timelineTasksList.replaceChildren();

    const filtered = tasks.filter(t => {
      if (state.taskFilter === 'pending') return !t.is_completed;
      if (state.taskFilter === 'completed') return t.is_completed;
      return true;
    });

    if (filtered.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'card-desc';
      emptyDiv.style.padding = '2rem';
      emptyDiv.style.textAlign = 'center';
      emptyDiv.textContent = state.taskFilter === 'all'
        ? 'No tasks in this schedule yet. Click "+ Add Task" to schedule one.'
        : `No ${state.taskFilter} tasks found.`;
      elements.timelineTasksList.appendChild(emptyDiv);
      return;
    }

    filtered.forEach(task => {
      const card = document.createElement('div');
      card.className = `task-card ${task.is_completed ? 'completed' : ''} ${task.is_overdue ? 'overdue' : ''}`;

      // Checkbox
      const checkWrap = document.createElement('div');
      checkWrap.className = 'task-checkbox-wrap';
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.className = 'task-checkbox';
      cb.checked = Boolean(task.is_completed);
      cb.setAttribute('aria-label', `Mark "${task.title}" as complete`);
      cb.addEventListener('change', async () => {
        await handleToggleTask(task.id, cb.checked);
      });
      checkWrap.appendChild(cb);
      card.appendChild(checkWrap);

      // Task Body
      const main = document.createElement('div');
      main.className = 'task-main';

      const headerRow = document.createElement('div');
      headerRow.className = 'task-header-row';

      const title = document.createElement('span');
      title.className = 'task-title';
      title.textContent = task.title;
      headerRow.appendChild(title);

      const priorityTag = document.createElement('span');
      priorityTag.className = `priority-tag priority-${task.priority}`;
      priorityTag.textContent = task.priority;
      headerRow.appendChild(priorityTag);

      if (task.category) {
        const catTag = document.createElement('span');
        catTag.className = 'priority-tag';
        catTag.style.backgroundColor = 'var(--bg-input)';
        catTag.textContent = task.category;
        headerRow.appendChild(catTag);
      }

      main.appendChild(headerRow);

      if (task.description) {
        const desc = document.createElement('p');
        desc.className = 'task-desc';
        desc.textContent = task.description;
        main.appendChild(desc);
      }

      const footerMeta = document.createElement('div');
      footerMeta.className = 'task-footer-meta';

      const dueSpan = document.createElement('span');
      dueSpan.className = `due-tag ${task.is_overdue ? 'overdue' : ''}`;
      dueSpan.textContent = task.is_overdue
        ? `Overdue (${task.due_date})`
        : `Target Due: ${task.due_date}`;
      footerMeta.appendChild(dueSpan);

      main.appendChild(footerMeta);
      card.appendChild(main);

      // Delete Button
      const btnDel = document.createElement('button');
      btnDel.className = 'btn btn-ghost btn-sm';
      btnDel.setAttribute('aria-label', `Delete task "${task.title}"`);
      btnDel.textContent = '✕';
      btnDel.addEventListener('click', () => {
        showConfirm(`Delete task "${task.title}"?`, () => handleDeleteTask(task.id));
      });
      card.appendChild(btnDel);

      elements.timelineTasksList.appendChild(card);
    });
  }

  async function handleToggleTask(taskId, isCompleted) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_completed: isCompleted })
      });
      if (res.success) {
        state.currentEvent.tasks = res.tasks;
        renderTimelineTasks();
      }
    } catch (err) {
      showToast(err.message || 'Failed to update task status.', 'error');
    }
  }

  async function handleAddTask(e) {
    e.preventDefault();
    if (!state.currentEvent) return;

    const title = document.getElementById('newTaskTitle').value.trim();
    const description = document.getElementById('newTaskDesc').value.trim();
    const dueDate = document.getElementById('newTaskDueDate').value;
    const priority = document.getElementById('newTaskPriority').value;

    if (!title || !dueDate) return;

    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/tasks`, {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          due_date: dueDate,
          priority,
          category: 'Custom'
        })
      });

      if (res.success) {
        state.currentEvent.tasks = res.tasks;
        elements.tabTaskCount.textContent = res.tasks.length;
        renderTimelineTasks();
        elements.modalAddTask.classList.remove('active');
        elements.formAddTask.reset();
        showToast('Timeline task created.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to create task.', 'error');
    }
  }

  async function handleDeleteTask(taskId) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/tasks/${taskId}`, {
        method: 'DELETE'
      });
      if (res.success) {
        state.currentEvent.tasks = res.tasks;
        elements.tabTaskCount.textContent = res.tasks.length;
        renderTimelineTasks();
        showToast('Task deleted.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete task.', 'error');
    }
  }

  // --- Render Vendors Section ---
  function renderVendors() {
    const vendors = state.currentEvent.vendors || [];
    elements.vendorGrid.replaceChildren();

    if (vendors.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'card-desc';
      emptyDiv.style.padding = '2rem';
      emptyDiv.style.textAlign = 'center';
      emptyDiv.textContent = 'No vendor items added yet. Click "+ Add Vendor" to add one.';
      elements.vendorGrid.appendChild(emptyDiv);
      return;
    }

    vendors.forEach(v => {
      const card = document.createElement('div');
      card.className = 'vendor-card';

      const top = document.createElement('div');
      top.className = 'vc-top';

      const titleBlock = document.createElement('div');
      const cat = document.createElement('span');
      cat.className = 'vc-cat';
      cat.textContent = v.category;
      titleBlock.appendChild(cat);

      const title = document.createElement('h3');
      title.className = 'vc-title';
      title.textContent = v.title;
      titleBlock.appendChild(title);

      top.appendChild(titleBlock);

      const btnDel = document.createElement('button');
      btnDel.className = 'btn btn-ghost btn-sm';
      btnDel.setAttribute('aria-label', `Delete vendor "${v.title}"`);
      btnDel.textContent = '✕';
      btnDel.addEventListener('click', () => {
        showConfirm(`Delete vendor entry "${v.title}"?`, () => handleDeleteVendor(v.id));
      });
      top.appendChild(btnDel);

      card.appendChild(top);

      if (v.description) {
        const desc = document.createElement('p');
        desc.className = 'vc-desc';
        desc.textContent = v.description;
        card.appendChild(desc);
      }

      if (v.notes) {
        const notesBox = document.createElement('div');
        notesBox.className = 'vc-notes-box';
        notesBox.textContent = `Notes / Criteria: ${v.notes}`;
        card.appendChild(notesBox);
      }

      const actionsRow = document.createElement('div');
      actionsRow.className = 'vc-actions-row';

      const statusSelect = document.createElement('select');
      statusSelect.className = 'status-select';
      statusSelect.setAttribute('aria-label', `Status for ${v.title}`);
      const statuses = [
        { val: 'not_contacted', text: 'Not Contacted' },
        { val: 'in_discussion', text: 'In Discussion' },
        { val: 'quote_received', text: 'Quote Received' },
        { val: 'hired', text: 'Hired' },
        { val: 'completed', text: 'Completed' }
      ];
      statuses.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.val;
        opt.textContent = s.text;
        if (s.val === v.status) opt.selected = true;
        statusSelect.appendChild(opt);
      });

      statusSelect.addEventListener('change', async (e) => {
        await handleUpdateVendorStatus(v.id, e.target.value);
      });
      actionsRow.appendChild(statusSelect);

      card.appendChild(actionsRow);
      elements.vendorGrid.appendChild(card);
    });
  }

  async function handleUpdateVendorStatus(vendorId, newStatus) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/vendors/${vendorId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus })
      });
      if (res.success) {
        state.currentEvent.vendors = res.vendors;
        showToast('Vendor status updated.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to update vendor status.', 'error');
    }
  }

  async function handleAddVendor(e) {
    e.preventDefault();
    if (!state.currentEvent) return;

    const title = document.getElementById('newVendorTitle').value.trim();
    const category = document.getElementById('newVendorCat').value.trim() || 'General';
    const status = document.getElementById('newVendorStatus').value;
    const description = document.getElementById('newVendorDesc').value.trim();
    const notes = document.getElementById('newVendorNotes').value.trim();

    if (!title) return;

    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/vendors`, {
        method: 'POST',
        body: JSON.stringify({
          title,
          category,
          status,
          description,
          notes
        })
      });

      if (res.success) {
        state.currentEvent.vendors = res.vendors;
        elements.tabVendorCount.textContent = res.vendors.length;
        renderVendors();
        elements.modalAddVendor.classList.remove('active');
        elements.formAddVendor.reset();
        showToast('Vendor added to directory.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to add vendor.', 'error');
    }
  }

  async function handleDeleteVendor(vendorId) {
    if (!state.currentEvent) return;
    try {
      const res = await apiRequest(`/api/events/${state.currentEvent.event.id}/vendors/${vendorId}`, {
        method: 'DELETE'
      });
      if (res.success) {
        state.currentEvent.vendors = res.vendors;
        elements.tabVendorCount.textContent = res.vendors.length;
        renderVendors();
        showToast('Vendor deleted.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete vendor.', 'error');
    }
  }

  // --- Render Personalized Ideas Section ---
  function renderIdeas() {
    const ideas = state.currentEvent.ideas || [];
    elements.ideasGrid.replaceChildren();

    if (ideas.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'card-desc';
      emptyDiv.style.padding = '2rem';
      emptyDiv.style.textAlign = 'center';
      emptyDiv.textContent = 'No personalized ideas found for this event.';
      elements.ideasGrid.appendChild(emptyDiv);
      return;
    }

    ideas.forEach(idea => {
      const card = document.createElement('div');
      card.className = 'idea-card';

      const badge = document.createElement('span');
      badge.className = 'idea-badge';
      badge.textContent = (idea.category || 'Concept').toUpperCase();
      card.appendChild(badge);

      const title = document.createElement('h3');
      title.className = 'idea-title';
      title.textContent = idea.title;
      card.appendChild(title);

      const desc = document.createElement('p');
      desc.className = 'idea-desc';
      desc.textContent = idea.description;
      card.appendChild(desc);

      if (idea.rationale) {
        const rat = document.createElement('div');
        rat.className = 'idea-rationale';
        rat.textContent = `Why this suits your event: ${idea.rationale}`;
        card.appendChild(rat);
      }

      elements.ideasGrid.appendChild(card);
    });
  }

  // --- Saved Events Modal Management ---
  async function openSavedEventsModal() {
    await refreshSavedEvents();
    elements.savedEventsListContainer.replaceChildren();

    if (state.savedEvents.length === 0) {
      const emptyNotice = document.createElement('div');
      emptyNotice.className = 'card-desc';
      emptyNotice.style.padding = '3rem 1rem';
      emptyNotice.style.textAlign = 'center';
      emptyNotice.textContent = 'No saved event plans yet. Fill out the event creation form to build your first plan!';
      elements.savedEventsListContainer.appendChild(emptyNotice);
    } else {
      state.savedEvents.forEach(ev => {
        const card = document.createElement('div');
        card.className = 'saved-event-card';

        const top = document.createElement('div');
        const badge = document.createElement('span');
        badge.className = 'badge badge-cat';
        badge.style.marginBottom = '0.5rem';
        badge.style.display = 'inline-block';
        badge.textContent = ev.category.toUpperCase();
        top.appendChild(badge);

        const title = document.createElement('h3');
        title.className = 'sec-title';
        title.textContent = ev.name;
        top.appendChild(title);

        const meta = document.createElement('div');
        meta.className = 'sec-meta';
        meta.textContent = `📅 ${ev.event_date} | 📍 ${ev.location} | 👥 ${ev.guests} guests`;
        top.appendChild(meta);

        const finMeta = document.createElement('div');
        finMeta.className = 'sec-meta';
        finMeta.style.marginTop = '0.25rem';
        finMeta.textContent = `💰 Budget: ${formatMoney(ev.budget, ev.currency)} (Spent: ${formatMoney(ev.total_actual, ev.currency)})`;
        top.appendChild(finMeta);

        card.appendChild(top);

        const actions = document.createElement('div');
        actions.className = 'sec-actions';

        const btnOpen = document.createElement('button');
        btnOpen.className = 'btn btn-primary btn-sm';
        btnOpen.textContent = 'Open Plan';
        btnOpen.addEventListener('click', async () => {
          elements.modalSavedEvents.classList.remove('active');
          await loadEventById(ev.id);
        });
        actions.appendChild(btnOpen);

        const btnDel = document.createElement('button');
        btnDel.className = 'btn btn-danger btn-sm';
        btnDel.textContent = 'Delete';
        btnDel.addEventListener('click', () => {
          showConfirm(`Are you sure you want to delete "${ev.name}"? This cannot be undone.`, async () => {
            await deleteEventById(ev.id);
            await openSavedEventsModal();
          });
        });
        actions.appendChild(btnDel);

        card.appendChild(actions);
        elements.savedEventsListContainer.appendChild(card);
      });
    }

    elements.modalSavedEvents.classList.add('active');
  }

  async function loadEventById(eventId) {
    try {
      const res = await apiRequest(`/api/events/${eventId}`);
      if (res.success) {
        state.currentEvent = res.data;
        state.currencyCode = res.data.event.currency;
        state.currencySymbol = CURRENCY_SYMBOLS[state.currencyCode] || '₹';
        updateCurrencyLabels();
        renderDashboard();
        showDashboardView();
        showToast(`Loaded plan for ${res.data.event.name}`, 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to load event plan.', 'error');
    }
  }

  async function deleteEventById(eventId) {
    try {
      const res = await apiRequest(`/api/events/${eventId}`, { method: 'DELETE' });
      if (res.success) {
        await refreshSavedEvents();
        if (state.currentEvent && state.currentEvent.event.id === eventId) {
          state.currentEvent = null;
          showCreateEventView();
        }
        showToast('Event plan deleted.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete event.', 'error');
    }
  }

  function handleDeleteCurrentEvent() {
    if (!state.currentEvent) return;
    const name = state.currentEvent.event.name;
    const id = state.currentEvent.event.id;
    showConfirm(`Are you sure you want to delete "${name}"?`, async () => {
      await deleteEventById(id);
    });
  }

  // --- Bootstrap on DOM Ready ---
  document.addEventListener('DOMContentLoaded', init);

})();
