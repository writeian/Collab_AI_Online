/**
 * AI Collab Onboarding Tutorial - Shepherd.js
 * Three variants: Full Tutorial, Room Creation Tutorial, Chat Pages Tutorial
 */

(function() {
  'use strict';

  const STORAGE_KEY_ACTIVE = 'tutorial_tour_active';
  const STORAGE_KEY_STEP = 'tutorial_tour_step';
  const STORAGE_KEY_PENDING_CHAT = 'tutorial_pending_chat_view';
  const STORAGE_KEY_AFTER_ROOM_CREATION = 'tutorial_after_room_creation';

  function completeTutorial() {
    fetch('/api/tutorial/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin'
    }).catch(() => {});
    sessionStorage.removeItem(STORAGE_KEY_ACTIVE);
    sessionStorage.removeItem(STORAGE_KEY_STEP);
  }

  function createStepOptions(text, attachTo, buttons) {
    const step = {
      text: text,
      scrollTo: true,
      cancelIcon: { enabled: true },
      buttons: buttons || []
    };
    if (attachTo) {
      step.attachTo = attachTo;
    } else {
      step.attachTo = false;
    }
    return step;
  }

  function skipButton(tour) {
    return {
      text: 'Skip',
      action: function() {
        tour.cancel();
        completeTutorial();
      }
    };
  }

  function defaultButtons(tour, isLast, opts) {
    opts = opts || {};
    if (isLast) {
      var doneAction = function() {
        if (!opts.skipCompleteOnDone) completeTutorial();
        tour.complete();
      };
      return [
        skipButton(tour),
        { text: 'Next', action: doneAction }
      ];
    }
    return [
      skipButton(tour),
      { text: 'Next', action: tour.next }
    ];
  }

  function startRoomCreationTour(isFullTour) {
    if (typeof Shepherd === 'undefined') return;

    const container = document.querySelector('[data-has-rooms]');
    const hasRooms = container && container.getAttribute('data-has-rooms') === 'true';

    const welcomeEl = document.getElementById('tutorial-welcome') || document.querySelector('h2.text-3xl');
    const createBtn = document.querySelector('a[href*="create_room"]');
    const templateBtn = document.querySelector('button[onclick="showTemplateWizards()"]');
    const roomCard = document.querySelector('.room-card[data-room-id]') || document.querySelector('[data-tutorial="room-card"]');
    const createFirstRoomBtn = document.getElementById('tutorial-create-first-room');

    const steps = [];

    if (welcomeEl) {
      steps.push(createStepOptions(
        'Welcome to AI Collab! Let\'s take a quick tour to get you started. You can skip at any time.',
        { element: welcomeEl, on: 'bottom' },
        []
      ));
    }
    if (createBtn) {
      steps.push(createStepOptions(
        'Create a new room to start collaborating. Each room is a space for learning and discussion.',
        { element: createBtn, on: 'bottom' },
        []
      ));
    }
    if (templateBtn) {
      steps.push(createStepOptions(
        'Or use a template for guided setup. Templates include Study Group, Business Hub, Academic Essay, and more.',
        { element: templateBtn, on: 'bottom' },
        []
      ));
    }
    if (roomCard) {
      steps.push(createStepOptions(
        'Open any existing room to view your learning journey, start chats, and collaborate with your team.',
        { element: roomCard, on: 'top' },
        []
      ));
    }

    // No rooms: add "Create your first room" step that navigates to room creation
    if (!hasRooms && (createFirstRoomBtn || createBtn)) {
      var createRoomTarget = createFirstRoomBtn || createBtn;
      var createRoomHref = createRoomTarget.getAttribute('href') || '/room/create';
      steps.push(createStepOptions(
        'Create your first learning space to continue the tutorial. Click the button below to get started—we\'ll pick up the tutorial once your room is ready.',
        { element: createRoomTarget, on: 'top' },
        []
      ));
    }

    if (steps.length === 0) {
      steps.push(createStepOptions(
        'Welcome to AI Collab! Create a room or use a template to get started.',
        false,
        [{ text: 'Got it', action: function() { completeTutorial(); this.complete(); } }]
      ));
    }

    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: {
        classes: 'shepherd-theme-default',
        scrollTo: true,
        modalOverlayOpeningRadius: 12
      }
    });

    var createRoomHrefForNav = null;
    if (!hasRooms && (createFirstRoomBtn || createBtn)) {
      createRoomHrefForNav = (createFirstRoomBtn || createBtn).getAttribute('href') || '/room/create';
    }

    steps.forEach((s, i) => {
      var isLast = i === steps.length - 1;
      var isCreateRoomStep = !hasRooms && isLast && createRoomHrefForNav;
      if (isCreateRoomStep) {
        s.buttons = [
          skipButton(tour),
          {
            text: 'Create Room',
            action: function() {
              sessionStorage.setItem(STORAGE_KEY_AFTER_ROOM_CREATION, '1');
              if (sessionStorage.getItem(STORAGE_KEY_ACTIVE) !== 'full') {
                completeTutorial();
              }
              window.location.href = createRoomHrefForNav;
            }
          }
        ];
      } else {
        s.buttons = defaultButtons(tour, isLast, { skipCompleteOnDone: isFullTour });
      }
      tour.addStep({ id: 'room-step-' + i, ...s });
    });

    // Full Tutorial: when Room Creation completes, redirect to first room to continue
    tour.on('complete', function() {
      if (sessionStorage.getItem(STORAGE_KEY_ACTIVE) === 'full') {
        var roomCardEl = document.querySelector('.room-card[data-room-id]') || document.querySelector('[data-tutorial="room-card"]');
        var roomId = roomCardEl ? roomCardEl.getAttribute('data-room-id') : null;
        var roomLink = document.querySelector('.room-card a[href*="/room/"]');
        var href = roomLink ? (roomLink.getAttribute('href') || '') : '';
        var match = href.match(/\/room\/(\d+)/) || (roomId ? [null, roomId] : null);
        if (match && match[1]) {
          window.location.href = '/room/' + match[1] + '?start_chat_tutorial=1';
          return;
        }
        completeTutorial();
      }
    });

    tour.start();
    return tour;
  }

  function startRoomCreationStepsTour() {
    if (typeof Shepherd === 'undefined') return;

    var goalsInput = document.getElementById('goals');
    var templateSection = document.getElementById('tutorial-template-section');
    var generateBtn = document.getElementById('generate-proposal-btn');

    var steps = [];

    if (goalsInput) {
      steps.push(createStepOptions(
        'This is where you tell the AI what the goal of your room is. Describe what you want to achieve, and the AI will generate learning steps and suggest a room title.',
        { element: goalsInput, on: 'right' },
        []
      ));
    }
    if (templateSection) {
      steps.push(createStepOptions(
        'Use a template for pre-prepared room structures. Choose from proven templates like Study Group or Business Hub, or let AI create custom steps based on your goals.',
        { element: templateSection, on: 'right' },
        []
      ));
    }
    if (generateBtn) {
      steps.push(createStepOptions(
        'Press here to create your room. The AI will generate a complete room with title, description, and learning steps.',
        { element: generateBtn, on: 'top' },
        []
      ));
    }

    if (steps.length === 0) return;

    var tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });

    steps.forEach(function(s, i) {
      var isLast = i === steps.length - 1;
      s.buttons = [
        { text: 'Skip', action: tour.cancel },
        { text: isLast ? 'Got it' : 'Next', action: isLast ? tour.complete : tour.next }
      ];
      tour.addStep({ id: 'room-create-step-' + i, ...s });
    });

    tour.start();
  }

  function startRoomProposalTour() {
    if (typeof Shepherd === 'undefined') return;

    var proposalTitle = document.getElementById('tutorial-ai-proposal');
    var refineSection = document.getElementById('tutorial-refine-section');
    var createRoomBtn = document.getElementById('save-room-btn');

    var steps = [];

    if (proposalTitle) {
      steps.push(createStepOptions(
        'This is the proposal the AI has generated based on your previous instructions. Review the room title, description, and learning steps.',
        { element: proposalTitle, on: 'bottom' },
        []
      ));
    }
    if (refineSection) {
      steps.push(createStepOptions(
        'This is your opportunity to make any final changes. Chat with the AI to improve the title, description, or learning steps before creating the room.',
        { element: refineSection, on: 'right' },
        []
      ));
    }
    if (createRoomBtn) {
      steps.push(createStepOptions(
        'When you\'re happy with the proposal, press here to create your room.',
        { element: createRoomBtn, on: 'top' },
        []
      ));
    }

    if (steps.length === 0) return;

    var tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });

    steps.forEach(function(s, i) {
      var isLast = i === steps.length - 1;
      s.buttons = [
        { text: 'Skip', action: tour.cancel },
        { text: isLast ? 'Got it' : 'Next', action: isLast ? tour.complete : tour.next }
      ];
      tour.addStep({ id: 'room-proposal-step-' + i, ...s });
    });

    tour.start();
  }

  function showOptionsModal() {
    const modal = document.getElementById('tutorial-options-modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function hideOptionsModal() {
    const modal = document.getElementById('tutorial-options-modal');
    if (modal) {
      modal.classList.add('hidden');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  function startFullTour() {
    hideOptionsModal();
    sessionStorage.setItem(STORAGE_KEY_ACTIVE, 'full');
    sessionStorage.setItem(STORAGE_KEY_STEP, '0');
    startRoomCreationTour(true);
  }

  function startChatPagesTour() {
    hideOptionsModal();
    const match = location.pathname.match(/\/room\/(\d+)/);
    if (match) {
      const roomId = match[1];
      if (/\/chat\/\d+/.test(location.pathname)) {
        sessionStorage.setItem(STORAGE_KEY_ACTIVE, 'chat');
        sessionStorage.setItem(STORAGE_KEY_STEP, '0');
        startChatViewTour();
      } else {
        sessionStorage.setItem(STORAGE_KEY_ACTIVE, 'chat');
        sessionStorage.setItem(STORAGE_KEY_STEP, '0');
        startRoomViewTour();
      }
    } else {
      const firstRoomLink = document.querySelector('.room-card a[href*="/room/"]');
      if (firstRoomLink) {
        const href = firstRoomLink.getAttribute('href') || '';
        const roomMatch = href.match(/\/room\/(\d+)/);
        if (roomMatch) {
          window.location.href = '/room/' + roomMatch[1] + '?start_chat_tutorial=1';
          return;
        }
      }
      alert('Please open a room first to start the Chat Pages tutorial.');
    }
  }

  function startRoomViewTour() {
    if (typeof Shepherd === 'undefined') return;

    const startChat = document.querySelector('a[href*="/chat/create"]');
    const keyDocs = document.querySelector('button[onclick="openKeyDocumentsModal()"]');
    const inviteBtn = document.querySelector('a[href*="/invite"]');

    const steps = [];
    if (startChat) {
      steps.push(createStepOptions(
        'Start a new chat to begin a conversation with AI. Each chat can have its own mode and context.',
        { element: startChat, on: 'bottom' },
        []
      ));
    }
    if (keyDocs) {
      steps.push(createStepOptions(
        'Key Documents let you upload a syllabus, evaluation rubric, or other permanent docs. These are available across all chats.',
        { element: keyDocs, on: 'bottom' },
        []
      ));
    }
    if (inviteBtn) {
      steps.push(createStepOptions(
        'Invite collaborators to join your room. They can participate in chats and learning activities.',
        { element: inviteBtn, on: 'bottom' },
        []
      ));
    }

    if (steps.length === 0) return;

    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });

    steps.forEach((s, i) => {
      s.buttons = defaultButtons(tour, i === steps.length - 1, { skipCompleteOnDone: true });
      tour.addStep({ id: 'room-view-step-' + i, ...s });
    });

    tour.on('complete', function() {
      const roomId = (location.pathname.match(/\/room\/(\d+)/) || [])[1];
      if (roomId) {
        window.location.href = '/room/' + roomId + '/chat/create?start_chat_tutorial=1';
      }
    });

    tour.start();
  }

  function collapseSidebarSections() {
    document.querySelectorAll('.sidebar-section[open]').forEach(function(el) { el.removeAttribute('open'); });
  }

  function startChatViewTour() {
    if (typeof Shepherd === 'undefined') return;

    collapseSidebarSections();

    const toolsSection = document.querySelector('details[data-section="tools"]');
    const membersSection = document.querySelector('details[data-section="members"]');
    const aiRole = document.querySelector('details[data-section="ai-role"]');
    const libraryCard = document.getElementById('library-card');
    const toneCard = document.getElementById('tone-card');
    const toolsBtn = document.querySelector('.tools-menu-button');
    const inviteBtn = document.getElementById('invite-modal-open-btn');

    const steps = [];
    var inviteStepIndex = -1;
    if (aiRole) {
      steps.push(createStepOptions(
        'The AI Assistant has different modes (e.g., Tutor, Critic). Change the mode to adjust how the AI responds.',
        { element: aiRole, on: 'left' },
        []
      ));
    }
    if (libraryCard) {
      steps.push(createStepOptions(
        'The Library stores documents you upload. The AI can search and reference them in your chats.',
        { element: libraryCard, on: 'left' },
        []
      ));
    }
    if (toneCard) {
      steps.push(createStepOptions(
        'Tone & Critique lets you adjust how critical or supportive the AI feedback is. Slide to find your preference.',
        { element: toneCard, on: 'left' },
        []
      ));
    }
    if (inviteBtn) {
      inviteStepIndex = steps.length;
      steps.push(createStepOptions(
        'Invite collaborators to join this room directly from the chat view.',
        { element: inviteBtn, on: 'right' },
        []
      ));
    }
    if (toolsBtn) {
      steps.push(createStepOptions(
        'Open the Tools menu to access Quiz, Flashcards, Mind Map, and Narrative. We\'ll show you the Quiz next.',
        { element: toolsBtn, on: 'top' },
        []
      ));
    }

    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });

    steps.forEach((s, i) => {
      const isLast = i === steps.length - 1;
      s.buttons = isLast
        ? [
            skipButton(tour),
            {
              text: 'Next: Quiz',
              action: function() {
                tour.complete();
                const quizItem = document.querySelector('.tools-menu-item[data-tool="quiz"]');
                if (quizItem) quizItem.click();
                setTimeout(function() {
                  startQuizToolTour(true);
                }, 500);
              }
            }
          ]
        : defaultButtons(tour, false);
      tour.addStep({ id: 'chat-step-' + i, ...s });
    });

    document.body.classList.add('tutorial-chat-tour');
    tour.on('show', function(event) {
      var stepId = event.step && event.step.id;
      if (stepId === 'chat-step-0' && aiRole) aiRole.removeAttribute('open');
      if ((stepId === 'chat-step-1' || stepId === 'chat-step-2') && toolsSection) toolsSection.setAttribute('open', '');
      if (inviteStepIndex >= 0 && stepId === 'chat-step-' + inviteStepIndex && membersSection) {
        membersSection.setAttribute('open', '');
      }
    });

    tour.on('cancel', function() {
      document.body.classList.remove('tutorial-chat-tour');
    });
    tour.on('complete', function() {
      document.body.classList.remove('tutorial-chat-tour');
    });

    tour.start();
  }

  function finishFullTutorialAndGoHome() {
    completeTutorial();
    window.location.href = '/room/v2/';
  }

  function startQuizToolTour(isFromFullTour) {
    if (typeof Shepherd === 'undefined') return;

    const panel = document.getElementById('quiz-panel');
    if (!panel) return;

    var skipOrFinish = function() { if (isFromFullTour) finishFullTutorialAndGoHome(); else tour.cancel(); };
    var gotItOrFinish = function() { if (isFromFullTour) finishFullTutorialAndGoHome(); else tour.complete(); };

    const tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });

    const steps = [
      {
        id: 'quiz-step-1',
        text: 'The Quiz tool generates questions from your chat.',
        attachTo: { element: '#quiz-panel-title', on: 'bottom' }
      },
      {
        id: 'quiz-step-2',
        text: 'Enter topics or leave blank to use chat context.',
        attachTo: { element: '#quiz-context-mode', on: 'right' }
      },
      {
        id: 'quiz-step-3',
        text: 'Click Generate to create questions.',
        attachTo: { element: '#quiz-generate-btn', on: 'top' }
      },
      {
        id: 'quiz-step-4',
        text: 'Every educational tool has a Tutorial button for on-demand help.',
        attachTo: { element: '.quiz-panel__tutorial', on: 'bottom' }
      }
    ];

    steps.forEach(function(s, i) {
      var isLast = i === steps.length - 1;
      tour.addStep({
        id: s.id,
        text: s.text,
        attachTo: s.attachTo,
        scrollTo: true,
        cancelIcon: { enabled: true },
        buttons: [
          { text: 'Skip', action: skipOrFinish },
          { text: isLast ? 'Got it' : 'Next', action: isLast ? gotItOrFinish : tour.next }
        ]
      });
    });

    tour.start();
  }

  function startFlashcardsToolTour() {
    if (typeof Shepherd === 'undefined') return;
    var panel = document.getElementById('flashcards-panel');
    if (!panel) return;

    var steps = [
      { id: 'flashcards-step-1', text: 'Generate flashcards from your chat or library.', attachTo: { element: '#flashcards-panel-title', on: 'bottom' } },
      { id: 'flashcards-step-2', text: 'Choose context (chat, library, or both) and set display mode.', attachTo: { element: '#flashcards-context-mode', on: 'right' } },
      { id: 'flashcards-step-3', text: 'Click Generate to create flashcards.', attachTo: { element: '#flashcards-generate-btn', on: 'top' } },
      { id: 'flashcards-step-4', text: 'Every educational tool has a Tutorial button for on-demand help.', attachTo: { element: '.flashcards-panel__tutorial', on: 'bottom' } }
    ];
    runMultiStepToolTour(steps);
  }

  function startMindmapToolTour() {
    if (typeof Shepherd === 'undefined') return;
    var panel = document.getElementById('mindmap-panel');
    if (!panel) return;

    var steps = [
      { id: 'mindmap-step-1', text: 'Create a mind map from your chat or library.', attachTo: { element: '#mindmap-panel-title', on: 'bottom' } },
      { id: 'mindmap-step-2', text: 'Select context and size for your mind map.', attachTo: { element: '#mindmap-context-mode', on: 'right' } },
      { id: 'mindmap-step-3', text: 'Click Generate to visualize concepts and relationships.', attachTo: { element: '#mindmap-generate-btn', on: 'top' } },
      { id: 'mindmap-step-4', text: 'Every educational tool has a Tutorial button for on-demand help.', attachTo: { element: '.mindmap-panel__tutorial', on: 'bottom' } }
    ];
    runMultiStepToolTour(steps);
  }

  function startNarrativeToolTour() {
    if (typeof Shepherd === 'undefined') return;
    var panel = document.getElementById('narrative-panel');
    if (!panel) return;

    var steps = [
      { id: 'narrative-step-1', text: 'Generate narratives from your chat or library content.', attachTo: { element: '#narrative-panel-title', on: 'bottom' } },
      { id: 'narrative-step-2', text: 'Choose context and narrative type.', attachTo: { element: '#narrative-context-mode', on: 'right' } },
      { id: 'narrative-step-3', text: 'Click Generate to create your narrative.', attachTo: { element: '#narrative-generate-btn', on: 'top' } },
      { id: 'narrative-step-4', text: 'Every educational tool has a Tutorial button for on-demand help.', attachTo: { element: '.narrative-panel__tutorial', on: 'bottom' } }
    ];
    runMultiStepToolTour(steps);
  }

  function runMultiStepToolTour(steps) {
    var tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: { classes: 'shepherd-theme-default', scrollTo: true, modalOverlayOpeningRadius: 12 }
    });
    steps.forEach(function(s, i) {
      var isLast = i === steps.length - 1;
      tour.addStep({
        id: s.id,
        text: s.text,
        attachTo: s.attachTo,
        scrollTo: true,
        cancelIcon: { enabled: true },
        buttons: [
          { text: 'Skip', action: tour.cancel },
          { text: isLast ? 'Got it' : 'Next', action: isLast ? tour.complete : tour.next }
        ]
      });
    });
    tour.start();
  }

  window.TutorialManager = {
    showOptionsModal: showOptionsModal,
    hideOptionsModal: hideOptionsModal,
    startFullTour: startFullTour,
    startRoomCreationTour: startRoomCreationTour,
    startRoomCreationStepsTour: startRoomCreationStepsTour,
    startRoomProposalTour: startRoomProposalTour,
    startChatPagesTour: startChatPagesTour,
    startQuizToolTour: startQuizToolTour,
    startFlashcardsToolTour: startFlashcardsToolTour,
    startMindmapToolTour: startMindmapToolTour,
    startNarrativeToolTour: startNarrativeToolTour,
    completeTutorial: completeTutorial
  };

  document.addEventListener('DOMContentLoaded', function() {
    // Resume tutorial after room creation: redirect to room view with chat tutorial param
    if (sessionStorage.getItem(STORAGE_KEY_AFTER_ROOM_CREATION) === '1' &&
        /^\/room\/\d+$/.test(location.pathname) &&
        !/\/chat\//.test(location.pathname)) {
      sessionStorage.removeItem(STORAGE_KEY_AFTER_ROOM_CREATION);
      window.location.href = location.pathname + '?start_chat_tutorial=1';
      return;
    }

    // Room creation steps tour: highlight goals, template, and generate button
    if (sessionStorage.getItem(STORAGE_KEY_AFTER_ROOM_CREATION) === '1' &&
        /\/room\/create\/learning-steps/.test(location.pathname)) {
      var createContainer = document.querySelector('[data-tutorial-room-create]');
      if (createContainer && createContainer.getAttribute('data-tutorial-room-create') === 'true') {
        startRoomCreationStepsTour();
      }
    }

    const launcher = document.getElementById('tutorial-launcher-btn');
    if (launcher) {
      launcher.addEventListener('click', showOptionsModal);
    }

    document.querySelectorAll('[data-tutorial-modal-close]').forEach(function(btn) {
      btn.addEventListener('click', hideOptionsModal);
    });

    document.getElementById('tutorial-option-full')?.addEventListener('click', startFullTour);
    document.getElementById('tutorial-option-room')?.addEventListener('click', function() {
      hideOptionsModal();
      startRoomCreationTour();
    });
    document.getElementById('tutorial-option-chat')?.addEventListener('click', startChatPagesTour);

    // Auto-open tutorial disabled - was causing app to hang. Users can still click Tutorial button.
    // const container = document.querySelector('[data-show-tutorial-modal]');
    // const showModal = container?.getAttribute('data-show-tutorial-modal') === 'true';
    // const justRegistered = container?.getAttribute('data-just-registered') === 'true';
    // const tutorialCompleted = container?.getAttribute('data-tutorial-completed') === 'true';
    // if (showModal && !tutorialCompleted) {
    //   if (justRegistered) { startFullTour(); } else { showOptionsModal(); }
    // }

    // Chat create form: set flag so chat tour runs after user creates chat and lands on chat view
    if (location.search.includes('start_chat_tutorial=1') && /\/room\/\d+\/chat\/create/.test(location.pathname)) {
      sessionStorage.setItem(STORAGE_KEY_PENDING_CHAT, '1');
      const url = new URL(location.href);
      url.searchParams.delete('start_chat_tutorial');
      window.history.replaceState({}, '', url.pathname + url.search);
      // Ensure any lingering Shepherd overlay from previous tour is removed so form is clickable
      if (typeof Shepherd !== 'undefined') {
        document.querySelectorAll('.shepherd-modal-overlay-container').forEach(function(el) {
          el.classList.remove('shepherd-modal-is-visible');
          el.style.pointerEvents = 'none';
        });
      }
    }
    // Chat view: run tour if we have the param or the pending flag (set from chat create page)
    else if ((location.search.includes('start_chat_tutorial=1') || sessionStorage.getItem(STORAGE_KEY_PENDING_CHAT) === '1') && /\/chat\/\d+/.test(location.pathname)) {
      sessionStorage.removeItem(STORAGE_KEY_PENDING_CHAT);
      const url = new URL(location.href);
      url.searchParams.delete('start_chat_tutorial');
      window.history.replaceState({}, '', url.pathname + url.search);
      startChatViewTour();
    }
    // Room view (not chat create): run room tour
    else if (location.search.includes('start_chat_tutorial=1') && /\/room\/\d+/.test(location.pathname)) {
      const url = new URL(location.href);
      url.searchParams.delete('start_chat_tutorial');
      window.history.replaceState({}, '', url.pathname + url.search);
      startRoomViewTour();
    }
  });
})();
