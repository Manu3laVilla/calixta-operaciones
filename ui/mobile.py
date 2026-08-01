import streamlit.components.v1 as components

MOBILE_SIDEBAR_JS = """
<script>
(function () {
  const MOBILE_MAX = 768;

  function getDoc() {
    return window.parent && window.parent.document ? window.parent.document : document;
  }

  function getWidth() {
    return window.parent ? window.parent.innerWidth : window.innerWidth;
  }

  function collapseSidebar() {
    if (getWidth() > MOBILE_MAX) return;

    const doc = getDoc();
    const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
    if (!sidebar) return;

    if (sidebar.getAttribute('aria-expanded') !== 'true') return;

    const selectors = [
      '[data-testid="stSidebarCollapseButton"]',
      '[data-testid="collapsedControl"] button',
      'button[kind="headerNoPadding"]',
    ];

    for (const selector of selectors) {
      const button = doc.querySelector(selector);
      if (button) {
        button.click();
        return;
      }
    }
  }

  collapseSidebar();
  window.setTimeout(collapseSidebar, 150);
  window.setTimeout(collapseSidebar, 600);
  window.addEventListener('resize', collapseSidebar);
})();
</script>
"""


def inject_mobile_sidebar_fix() -> None:
    components.html(MOBILE_SIDEBAR_JS, height=0, width=0)
