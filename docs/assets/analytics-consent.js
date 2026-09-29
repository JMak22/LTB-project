(() => {
  'use strict';

  // LTB Project — privacy-first Google Analytics consent
  // Analytics is not loaded until the visitor explicitly opts in.
  const MEASUREMENT_ID = 'G-4BQEWTYXT2';
  const CONSENT_KEY = 'ltb-analytics-consent';
  const CONSENT_VERSION = '1';
  const CONSENT_VERSION_KEY = 'ltb-analytics-consent-version';

  const COPY = {
    message: `Hey, popping up to give you a choice -- would you mind letting me collect site usage data through Google Analytics? If you do, I'll have a better understanding of how site visitors are using the pages and where I need to change/adapt/add more.

According to Google Analytics, this includes things like which pages are visited, how visitors move through the site, scrolling, downloads and outbound links. I do not use Analytics to identify you personally.

If you choose to opt out, the site will work the same.`
  };

  let analyticsLoaded = false;

  function getStoredConsent() {
    try {
      const version = localStorage.getItem(CONSENT_VERSION_KEY);

      if (version !== CONSENT_VERSION) {
        return null;
      }

      const value = localStorage.getItem(CONSENT_KEY);

      return value === 'granted' || value === 'denied'
        ? value
        : null;
    } catch {
      // If storage is unavailable, treat this as no saved consent.
      return null;
    }
  }

  function storeConsent(value) {
    try {
      localStorage.setItem(CONSENT_KEY, value);
      localStorage.setItem(CONSENT_VERSION_KEY, CONSENT_VERSION);
    } catch {
      // The current page can still respect the visitor's choice
      // even if the browser prevents us from saving it.
    }
  }

  function ensureGtag() {
    window.dataLayer = window.dataLayer || [];

    window.gtag = window.gtag || function () {
      window.dataLayer.push(arguments);
    };
  }

  function loadAnalytics() {
    if (
      analyticsLoaded ||
      document.querySelector(`script[data-ltb-ga="${MEASUREMENT_ID}"]`)
    ) {
      return;
    }

    analyticsLoaded = true;
    ensureGtag();

    // Analytics consent is granted.
    // Advertising-related consent remains denied.
    window.gtag('consent', 'update', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });

    window.gtag('js', new Date());
    window.gtag('config', MEASUREMENT_ID);

    const script = document.createElement('script');

    script.async = true;
    script.src =
      `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(MEASUREMENT_ID)}`;

    script.dataset.ltbGa = MEASUREMENT_ID;

    document.head.appendChild(script);
  }

  function disableAnalytics() {
    // Prevent future GA hits on this page if consent is withdrawn.
    window[`ga-disable-${MEASUREMENT_ID}`] = true;

    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
    }

    // Remove Google Analytics cookies for this host where possible.
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.split('=')[0].trim();

      if (name === '_ga' || name.startsWith('_ga_')) {
        document.cookie =
          `${name}=; Max-Age=0; path=/; SameSite=Lax`;
      }
    });
  }

  function closePanel() {
    document
      .getElementById('analytics-consent-panel')
      ?.remove();
  }

  function saveChoice(value) {
    storeConsent(value);

    if (value === 'granted') {
      window[`ga-disable-${MEASUREMENT_ID}`] = false;
      loadAnalytics();
    } else {
      disableAnalytics();
    }

    closePanel();
  }

  function showPanel({ preferences = false } = {}) {
    closePanel();

    const panel = document.createElement('section');

    panel.id = 'analytics-consent-panel';
    panel.className = 'analytics-consent';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'false');
    panel.setAttribute(
      'aria-labelledby',
      'analytics-consent-title'
    );

    const heading = document.createElement('h2');

    heading.id = 'analytics-consent-title';
    heading.textContent = preferences
      ? 'Analytics preferences'
      : 'A quick analytics choice';

    const text = document.createElement('div');

    text.className = 'analytics-consent__copy';

    COPY.message
      .split('\n\n')
      .forEach(paragraph => {
        const p = document.createElement('p');

        p.textContent = paragraph;
        text.appendChild(p);
      });

    const actions = document.createElement('div');

    actions.className = 'analytics-consent__actions';

    const accept = document.createElement('button');

    accept.type = 'button';
    accept.className =
      'analytics-consent__button analytics-consent__button--primary';
    accept.textContent = 'Allow analytics';
    accept.addEventListener(
      'click',
      () => saveChoice('granted')
    );

    const decline = document.createElement('button');

    decline.type = 'button';
    decline.className = 'analytics-consent__button';
    decline.textContent = 'No thanks';
    decline.addEventListener(
      'click',
      () => saveChoice('denied')
    );

    actions.append(accept, decline);
    panel.append(heading, text, actions);

    document.body.appendChild(panel);

    heading.setAttribute('tabindex', '-1');
    heading.focus({ preventScroll: true });
  }

  function addPreferencesControl() {
    const footer = document.querySelector('footer');

    if (
      !footer ||
      footer.querySelector('[data-analytics-preferences]')
    ) {
      return;
    }

    const separator = document.createTextNode(' | ');

    const button = document.createElement('button');

    button.type = 'button';
    button.className = 'analytics-preferences-link';
    button.dataset.analyticsPreferences = '';
    button.textContent = 'Analytics preferences';

    button.addEventListener(
      'click',
      () => showPanel({ preferences: true })
    );

    const firstParagraph = footer.querySelector('p');

    if (firstParagraph) {
      firstParagraph.append(separator, button);
    } else {
      footer.append(button);
    }
  }

  function init() {
    addPreferencesControl();

    const consent = getStoredConsent();

    if (consent === 'granted') {
      loadAnalytics();
    } else if (consent === 'denied') {
      disableAnalytics();
    } else {
      showPanel();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      init,
      { once: true }
    );
  } else {
    init();
  }
})();