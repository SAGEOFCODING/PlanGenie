/**
 * PlanGenie - GenAI-Powered Event Planning Assistant
 * Terra Organic Design ("Rooted Warmth") Application Logic
 * Pure Vanilla JavaScript with zero external framework dependencies.
 * Uses strict DOM manipulation with textContent to eliminate XSS risks.
 */

(function () {
  'use strict';

  // --- Currency Configuration ---
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

  // --- Application State ---
  const state = {
    currentEvent: null,
    savedEvents: [],
    config: null,
    currentView: 'viewTimeline',
    taskFilter: 'all',
    currencySymbol: '₹',
    currencyCode: 'INR'
  };

  // --- DOM Elements Cache ---
  const elements = {
    // Top Bar & Logo
    btnLogoHome: document.getElementById('btnLogoHome'),
    omniSearchInput: document.getElementById('omniSearchInput'),
    btnHeaderNewEvent: document.getElementById('btnHeaderNewEvent'),
    btnHeaderPrint: document.getElementById('btnHeaderPrint'),
    headerCurrentCat: document.getElementById('headerCurrentCat'),

    // Left Sidebar Elements
    sidebarActiveEventCard: document.getElementById('sidebarActiveEventCard'),
    sidebarCatIcon: document.getElementById('sidebarCatIcon'),
    sidebarEventTitle: document.getElementById('sidebarEventTitle'),
    sidebarEventMeta: document.getElementById('sidebarEventMeta'),
    sidebarSavedCount: document.getElementById('sidebarSavedCount'),
    aiCopilotStatus: document.getElementById('aiCopilotStatus'),
    aiCopilotBadge: document.getElementById('aiCopilotBadge'),
    aiCopilotSub: document.getElementById('aiCopilotSub'),

    // Sidebar Navigation Buttons
    navItemOverview: document.getElementById('navItemOverview'),
    navItemTimeline: document.getElementById('navItemTimeline'),
    navItemBudget: document.getElementById('navItemBudget'),
    navItemVendors: document.getElementById('navItemVendors'),
    navItemIdeas: document.getElementById('navItemIdeas'),
    navItemSaved: document.getElementById('navItemSaved'),

    // Main View Sections
    viewCreateEvent: document.getElementById('viewCreateEvent'),
    viewTimeline: document.getElementById('viewTimeline'),
    viewBudget: document.getElementById('viewBudget'),
    viewVendors: document.getElementById('viewVendors'),
    viewIdeas: document.getElementById('viewIdeas'),
    viewOverview: document.getElementById('viewOverview'),

    // Event Creation Form
    formEventCreate: document.getElementById('formEventCreate'),
    btnCancelCreate: document.getElementById('btnCancelCreate'),
    btnGeneratePlan: document.getElementById('btnGeneratePlan'),
    btnGenText: document.getElementById('btnGenText'),
    btnGenSpinner: document.getElementById('btnGenSpinner'),
    eventCurrency: document.getElementById('eventCurrency'),
    eventDate: document.getElementById('eventDate'),

    // Timeline View Controls
    dashCountdown: document.getElementById('dashCountdown'),
    btnOpenAddTaskModal: document.getElementById('btnOpenAddTaskModal'),
    btnAutoSequence: document.getElementById('btnAutoSequence'),
    btnDismissAiBar: document.getElementById('btnDismissAiBar'),
    btnResolveAiBar: document.getElementById('btnResolveAiBar'),
    pbTitle: document.getElementById('pbTitle'),
    pbStatus: document.getElementById('pbStatus'),
    pbBottleneck: document.getElementById('pbBottleneck'),
    phasesContainer: document.getElementById('phasesContainer'),
    runOfShowTrack: document.getElementById('runOfShowTrack'),
    rosDateDisplay: document.getElementById('rosDateDisplay'),
    btnExpandCueSheet: document.getElementById('btnExpandCueSheet'),
    widgetWeatherText: document.getElementById('widgetWeatherText'),
    filterAll: document.getElementById('filterAll'),
    filterPending: document.getElementById('filterPending'),
    filterCompleted: document.getElementById('filterCompleted'),
    btnViewGantt: document.getElementById('btnViewGantt'),
    btnViewCards: document.getElementById('btnViewCards'),
    btnViewDayOf: document.getElementById('btnViewDayOf'),
    btnViewCritical: document.getElementById('btnViewCritical'),

    // Budget View Controls
    btnOpenAddBudgetModal: document.getElementById('btnOpenAddBudgetModal'),
    metricTotalBudget: document.getElementById('metricTotalBudget'),
    metricTotalAllocated: document.getElementById('metricTotalAllocated'),
    metricAllocPct: document.getElementById('metricAllocPct'),
    metricTotalActual: document.getElementById('metricTotalActual'),
    metricSpentPct: document.getElementById('metricSpentPct'),
    metricRemaining: document.getElementById('metricRemaining'),
    metricReserveNotice: document.getElementById('metricReserveNotice'),
    budgetProgressFill: document.getElementById('budgetProgressFill'),
    progressPctText: document.getElementById('progressPctText'),
    budgetWarningsContainer: document.getElementById('budgetWarningsContainer'),
    budgetTableBody: document.getElementById('budgetTableBody'),

    // Vendor View Controls
    btnOpenAddVendorModal: document.getElementById('btnOpenAddVendorModal'),
    vendorGrid: document.getElementById('vendorGrid'),

    // Ideas View Controls
    ideasGrid: document.getElementById('ideasGrid'),

    // Overview View Controls
    overviewEventName: document.getElementById('overviewEventName'),
    overviewSummaryText: document.getElementById('overviewSummaryText'),
    overviewAiBadge: document.getElementById('overviewAiBadge'),
    ovMetricCat: document.getElementById('ovMetricCat'),
    ovMetricDate: document.getElementById('ovMetricDate'),
    ovMetricGuests: document.getElementById('ovMetricGuests'),
    ovMetricBudget: document.getElementById('ovMetricBudget'),
    btnOverviewEdit: document.getElementById('btnOverviewEdit'),
    btnOverviewDelete: document.getElementById('btnOverviewDelete'),

    // Modals
    modalSavedEvents: document.getElementById('modalSavedEvents'),
    btnCloseSavedModal: document.getElementById('btnCloseSavedModal'),
    savedEventsListContainer: document.getElementById('savedEventsListContainer'),

    modalAddTask: document.getElementById('modalAddTask'),
    btnCloseAddTask: document.getElementById('btnCloseAddTask'),
    btnCancelAddTask: document.getElementById('btnCancelAddTask'),
    formAddTask: document.getElementById('formAddTask'),

    modalAddBudget: document.getElementById('modalAddBudget'),
    btnCloseAddBudget: document.getElementById('btnCloseAddBudget'),
    btnCancelAddBudget: document.getElementById('btnCancelAddBudget'),
    formAddBudget: document.getElementById('formAddBudget'),

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
    if (!elements.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }

  function clearFormErrors() {
    document.querySelectorAll('[id^="err_"]').forEach(el => el.textContent = '');
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
    if (!elements.modalConfirm) return;
    elements.confirmMessageText.textContent = message;
    confirmCallback = onConfirm;
    elements.modalConfirm.classList.add('active');
  }

  function hideConfirm() {
    if (!elements.modalConfirm) return;
    elements.modalConfirm.classList.remove('active');
    confirmCallback = null;
  }

  // --- API Client ---
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
      console.error(`[PlanGenie] API Error (${url}):`, err);
      throw err;
    }
  }

  // --- Navigation & View Switching (Terra Styling) ---
  const NAV_ITEMS = [
    { btn: elements.navItemOverview, view: elements.viewOverview, id: 'overview' },
    { btn: elements.navItemTimeline, view: elements.viewTimeline, id: 'timeline' },
    { btn: elements.navItemBudget, view: elements.viewBudget, id: 'budget' },
    { btn: elements.navItemVendors, view: elements.viewVendors, id: 'vendors' },
    { btn: elements.navItemIdeas, view: elements.viewIdeas, id: 'ideas' }
  ];

  function setActiveView(targetId) {
    state.currentView = targetId;

    const views = [
      elements.viewCreateEvent,
      elements.viewTimeline,
      elements.viewBudget,
      elements.viewVendors,
      elements.viewIdeas,
      elements.viewOverview
    ];

    views.forEach(v => {
      if (v) v.style.display = 'none';
    });

    if (targetId === 'create') {
      if (elements.viewCreateEvent) elements.viewCreateEvent.style.display = 'block';
      NAV_ITEMS.forEach(item => {
        if (item.btn) {
          item.btn.className = "flex items-center gap-3 px-4 py-2.5 rounded-[12px] text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-all text-sm font-semibold text-left w-full";
        }
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    NAV_ITEMS.forEach(item => {
      if (!item.btn || !item.view) return;
      if (item.id === targetId) {
        item.view.style.display = 'block';
        item.btn.className = "flex items-center gap-3 px-4 py-2.5 rounded-[12px] bg-surface-container text-primary border-l-4 border-primary text-sm font-bold text-left w-full shadow-terra-subtle";
      } else {
        item.btn.className = "flex items-center gap-3 px-4 py-2.5 rounded-[12px] text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low transition-all text-sm font-semibold text-left w-full";
      }
    });

    // Update Semantic Breadcrumbs Label
    const breadcrumb = document.getElementById('breadcrumbActiveView');
    if (breadcrumb) {
      const titles = {
        'timeline': 'Timeline Engine',
        'overview': 'Overview & Hub',
        'budget': 'Smart Budgeting',
        'vendors': 'Vendor Deck',
        'ideas': 'AI Ideation Studio',
        'create': 'Event Specification'
      };
      breadcrumb.textContent = titles[targetId] || 'Event Workspace';
    }

    // Auto-close mobile drawer when navigation item is clicked
    const drawer = document.getElementById('sidebarDrawer');
    if (drawer && window.innerWidth < 1024) {
      drawer.classList.add('-translate-x-full');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- Application Initialization ---
  async function init() {
    const todayStr = new Date().toISOString().split('T')[0];
    if (elements.eventDate) {
      elements.eventDate.min = todayStr;
      const defaultDate = new Date();
      defaultDate.setDate(defaultDate.getDate() + 120);
      elements.eventDate.value = defaultDate.toISOString().split('T')[0];
    }

    bindEventListeners();
    await loadAppConfig();
    await loadInitialOrSavedEvent();
  }

  async function loadAppConfig() {
    try {
      const res = await apiRequest('/api/config');
      state.config = res;
      if (elements.aiCopilotBadge) {
        elements.aiCopilotBadge.textContent = res.ai_available ? `GenAI Live (${res.ai_provider.toUpperCase()})` : 'Offline Mode';
      }
      if (elements.aiCopilotStatus) {
        elements.aiCopilotStatus.textContent = res.ai_available ? 'Copilot Active' : 'Planner Engine Ready';
      }
    } catch (e) {
      console.warn('App config unavailable, using defaults');
    }
  }

  async function loadInitialOrSavedEvent() {
    try {
      await refreshSavedEvents();
      if (state.savedEvents.length > 0) {
        await loadEventById(state.savedEvents[0].id);
      } else {
        await seedDemoEvent();
      }
    } catch (e) {
      console.error('Failed to load initial event:', e);
      setActiveView('create');
    }
  }

  async function seedDemoEvent() {
    const demoPayload = {
      name: "Elena & Julian's Wedding",
      category: "wedding",
      event_date: "2026-10-18",
      location: "Villa Bellisima, Tuscany",
      guests: 160,
      budget: 8500000,
      currency: "INR",
      theme: "Rooted Warmth & Botanical Courtyard Elegance",
      venue_type: "hybrid",
      priorities: "Michelin-tier culinary tasting, candid twilight cinematography, lush botanical floral styling",
      dietary: "Organic farm-to-table, vegan options, sommelier wine pairing, Italian prosecco bar",
      accessibility: "Smooth garden ramps for orangery pavilion, shaded lounge seating for elders",
      notes: "10 PM courtyard curfew, strict zero single-use plastic, custom twilight lighting rig"
    };

    try {
      const res = await apiRequest('/api/events', {
        method: 'POST',
        body: JSON.stringify(demoPayload)
      });
      if (res.success) {
        state.currentEvent = res.data;
        state.currencyCode = res.data.event.currency;
        state.currencySymbol = CURRENCY_SYMBOLS[state.currencyCode] || '₹';
        updateCurrencyLabels();
        await refreshSavedEvents();
        renderAllViews();
        setActiveView('timeline');
      }
    } catch (err) {
      console.error('Demo event seeding failed:', err);
      setActiveView('create');
    }
  }

  async function refreshSavedEvents() {
    try {
      const res = await apiRequest('/api/events');
      if (res.success) {
        state.savedEvents = res.events || [];
        if (elements.sidebarSavedCount) {
          elements.sidebarSavedCount.textContent = state.savedEvents.length;
        }
      }
    } catch (e) {
      console.error('refreshSavedEvents error:', e);
    }
  }

  // --- Event Listeners Binding ---
  function bindEventListeners() {
    if (elements.navItemOverview) elements.navItemOverview.addEventListener('click', () => setActiveView('overview'));
    if (elements.navItemTimeline) elements.navItemTimeline.addEventListener('click', () => setActiveView('timeline'));
    if (elements.navItemBudget) elements.navItemBudget.addEventListener('click', () => setActiveView('budget'));
    if (elements.navItemVendors) elements.navItemVendors.addEventListener('click', () => setActiveView('vendors'));
    if (elements.navItemIdeas) elements.navItemIdeas.addEventListener('click', () => setActiveView('ideas'));

    if (elements.sidebarActiveEventCard) elements.sidebarActiveEventCard.addEventListener('click', openSavedEventsModal);
    if (elements.navItemSaved) elements.navItemSaved.addEventListener('click', openSavedEventsModal);
    if (elements.btnCloseSavedModal) elements.btnCloseSavedModal.addEventListener('click', () => elements.modalSavedEvents.classList.remove('active'));

    if (elements.btnLogoHome) elements.btnLogoHome.addEventListener('click', () => setActiveView('timeline'));
    if (elements.btnHeaderNewEvent) elements.btnHeaderNewEvent.addEventListener('click', () => setActiveView('create'));
    if (elements.btnCancelCreate) elements.btnCancelCreate.addEventListener('click', () => setActiveView('timeline'));
    if (elements.btnHeaderPrint) elements.btnHeaderPrint.addEventListener('click', () => window.print());

    // Mobile Drawer Toggle
    const btnMobileToggle = document.getElementById('btnMobileMenuToggle');
    const btnMobileClose = document.getElementById('btnMobileCloseDrawer');
    const sidebarDrawer = document.getElementById('sidebarDrawer');
    if (btnMobileToggle && sidebarDrawer) {
      btnMobileToggle.addEventListener('click', () => {
        sidebarDrawer.classList.toggle('-translate-x-full');
      });
    }
    if (btnMobileClose && sidebarDrawer) {
      btnMobileClose.addEventListener('click', () => {
        sidebarDrawer.classList.add('-translate-x-full');
      });
    }

    if (elements.omniSearchInput) {
      elements.omniSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const query = elements.omniSearchInput.value.trim().toLowerCase();
          if (!query) return;
          if (query.includes('budget') || query.includes('money') || query.includes('cost')) {
            setActiveView('budget');
            showToast('Navigated to Smart Budgeting', 'info');
          } else if (query.includes('vendor') || query.includes('cater') || query.includes('photo')) {
            setActiveView('vendors');
            showToast('Navigated to Vendor Deck', 'info');
          } else if (query.includes('idea') || query.includes('theme') || query.includes('decor')) {
            setActiveView('ideas');
            showToast('Navigated to AI Ideation Studio', 'info');
          } else {
            setActiveView('timeline');
            showToast(`Aura analyzed query: "${query}"`, 'info');
          }
          elements.omniSearchInput.value = '';
        }
      });
    }

    if (elements.formEventCreate) elements.formEventCreate.addEventListener('submit', handleCreateEvent);
    if (elements.eventCurrency) {
      elements.eventCurrency.addEventListener('change', (e) => {
        state.currencyCode = e.target.value;
        state.currencySymbol = CURRENCY_SYMBOLS[e.target.value] || '₹';
        updateCurrencyLabels();
      });
    }

    if (elements.filterAll) {
      elements.filterAll.addEventListener('click', () => {
        state.taskFilter = 'all';
        updateFilterChipStyles(elements.filterAll);
        renderTimelineTasks();
      });
    }
    if (elements.filterPending) {
      elements.filterPending.addEventListener('click', () => {
        state.taskFilter = 'pending';
        updateFilterChipStyles(elements.filterPending);
        renderTimelineTasks();
      });
    }
    if (elements.filterCompleted) {
      elements.filterCompleted.addEventListener('click', () => {
        state.taskFilter = 'completed';
        updateFilterChipStyles(elements.filterCompleted);
        renderTimelineTasks();
      });
    }

    [elements.btnViewGantt, elements.btnViewCards, elements.btnViewDayOf, elements.btnViewCritical].forEach(btn => {
      if (btn) {
        btn.addEventListener('click', () => {
          [elements.btnViewGantt, elements.btnViewCards, elements.btnViewDayOf, elements.btnViewCritical].forEach(b => {
            if (b) {
              b.className = "px-4 py-1.5 rounded-[10px] text-on-surface-variant text-xs whitespace-nowrap hover:text-on-surface transition-all font-medium";
            }
          });
          btn.className = "px-4 py-1.5 rounded-[10px] bg-surface text-primary text-xs whitespace-nowrap shadow-terra-subtle flex items-center gap-1.5 font-bold border border-primary/20";
          showToast(`Switched to ${btn.textContent.trim()}`, 'info');
        });
      }
    });

    if (elements.btnDismissAiBar) {
      elements.btnDismissAiBar.addEventListener('click', () => {
        const bar = elements.btnDismissAiBar.closest('div.p-5');
        if (bar) bar.style.display = 'none';
        showToast('Predictive alert dismissed.', 'info');
      });
    }

    if (elements.btnResolveAiBar) {
      elements.btnResolveAiBar.addEventListener('click', () => {
        if (elements.pbStatus) {
          elements.pbStatus.textContent = "Resolved & Synchronized";
          elements.pbStatus.className = "px-2.5 py-0.5 rounded-full bg-primary/10 text-primary font-bold text-[11px] border border-primary/20";
        }
        if (elements.pbBottleneck) {
          elements.pbBottleneck.textContent = "AI successfully adjusted vendor briefings buffer. All milestone dependencies verified.";
        }
        showToast('Milestone dependencies auto-resolved with AI!', 'success');
      });
    }

    if (elements.btnAutoSequence) {
      elements.btnAutoSequence.addEventListener('click', () => {
        showToast('Auto-sequenced milestones along critical path!', 'success');
      });
    }

    if (elements.btnOpenAddTaskModal) {
      elements.btnOpenAddTaskModal.addEventListener('click', () => {
        const defaultDue = state.currentEvent ? state.currentEvent.event.event_date : '';
        const dueInput = document.getElementById('newTaskDueDate');
        if (dueInput) dueInput.value = defaultDue;
        elements.modalAddTask.classList.add('active');
      });
    }
    if (elements.btnCloseAddTask) elements.btnCloseAddTask.addEventListener('click', () => elements.modalAddTask.classList.remove('active'));
    if (elements.btnCancelAddTask) elements.btnCancelAddTask.addEventListener('click', () => elements.modalAddTask.classList.remove('active'));
    if (elements.formAddTask) elements.formAddTask.addEventListener('submit', handleAddTask);

    if (elements.btnOpenAddBudgetModal) {
      elements.btnOpenAddBudgetModal.addEventListener('click', () => elements.modalAddBudget.classList.add('active'));
    }
    if (elements.btnCloseAddBudget) elements.btnCloseAddBudget.addEventListener('click', () => elements.modalAddBudget.classList.remove('active'));
    if (elements.btnCancelAddBudget) elements.btnCancelAddBudget.addEventListener('click', () => elements.modalAddBudget.classList.remove('active'));
    if (elements.formAddBudget) elements.formAddBudget.addEventListener('submit', handleAddBudgetItem);

    if (elements.btnOpenAddVendorModal) {
      elements.btnOpenAddVendorModal.addEventListener('click', () => elements.modalAddVendor.classList.add('active'));
    }
    if (elements.btnCloseAddVendor) elements.btnCloseAddVendor.addEventListener('click', () => elements.modalAddVendor.classList.remove('active'));
    if (elements.btnCancelAddVendor) elements.btnCancelAddVendor.addEventListener('click', () => elements.modalAddVendor.classList.remove('active'));
    if (elements.formAddVendor) elements.formAddVendor.addEventListener('submit', handleAddVendor);

    if (elements.btnCloseConfirm) elements.btnCloseConfirm.addEventListener('click', hideConfirm);
    if (elements.btnConfirmCancel) elements.btnConfirmCancel.addEventListener('click', hideConfirm);
    if (elements.btnConfirmOk) {
      elements.btnConfirmOk.addEventListener('click', () => {
        if (confirmCallback) confirmCallback();
        hideConfirm();
      });
    }

    if (elements.btnOverviewEdit) elements.btnOverviewEdit.addEventListener('click', () => setActiveView('create'));
    if (elements.btnOverviewDelete) elements.btnOverviewDelete.addEventListener('click', handleDeleteCurrentEvent);

    [elements.modalSavedEvents, elements.modalAddTask, elements.modalAddBudget, elements.modalAddVendor, elements.modalConfirm].forEach(m => {
      if (m) {
        m.addEventListener('click', (e) => {
          if (e.target === m) m.classList.remove('active');
        });
      }
    });
  }

  function updateFilterChipStyles(activeEl) {
    [elements.filterAll, elements.filterPending, elements.filterCompleted].forEach(chip => {
      if (!chip) return;
      if (chip === activeEl) {
        chip.className = "px-3.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold border border-primary/25 cursor-pointer";
      } else {
        chip.className = "px-3.5 py-1 rounded-full bg-surface-container text-on-surface-variant text-xs hover:text-on-surface cursor-pointer border border-outline-variant/30 transition-all font-semibold";
      }
    });
  }

  function updateCurrencyLabels() {
    document.querySelectorAll('.currencySymbol').forEach(el => {
      el.textContent = state.currencySymbol;
    });
  }

  // --- Render All Views ---
  function renderAllViews() {
    if (!state.currentEvent) return;

    renderSidebarAndHeaders();
    renderTimelineTasks();
    renderBudgetSection();
    renderVendors();
    renderIdeas();
    renderOverview();
  }

  // --- Render Sidebar and Top Metadata ---
  function renderSidebarAndHeaders() {
    const ev = state.currentEvent.event;

    if (elements.sidebarEventTitle) elements.sidebarEventTitle.textContent = ev.name;
    if (elements.sidebarEventMeta) elements.sidebarEventMeta.textContent = `${ev.event_date} • ${ev.location}`;
    if (elements.headerCurrentCat) elements.headerCurrentCat.textContent = `Terra ${ev.category.charAt(0).toUpperCase() + ev.category.slice(1)} Suite`;

    if (elements.sidebarCatIcon) {
      if (ev.category === 'wedding') elements.sidebarCatIcon.textContent = 'celebration';
      else if (ev.category === 'birthday') elements.sidebarCatIcon.textContent = 'cake';
      else elements.sidebarCatIcon.textContent = 'groups';
    }

    if (elements.dashCountdown) {
      const target = new Date(ev.event_date);
      const now = new Date();
      const diffDays = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
      elements.dashCountdown.textContent = diffDays > 0 ? `T-Minus ${diffDays} Days` : (diffDays === 0 ? 'Today is Event Day!' : 'Event Concluded');
    }
  }

  // --- Render Timeline Phase-by-Phase (Terra Organic Design) ---
  function renderTimelineTasks() {
    if (!state.currentEvent || !elements.phasesContainer) return;

    const tasks = state.currentEvent.tasks || [];
    elements.phasesContainer.replaceChildren();

    const filteredTasks = tasks.filter(t => {
      if (state.taskFilter === 'pending') return !t.is_completed;
      if (state.taskFilter === 'completed') return t.is_completed;
      return true;
    });

    const phase1Tasks = [];
    const phase2Tasks = [];
    const phase3Tasks = [];

    filteredTasks.forEach((task) => {
      const cat = (task.category || '').toLowerCase();
      const title = (task.title || '').toLowerCase();
      if (cat.includes('venue') || cat.includes('legal') || cat.includes('permit') || cat.includes('contract') || title.includes('venue') || title.includes('deposit') || title.includes('contract')) {
        phase1Tasks.push(task);
      } else if (cat.includes('cater') || cat.includes('decor') || cat.includes('floral') || cat.includes('invitation') || cat.includes('sensory') || title.includes('cater') || title.includes('menu') || title.includes('floral') || title.includes('invite')) {
        phase2Tasks.push(task);
      } else {
        phase3Tasks.push(task);
      }
    });

    if (phase1Tasks.length === 0 && phase2Tasks.length === 0 && phase3Tasks.length === 0) {
      tasks.forEach((t, i) => {
        if (i % 3 === 0) phase1Tasks.push(t);
        else if (i % 3 === 1) phase2Tasks.push(t);
        else phase3Tasks.push(t);
      });
    }

    // Phase 1: Foundation & Venue
    renderPhaseSection({
      phaseNumber: "Phase 01",
      title: "Foundation & Venue",
      subtitle: "Executed Contract & Escrow Lock",
      icon: "check_circle",
      tasks: phase1Tasks,
      isCompleted: phase1Tasks.length > 0 && phase1Tasks.every(t => t.is_completed),
      defaultStatus: "Completed"
    });

    // Phase 2: Design, Catering & Sensory
    renderPhaseSection({
      phaseNumber: "Phase 02 (Current Focus)",
      title: "Design, Catering & Sensory",
      subtitle: `Target Closure: ${state.currentEvent.event.event_date}`,
      icon: "palette",
      tasks: phase2Tasks,
      isCompleted: false,
      defaultStatus: "Active",
      showAiOptimization: true
    });

    // Phase 3: Logistics, AV & Transport
    renderPhaseSection({
      phaseNumber: "Phase 03 (Upcoming)",
      title: "Logistics, AV & Transport",
      subtitle: "Scheduled Prep & Soundcheck",
      icon: "commute",
      tasks: phase3Tasks,
      isCompleted: false,
      defaultStatus: "Scheduled"
    });

    renderRunOfShow();
  }

  function renderPhaseSection(phaseData) {
    const sec = document.createElement('section');
    sec.className = "flex flex-col gap-4";

    const total = phaseData.tasks.length;
    const completed = phaseData.tasks.filter(t => t.is_completed).length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : (phaseData.defaultStatus === 'Completed' ? 100 : (phaseData.defaultStatus === 'Active' ? 75 : 20));

    // Phase Header Well (Terra Tonal Layering)
    const headerWell = document.createElement('div');
    headerWell.className = "p-4.5 rounded-[12px] bg-surface-container-low border border-outline-variant/30 flex items-center justify-between shadow-terra-subtle";

    const left = document.createElement('div');
    left.className = "flex items-center gap-3.5";

    const iconCircle = document.createElement('div');
    iconCircle.className = "w-10 h-10 rounded-[10px] bg-surface-container-high flex items-center justify-center border border-outline-variant/30 text-primary";
    const iconSpan = document.createElement('span');
    iconSpan.className = "material-symbols-outlined text-xl";
    iconSpan.textContent = phaseData.icon;
    iconCircle.appendChild(iconSpan);
    left.appendChild(iconCircle);

    const titleGroup = document.createElement('div');
    const titleRow = document.createElement('div');
    titleRow.className = "flex items-center gap-2";
    
    const phaseNum = document.createElement('span');
    phaseNum.className = "text-xs uppercase font-bold text-primary";
    phaseNum.textContent = phaseData.phaseNumber;
    titleRow.appendChild(phaseNum);

    const dot = document.createElement('span');
    dot.className = "text-outline-variant";
    dot.textContent = "•";
    titleRow.appendChild(dot);

    const mainTitle = document.createElement('span');
    mainTitle.className = "font-headline text-lg lg:text-xl text-on-surface font-bold";
    mainTitle.textContent = phaseData.title;
    titleRow.appendChild(mainTitle);

    titleGroup.appendChild(titleRow);

    const sub = document.createElement('p');
    sub.className = "text-xs text-on-surface-variant leading-tight";
    sub.textContent = phaseData.subtitle;
    titleGroup.appendChild(sub);

    left.appendChild(titleGroup);
    headerWell.appendChild(left);

    // Progress pill & bar
    const right = document.createElement('div');
    right.className = "flex items-center gap-3";

    const pctSpan = document.createElement('span');
    pctSpan.className = "text-xs text-primary font-bold";
    pctSpan.textContent = `${pct}% ${pct === 100 ? 'Completed' : (phaseData.defaultStatus === 'Active' ? 'Active' : 'Scheduled')}`;
    right.appendChild(pctSpan);

    const barOuter = document.createElement('div');
    barOuter.className = "w-24 h-2 rounded-full bg-surface-container overflow-hidden";
    const barInner = document.createElement('div');
    barInner.className = "h-full bg-primary rounded-full transition-all duration-300";
    barInner.style.width = `${pct}%`;
    barOuter.appendChild(barInner);
    right.appendChild(barOuter);

    headerWell.appendChild(right);
    sec.appendChild(headerWell);

    // Cards Container
    const cardsContainer = document.createElement('div');
    cardsContainer.className = "flex flex-col gap-4";

    if (phaseData.tasks.length === 0) {
      const emptyCard = document.createElement('div');
      emptyCard.className = "terra-card bg-surface-container-low p-5 text-xs text-on-surface-variant text-center";
      emptyCard.textContent = "No tasks currently assigned to this phase.";
      cardsContainer.appendChild(emptyCard);
    } else {
      phaseData.tasks.forEach((task, idx) => {
        const card = createTerraTaskCard(task);
        cardsContainer.appendChild(card);

        // Inject the AI Cost-Optimization Callout well after task 1 of Phase 2
        if (phaseData.showAiOptimization && idx === 1) {
          const aiSwapWell = document.createElement('div');
          aiSwapWell.className = "p-3.5 px-4.5 rounded-[12px] bg-surface-container border border-outline-variant/35 flex items-center justify-between gap-3 shadow-terra-subtle -mt-1 mb-1";

          const tipLeft = document.createElement('div');
          tipLeft.className = "flex items-center gap-3";
          const tipIcon = document.createElement('span');
          tipIcon.className = "material-symbols-outlined text-primary text-lg";
          tipIcon.textContent = "savings";
          tipLeft.appendChild(tipIcon);

          const tipText = document.createElement('span');
          tipText.className = "text-xs text-on-surface font-medium leading-relaxed";
          tipText.textContent = "AI Suggestion: Seasonal organic bloom swap (Lisianthus & Olive branch cascade) saves ~₹28,000 ($650) with identical volume.";
          tipLeft.appendChild(tipText);
          aiSwapWell.appendChild(tipLeft);

          const btnSwap = document.createElement('button');
          btnSwap.className = "terra-btn-primary py-1 px-3.5 text-xs shrink-0";
          btnSwap.textContent = "Apply Swap";
          btnSwap.addEventListener('click', () => {
            btnSwap.textContent = "Applied ✓";
            btnSwap.disabled = true;
            showToast("AI Floral Swap applied! Budget allocation updated with ₹28,000 reserve savings.", "success");
          });
          aiSwapWell.appendChild(btnSwap);

          cardsContainer.appendChild(aiSwapWell);
        }
      });
    }

    sec.appendChild(cardsContainer);
    elements.phasesContainer.appendChild(sec);
  }

  function createTerraTaskCard(task) {
    const card = document.createElement('div');
    card.className = "terra-card bg-surface-container-low p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-outline-variant/30 shadow-terra-soft";

    const left = document.createElement('div');
    left.className = "flex items-start gap-4 flex-1";

    // Rounded Organic Checkbox Button
    const checkBtn = document.createElement('button');
    checkBtn.type = "button";
    checkBtn.className = "mt-0.5 w-6 h-6 rounded-[8px] bg-surface border border-outline-variant/40 flex items-center justify-center text-primary hover:border-primary transition-all shrink-0";
    checkBtn.title = "Toggle Milestone Completion";
    
    const checkIcon = document.createElement('span');
    checkIcon.className = `material-symbols-outlined text-sm font-bold ${task.is_completed ? 'opacity-100 text-primary' : 'opacity-0 hover:opacity-40'}`;
    checkIcon.textContent = "check";
    checkBtn.appendChild(checkIcon);

    checkBtn.addEventListener('click', async () => {
      await handleToggleTask(task.id, !task.is_completed);
    });
    left.appendChild(checkBtn);

    // Text & Tags
    const body = document.createElement('div');
    body.className = "flex flex-col gap-1 flex-1";

    const titleRow = document.createElement('div');
    titleRow.className = "flex items-center gap-2 flex-wrap";

    const title = document.createElement('span');
    title.className = `font-headline text-base font-bold text-on-surface ${task.is_completed ? 'line-through opacity-60' : ''}`;
    title.textContent = task.title;
    titleRow.appendChild(title);

    if (task.category) {
      const catTag = document.createElement('span');
      catTag.className = "px-2.5 py-0.5 rounded-full bg-surface-container text-on-surface-variant text-[11px] font-semibold border border-outline-variant/30";
      catTag.textContent = task.category;
      titleRow.appendChild(catTag);
    }

    if (task.priority === 'high') {
      const prioTag = document.createElement('span');
      prioTag.className = "px-2.5 py-0.5 rounded-full bg-tertiary/15 text-tertiary text-[11px] font-bold border border-tertiary/25";
      prioTag.textContent = "High Priority";
      titleRow.appendChild(prioTag);
    }

    body.appendChild(titleRow);

    if (task.description) {
      const desc = document.createElement('p');
      desc.className = "text-xs text-on-surface-variant leading-relaxed";
      desc.textContent = task.description;
      body.appendChild(desc);
    }

    const metaRow = document.createElement('div');
    metaRow.className = "flex items-center gap-3 text-on-surface-variant text-xs mt-1";

    const dueSpan = document.createElement('span');
    dueSpan.className = `flex items-center gap-1 font-semibold ${task.is_overdue ? 'text-error' : 'text-on-surface'}`;
    const calIcon = document.createElement('span');
    calIcon.className = "material-symbols-outlined text-sm text-primary";
    calIcon.textContent = "calendar_clock";
    dueSpan.appendChild(calIcon);
    const dateText = document.createTextNode(` Due ${task.due_date}`);
    dueSpan.appendChild(dateText);
    metaRow.appendChild(dueSpan);

    const bullet = document.createElement('span');
    bullet.textContent = "•";
    metaRow.appendChild(bullet);

    const statusText = document.createElement('span');
    statusText.textContent = task.is_completed ? "Completed & Cleared" : (task.is_overdue ? "Bottleneck Flagged" : "Active Flow");
    metaRow.appendChild(statusText);

    body.appendChild(metaRow);
    left.appendChild(body);
    card.appendChild(left);

    // Right Action Buttons
    const right = document.createElement('div');
    right.className = "flex items-center gap-2.5 self-end md:self-center shrink-0";

    const btnAction = document.createElement('button');
    btnAction.className = "terra-btn-secondary text-xs py-1.5 px-3.5";
    btnAction.textContent = task.is_completed ? "Review Record" : "View Details";
    btnAction.addEventListener('click', () => {
      showToast(`Milestone Details: "${task.title}" due on ${task.due_date}.`, 'info');
    });
    right.appendChild(btnAction);

    const btnDel = document.createElement('button');
    btnDel.className = "w-8 h-8 rounded-[10px] bg-surface hover:bg-error-container text-on-surface-variant hover:text-error flex items-center justify-center border border-outline-variant/30 transition-colors";
    btnDel.title = "Delete Milestone";
    const delIcon = document.createElement('span');
    delIcon.className = "material-symbols-outlined text-sm";
    delIcon.textContent = "delete";
    btnDel.appendChild(delIcon);
    btnDel.addEventListener('click', () => {
      showConfirm(`Delete milestone "${task.title}"?`, () => handleDeleteTask(task.id));
    });
    right.appendChild(btnDel);

    card.appendChild(right);
    return card;
  }

  // --- Render Day-of Run of Show Drawer ---
  function renderRunOfShow() {
    if (!state.currentEvent || !elements.runOfShowTrack) return;
    const items = state.currentEvent.run_of_show || [];
    elements.runOfShowTrack.replaceChildren();

    if (elements.rosDateDisplay) {
      const d = new Date(state.currentEvent.event.event_date);
      const formatted = isNaN(d) ? state.currentEvent.event.event_date : d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' });
      elements.rosDateDisplay.textContent = formatted;
    }

    if (elements.widgetWeatherText) {
      elements.widgetWeatherText.textContent = `${state.currentEvent.event.location} • Historic avg 21°C • 5% Rain Risk`;
    }

    const vLine = document.createElement('div');
    vLine.className = "absolute left-7 top-4 bottom-4 w-0.5 bg-outline-variant/40";
    elements.runOfShowTrack.appendChild(vLine);

    if (items.length === 0) {
      const empty = document.createElement('div');
      empty.className = "text-xs text-on-surface-variant p-3 text-center";
      empty.textContent = "Micro-schedule will synchronize on event creation.";
      elements.runOfShowTrack.appendChild(empty);
      return;
    }

    items.forEach(item => {
      const row = document.createElement('div');
      row.className = "flex items-start gap-3.5 relative z-10 transition-all hover:translate-x-0.5";

      const dotCircle = document.createElement('div');
      if (item.is_key) {
        dotCircle.className = "w-6 h-6 rounded-[8px] bg-tertiary/15 border border-tertiary/25 flex items-center justify-center shrink-0 mt-0.5 text-tertiary";
        const star = document.createElement('span');
        star.className = "material-symbols-outlined text-xs font-bold";
        star.textContent = "favorite";
        dotCircle.appendChild(star);
      } else {
        dotCircle.className = "w-6 h-6 rounded-[8px] bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-0.5 text-primary";
        const innerDot = document.createElement('span');
        innerDot.className = "w-2 h-2 rounded-full bg-primary";
        dotCircle.appendChild(innerDot);
      }
      row.appendChild(dotCircle);

      const body = document.createElement('div');
      body.className = "flex-1 flex flex-col";

      const topRow = document.createElement('div');
      topRow.className = "flex items-center justify-between";

      const timeSpan = document.createElement('span');
      timeSpan.className = "text-xs font-bold text-primary";
      timeSpan.textContent = item.time;
      topRow.appendChild(timeSpan);

      const durSpan = document.createElement('span');
      durSpan.className = `text-[11px] ${item.is_key ? 'text-tertiary font-bold' : 'text-on-surface-variant font-medium'}`;
      durSpan.textContent = item.is_key ? 'Key Event' : (item.duration || '60m');
      topRow.appendChild(durSpan);

      body.appendChild(topRow);

      const title = document.createElement('span');
      title.className = "text-xs text-on-surface font-bold";
      title.textContent = item.title;
      body.appendChild(title);

      const desc = document.createElement('span');
      desc.className = "text-[11px] text-on-surface-variant";
      desc.textContent = item.description;
      body.appendChild(desc);

      row.appendChild(body);
      elements.runOfShowTrack.appendChild(row);
    });
  }

  // --- Render Budget Section ---
  function renderBudgetSection() {
    if (!state.currentEvent) return;
    const summary = state.currentEvent.budget_summary;
    const items = state.currentEvent.budget || [];
    const currency = state.currentEvent.event.currency;

    if (elements.metricTotalBudget) elements.metricTotalBudget.textContent = formatMoney(summary.total_budget, currency);
    if (elements.metricTotalAllocated) elements.metricTotalAllocated.textContent = formatMoney(summary.total_estimated, currency);
    if (elements.metricAllocPct) elements.metricAllocPct.textContent = `${summary.allocation_pct}% allocated`;

    if (elements.metricTotalActual) elements.metricTotalActual.textContent = formatMoney(summary.total_actual, currency);
    if (elements.metricSpentPct) elements.metricSpentPct.textContent = `${summary.actual_utilization_pct}% utilized`;

    if (elements.metricRemaining) {
      elements.metricRemaining.textContent = formatMoney(summary.remaining_balance, currency);
      elements.metricRemaining.style.color = summary.remaining_balance < 0 ? '#b83230' : '#4a7c59';
    }

    if (elements.metricReserveNotice) {
      elements.metricReserveNotice.textContent = `Unallocated reserve: ${formatMoney(summary.unallocated_reserve, currency)}`;
    }

    if (elements.budgetProgressFill) {
      const utilPct = Math.min(100, Math.max(0, summary.utilization_pct));
      elements.budgetProgressFill.style.width = `${utilPct}%`;
    }
    if (elements.progressPctText) {
      elements.progressPctText.textContent = `${summary.actual_utilization_pct}% spent of total ceiling`;
    }

    if (elements.budgetWarningsContainer) {
      elements.budgetWarningsContainer.replaceChildren();
      if (summary.warnings && summary.warnings.length > 0) {
        elements.budgetWarningsContainer.style.display = 'block';
        const strong = document.createElement('strong');
        strong.textContent = 'Financial Alerts: ';
        elements.budgetWarningsContainer.appendChild(strong);
        const ul = document.createElement('ul');
        ul.className = "list-disc pl-5 mt-1";
        summary.warnings.forEach(w => {
          const li = document.createElement('li');
          li.textContent = w;
          ul.appendChild(li);
        });
        elements.budgetWarningsContainer.appendChild(ul);
      } else {
        elements.budgetWarningsContainer.style.display = 'none';
      }
    }

    if (elements.budgetTableBody) {
      elements.budgetTableBody.replaceChildren();
      items.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-surface-container transition-colors";

        const tdCat = document.createElement('td');
        tdCat.className = "py-3 px-4 font-bold text-on-surface";
        tdCat.textContent = item.category;
        tr.appendChild(tdCat);

        const tdPriority = document.createElement('td');
        tdPriority.className = "py-3 px-4";
        const tag = document.createElement('span');
        tag.className = `px-2.5 py-0.5 rounded-full text-[11px] font-bold ${item.priority === 'essential' ? 'bg-primary/10 text-primary border border-primary/20' : 'bg-surface-container-high text-on-surface-variant'}`;
        tag.textContent = item.priority || 'essential';
        tdPriority.appendChild(tag);
        tr.appendChild(tdPriority);

        const tdEst = document.createElement('td');
        tdEst.className = "py-3 px-4 font-semibold text-on-surface";
        tdEst.textContent = formatMoney(item.estimated_amount, currency);
        tr.appendChild(tdEst);

        const tdAct = document.createElement('td');
        tdAct.className = "py-3 px-4";
        const actInput = document.createElement('input');
        actInput.type = "number";
        actInput.min = "0";
        actInput.className = "terra-input w-28 py-1 px-2.5 text-xs font-semibold";
        actInput.value = item.actual_amount;
        actInput.setAttribute('aria-label', `Actual spent for ${item.category}`);
        actInput.addEventListener('change', async (e) => {
          await handleUpdateBudgetActual(item.id, e.target.value);
        });
        tdAct.appendChild(actInput);
        tr.appendChild(tdAct);

        const tdNotes = document.createElement('td');
        tdNotes.className = "py-3 px-4 text-on-surface-variant text-xs";
        tdNotes.textContent = item.notes || '—';
        tr.appendChild(tdNotes);

        const tdActions = document.createElement('td');
        tdActions.className = "py-3 px-4 text-center";
        const btnDel = document.createElement('button');
        btnDel.className = "w-7 h-7 rounded-[8px] bg-surface hover:bg-error-container text-on-surface-variant hover:text-error inline-flex items-center justify-center font-bold text-xs transition-colors border border-outline-variant/30";
        btnDel.textContent = "✕";
        btnDel.title = `Delete ${item.category}`;
        btnDel.addEventListener('click', () => {
          showConfirm(`Delete category "${item.category}"?`, () => handleDeleteBudgetItem(item.id));
        });
        tdActions.appendChild(btnDel);
        tr.appendChild(tdActions);

        elements.budgetTableBody.appendChild(tr);
      });
    }
  }

  // --- Render Vendors Section ---
  function renderVendors() {
    if (!state.currentEvent || !elements.vendorGrid) return;
    const vendors = state.currentEvent.vendors || [];
    elements.vendorGrid.replaceChildren();

    if (vendors.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = "col-span-full p-8 text-center text-xs text-on-surface-variant";
      emptyDiv.textContent = 'No vendor items added yet. Click "+ Add Vendor" to add one.';
      elements.vendorGrid.appendChild(emptyDiv);
      return;
    }

    vendors.forEach(v => {
      const card = document.createElement('div');
      card.className = "terra-card bg-surface-container-low p-6 flex flex-col justify-between border border-outline-variant/30 gap-3 shadow-terra-soft";

      const top = document.createElement('div');
      top.className = "flex items-start justify-between";

      const catBadge = document.createElement('span');
      catBadge.className = "px-2.5 py-0.5 rounded-full bg-tertiary/15 text-tertiary text-[11px] font-bold border border-tertiary/25";
      catBadge.textContent = v.category;
      top.appendChild(catBadge);

      const btnDel = document.createElement('button');
      btnDel.className = "w-7 h-7 rounded-[8px] bg-surface text-on-surface-variant hover:text-error hover:bg-error-container flex items-center justify-center text-xs font-bold transition-colors";
      btnDel.textContent = "✕";
      btnDel.title = "Delete Vendor";
      btnDel.addEventListener('click', () => {
        showConfirm(`Delete vendor "${v.title}"?`, () => handleDeleteVendor(v.id));
      });
      top.appendChild(btnDel);
      card.appendChild(top);

      const mid = document.createElement('div');
      const title = document.createElement('h3');
      title.className = "font-headline text-base text-on-surface font-bold mt-1";
      title.textContent = v.title;
      mid.appendChild(title);

      if (v.description) {
        const desc = document.createElement('p');
        desc.className = "text-xs text-on-surface-variant mt-1 leading-relaxed";
        desc.textContent = v.description;
        mid.appendChild(desc);
      }

      if (v.notes) {
        const notesWell = document.createElement('div');
        notesWell.className = "mt-2.5 p-2 px-3 rounded-[8px] bg-surface border border-outline-variant/30 text-[11px] text-on-surface-variant";
        notesWell.textContent = `Criteria: ${v.notes}`;
        mid.appendChild(notesWell);
      }
      card.appendChild(mid);

      const bot = document.createElement('div');
      bot.className = "flex items-center justify-between pt-3 border-t border-outline-variant/30";

      const statusSelect = document.createElement('select');
      statusSelect.className = "terra-input text-xs py-1 px-3";
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
      bot.appendChild(statusSelect);

      card.appendChild(bot);
      elements.vendorGrid.appendChild(card);
    });
  }

  // --- Render Ideas Section ---
  function renderIdeas() {
    if (!state.currentEvent || !elements.ideasGrid) return;
    const ideas = state.currentEvent.ideas || [];
    elements.ideasGrid.replaceChildren();

    if (ideas.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = "col-span-full p-8 text-center text-xs text-on-surface-variant";
      emptyDiv.textContent = 'No personalized recommendations found for this plan.';
      elements.ideasGrid.appendChild(emptyDiv);
      return;
    }

    ideas.forEach(idea => {
      const card = document.createElement('div');
      card.className = "terra-card bg-surface-container-low p-6 flex flex-col justify-between border border-outline-variant/30 gap-3 shadow-terra-soft";

      const top = document.createElement('div');
      const badge = document.createElement('span');
      badge.className = "px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-[11px] font-bold border border-primary/20 w-fit";
      badge.textContent = (idea.category || 'Concept').toUpperCase();
      top.appendChild(badge);
      card.appendChild(top);

      const mid = document.createElement('div');
      const title = document.createElement('h3');
      title.className = "font-headline text-base text-on-surface font-bold mt-1";
      title.textContent = idea.title;
      mid.appendChild(title);

      const desc = document.createElement('p');
      desc.className = "text-xs text-on-surface-variant mt-1.5 leading-relaxed";
      desc.textContent = idea.description;
      mid.appendChild(desc);

      if (idea.rationale) {
        const rat = document.createElement('div');
        rat.className = "mt-3 p-2.5 px-3 rounded-[8px] bg-surface border border-outline-variant/30 text-xs text-primary font-medium leading-relaxed";
        rat.textContent = `★ Why it suits your event: ${idea.rationale}`;
        mid.appendChild(rat);
      }
      card.appendChild(mid);

      elements.ideasGrid.appendChild(card);
    });
  }

  // --- Render Overview Section ---
  function renderOverview() {
    if (!state.currentEvent) return;
    const ev = state.currentEvent.event;

    if (elements.overviewEventName) elements.overviewEventName.textContent = ev.name;
    if (elements.overviewSummaryText) elements.overviewSummaryText.textContent = ev.plan_summary || 'Comprehensive GenAI-architected event plan.';
    if (elements.overviewAiBadge) elements.overviewAiBadge.textContent = ev.ai_source === 'live_genai' ? 'Live GenAI' : 'Intelligent Fallback';

    if (elements.ovMetricCat) elements.ovMetricCat.textContent = ev.category.toUpperCase();
    if (elements.ovMetricDate) elements.ovMetricDate.textContent = ev.event_date;
    if (elements.ovMetricGuests) elements.ovMetricGuests.textContent = `${ev.guests} Attendees`;
    if (elements.ovMetricBudget) elements.ovMetricBudget.textContent = formatMoney(ev.budget, ev.currency);
  }

  // --- Handlers: Event Creation ---
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

    if (elements.btnGeneratePlan) elements.btnGeneratePlan.disabled = true;
    if (elements.btnGenText) elements.btnGenText.textContent = "Synthesizing Terra Blueprint...";
    if (elements.btnGenSpinner) elements.btnGenSpinner.classList.remove('hidden');

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
        renderAllViews();
        setActiveView('timeline');
        
        const sourceLabel = res.ai_source === 'live_genai' ? 'Live GenAI' : 'Intelligent Rule-Based Engine';
        showToast(`Event blueprint generated successfully via ${sourceLabel}!`, 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to generate event blueprint.', 'error');
    } finally {
      if (elements.btnGeneratePlan) elements.btnGeneratePlan.disabled = false;
      if (elements.btnGenText) elements.btnGenText.textContent = "Generate Terra Event Blueprint";
      if (elements.btnGenSpinner) elements.btnGenSpinner.classList.add('hidden');
    }
  }

  // --- Handlers: Budget Items ---
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

  // --- Handlers: Tasks ---
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
          category: 'Custom Milestone'
        })
      });

      if (res.success) {
        state.currentEvent.tasks = res.tasks;
        renderTimelineTasks();
        elements.modalAddTask.classList.remove('active');
        elements.formAddTask.reset();
        showToast('Milestone created.', 'success');
      }
    } catch (err) {
      showToast(err.message || 'Failed to create milestone.', 'error');
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
        renderTimelineTasks();
        showToast('Milestone deleted.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete milestone.', 'error');
    }
  }

  // --- Handlers: Vendors ---
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
        renderVendors();
        showToast('Vendor removed.', 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to delete vendor.', 'error');
    }
  }

  // --- Handlers: Saved Events ---
  async function openSavedEventsModal() {
    await refreshSavedEvents();
    elements.savedEventsListContainer.replaceChildren();

    if (state.savedEvents.length === 0) {
      const emptyNotice = document.createElement('div');
      emptyNotice.className = "text-center text-xs text-on-surface-variant py-8";
      emptyNotice.textContent = "No saved plans yet. Create an event to save your first blueprint.";
      elements.savedEventsListContainer.appendChild(emptyNotice);
    } else {
      state.savedEvents.forEach(ev => {
        const item = document.createElement('div');
        item.className = "terra-card bg-surface-container-low p-4.5 flex items-center justify-between border border-outline-variant/30 shadow-terra-subtle";

        const left = document.createElement('div');
        const title = document.createElement('h4');
        title.className = "font-headline text-sm font-bold text-on-surface";
        title.textContent = ev.name;
        left.appendChild(title);

        const meta = document.createElement('span');
        meta.className = "text-xs text-on-surface-variant block mt-0.5";
        meta.textContent = `${ev.category.toUpperCase()} • ${ev.event_date} • ${ev.location} • ${formatMoney(ev.budget, ev.currency)}`;
        left.appendChild(meta);
        item.appendChild(left);

        const actions = document.createElement('div');
        actions.className = "flex items-center gap-2";

        const btnOpen = document.createElement('button');
        btnOpen.className = "terra-btn-primary py-1 px-3.5 text-xs";
        btnOpen.textContent = "Open";
        btnOpen.addEventListener('click', async () => {
          elements.modalSavedEvents.classList.remove('active');
          await loadEventById(ev.id);
        });
        actions.appendChild(btnOpen);

        const btnDel = document.createElement('button');
        btnDel.className = "w-7 h-7 rounded-[8px] bg-surface hover:bg-error-container text-on-surface-variant hover:text-error text-xs font-bold transition-colors border border-outline-variant/30 flex items-center justify-center";
        btnDel.textContent = "✕";
        btnDel.title = "Delete Event";
        btnDel.addEventListener('click', () => {
          showConfirm(`Are you sure you want to delete "${ev.name}"? This cannot be undone.`, async () => {
            await deleteEventById(ev.id);
            await openSavedEventsModal();
          });
        });
        actions.appendChild(btnDel);

        item.appendChild(actions);
        elements.savedEventsListContainer.appendChild(item);
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
        renderAllViews();
        setActiveView('timeline');
        showToast(`Loaded blueprint for ${res.data.event.name}`, 'info');
      }
    } catch (err) {
      showToast(err.message || 'Failed to load event blueprint.', 'error');
    }
  }

  async function deleteEventById(eventId) {
    try {
      const res = await apiRequest(`/api/events/${eventId}`, { method: 'DELETE' });
      if (res.success) {
        await refreshSavedEvents();
        if (state.currentEvent && state.currentEvent.event.id === eventId) {
          state.currentEvent = null;
          if (state.savedEvents.length > 0) {
            await loadEventById(state.savedEvents[0].id);
          } else {
            setActiveView('create');
          }
        }
        showToast('Event blueprint deleted.', 'info');
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
