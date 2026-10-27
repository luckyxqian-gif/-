/* personal-html-interactions-baseline:v2 | 按 data-capabilities 选择并内联；正文结构由内容决定。 */
(() => {
  const root = document.documentElement;
  const main = document.querySelector("main");
  const status = document.querySelector("[role='status']");
  const actions = Object.fromEntries(
    [...document.querySelectorAll("[data-action]")].map(node => [node.dataset.action, node])
  );
  const capabilities = new Set((root.dataset.capabilities || "").split(/\s+/).filter(Boolean));
  const reviewEnabled = capabilities.has("review");
  const focusEnabled = capabilities.has("focus") || reviewEnabled;
  const editorEnabled = capabilities.has("editor");
  const navigationEnabled = capabilities.has("navigation");
  const searchEnabled = capabilities.has("search");
  const interactive = reviewEnabled || editorEnabled;
  const baseKey = root.dataset.documentKey || `${location.pathname}|${document.title}`;
  const contentVersion = root.dataset.contentVersion || "v1";
  const identity = `${baseKey}|${contentVersion}`;
  const storageKey = `personal-html-content:${identity}`;
  const legacyStorageKey = `personal-html-highlights:${baseKey}`;
  const focusStorageKey = `personal-html-focus:${identity}`;
  const editorToolbar = document.querySelector("[data-editor-toolbar]");
  const searchPanel = document.querySelector("[data-search-panel]");
  const searchInput = document.querySelector("[data-search-input]");
  const searchCount = document.querySelector("[data-search-count]");
  const readingProgress = document.querySelector("[data-reading-progress]");
  const editorCommands = new Set([
    "fontSize", "bold", "italic", "underline", "strikeThrough", "foreColor",
    "createLink", "justifyLeft", "justifyCenter", "justifyRight", "removeFormat", "delete", "undo", "redo"
  ]);
  let savedRange = null;
  let editorRange = null;
  let targetHighlight = null;
  let highlightMode = false;
  let removeMode = false;
  let editMode = false;
  let searchHits = [];
  let searchIndex = -1;
  let activeRoom = null;
  let activateSection = null;

  const announce = message => {
    if (!status) return;
    status.textContent = message;
    window.setTimeout(() => { if (status.textContent === message) status.textContent = ""; }, 2400);
  };

  const editableRoots = () => main ? [...main.querySelectorAll("[data-editable]")] : [];

  function selectionRange() {
    const selection = window.getSelection();
    if (!main || !selection || selection.rangeCount === 0 || selection.isCollapsed) return null;
    const range = selection.getRangeAt(0);
    const common = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
      ? range.commonAncestorContainer : range.commonAncestorContainer.parentElement;
    return common && main.contains(common) ? range.cloneRange() : null;
  }

  function editableRootFor(range) {
    if (!range) return null;
    const node = range.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
      ? range.commonAncestorContainer : range.commonAncestorContainer.parentElement;
    return node?.closest?.("[data-editable]") || null;
  }

  function persist() {
    if (!interactive || !main) return;
    try { localStorage.setItem(storageKey, main.innerHTML); }
    catch (_) { announce("浏览器未能保存本次修改"); }
  }

  function rememberEditorRange() {
    if (!editMode) return null;
    const range = selectionRange();
    if (!range || !editableRootFor(range)) return null;
    editorRange = range;
    return editorRange;
  }

  function restoreEditorRange() {
    if (!editorRange || !editableRootFor(editorRange)) return null;
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(editorRange);
    return editableRootFor(editorRange);
  }

  function hideEditorToolbar() {
    if (editorToolbar) editorToolbar.hidden = true;
  }

  function positionEditorToolbar(range = editorRange) {
    if (!editorToolbar || !editMode || !range || range.collapsed || !editableRootFor(range)) {
      hideEditorToolbar();
      return;
    }
    const rect = range.getBoundingClientRect();
    if (!rect.width && !rect.height) { hideEditorToolbar(); return; }
    editorToolbar.hidden = false;
    const margin = 10;
    const toolbarRect = editorToolbar.getBoundingClientRect();
    const left = Math.min(
      window.innerWidth - toolbarRect.width - margin,
      Math.max(margin, rect.left + rect.width / 2 - toolbarRect.width / 2)
    );
    const above = rect.top - toolbarRect.height - margin;
    const top = above >= margin ? above : Math.min(window.innerHeight - toolbarRect.height - margin, rect.bottom + margin);
    editorToolbar.style.left = `${left}px`;
    editorToolbar.style.top = `${Math.max(margin, top)}px`;
  }

  function safeLink(raw) {
    const value = raw.trim();
    if (value.startsWith("#")) return value;
    const withProtocol = /^www\./i.test(value) ? `https://${value}` : value;
    try {
      const parsed = new URL(withProtocol);
      return ["https:", "http:", "mailto:"].includes(parsed.protocol) ? withProtocol : null;
    } catch (_) { return null; }
  }

  function normalizeNewFontSize(editableRoot, before, px) {
    if (!editableRoot || !px) return;
    editableRoot.querySelectorAll('font[size="7"]').forEach(font => {
      if (before.has(font)) return;
      const span = document.createElement("span");
      span.style.fontSize = `${px}px`;
      span.append(...font.childNodes);
      font.replaceWith(span);
    });
  }

  function runEditorCommand(command, value = null) {
    if (!editMode || !editorCommands.has(command)) return;
    const historyCommand = command === "undo" || command === "redo";
    const editableRoot = historyCommand
      ? document.activeElement?.closest?.("[data-editable]") || editableRoots()[0]
      : restoreEditorRange();
    if (!editableRoot) return;
    editableRoot.focus({ preventScroll: true });
    if (command === "createLink") {
      const raw = value || window.prompt("请输入链接地址", "https://");
      if (!raw) return;
      const href = safeLink(raw);
      if (!href) { announce("链接仅支持网页、邮件或页面内锚点"); return; }
      document.execCommand(command, false, href);
    } else if (command === "fontSize") {
      const before = new Set(editableRoot.querySelectorAll('font[size="7"]'));
      document.execCommand("fontSize", false, "7");
      normalizeNewFontSize(editableRoot, before, value);
    } else {
      document.execCommand(command, false, value);
    }
    if (!historyCommand) rememberEditorRange();
    persist();
    positionEditorToolbar();
  }

  function toggleEdit() {
    if (!editorEnabled) return;
    const blocks = editableRoots();
    if (!blocks.length) { announce("未找到可编辑正文块"); return; }
    editMode = !editMode;
    document.body.classList.toggle("is-editing", editMode);
    blocks.forEach(block => {
      block.setAttribute("contenteditable", String(editMode));
      block.setAttribute("spellcheck", String(editMode));
    });
    actions.edit?.setAttribute("aria-pressed", String(editMode));
    if (actions.edit) actions.edit.textContent = editMode ? "结束编辑" : "编辑正文";
    if (editMode) {
      highlightMode = false;
      removeMode = false;
      actions.highlight?.setAttribute("aria-pressed", "false");
      actions["remove-highlight"]?.setAttribute("aria-pressed", "false");
      blocks[0].focus({ preventScroll: true });
      announce("已进入本地编辑模式");
    } else {
      hideEditorToolbar();
      editorRange = null;
      persist();
      announce("已保存本次文字修改");
    }
  }

  function setupEditor() {
    if (!editorEnabled || !actions.edit || !editorToolbar || !main) return;
    actions.edit.addEventListener("click", toggleEdit);
    actions.undo?.addEventListener("click", () => runEditorCommand("undo"));
    actions.redo?.addEventListener("click", () => runEditorCommand("redo"));
    editorToolbar.addEventListener("pointerdown", event => {
      if (event.target.closest("button")) event.preventDefault();
    });
    editorToolbar.querySelectorAll("[data-command]").forEach(control => {
      const apply = () => runEditorCommand(control.dataset.command, control.dataset.value || control.value || null);
      if (control.matches("select,input")) control.addEventListener("change", apply);
      else control.addEventListener("click", apply);
    });
    main.addEventListener("input", event => {
      if (event.target.closest?.("[data-editable]")) persist();
    });
  }

  function addHighlight(rangeOverride = null) {
    const range = rangeOverride || selectionRange() || savedRange;
    savedRange = null;
    const text = range?.toString().trim() || "";
    if (!range || range.collapsed || !text || !main?.contains(range.commonAncestorContainer)) {
      highlightMode = !highlightMode;
      removeMode = false;
      actions.highlight?.setAttribute("aria-pressed", String(highlightMode));
      actions["remove-highlight"]?.setAttribute("aria-pressed", "false");
      if (actions.highlight) actions.highlight.textContent = highlightMode ? "结束标记" : "标记选中文字";
      if (actions["remove-highlight"]) actions["remove-highlight"].textContent = "移除已标记";
      announce(highlightMode ? "请框选要标记的文字" : "已结束标记");
      return;
    }
    const start = range.startContainer.nodeType === Node.ELEMENT_NODE ? range.startContainer : range.startContainer.parentElement;
    const end = range.endContainer.nodeType === Node.ELEMENT_NODE ? range.endContainer : range.endContainer.parentElement;
    const startBlock = start?.closest?.("p, li, td, th, h1, h2, h3, h4, summary, figcaption");
    const endBlock = end?.closest?.("p, li, td, th, h1, h2, h3, h4, summary, figcaption");
    if (!startBlock || startBlock !== endBlock) { announce("请只框选同一段中的连续文字"); return; }
    if (start?.closest(".user-highlight")) { announce("所选文字已有标记"); return; }
    const wrapper = document.createElement("span");
    wrapper.className = "user-highlight";
    wrapper.append(range.extractContents());
    range.insertNode(wrapper);
    window.getSelection()?.removeAllRanges();
    persist();
    announce("已标记选中文字");
  }

  function clearTarget() {
    targetHighlight?.classList.remove("is-target");
    targetHighlight = null;
  }

  function removeHighlight() {
    const selection = window.getSelection();
    const start = selection?.rangeCount ? selection.getRangeAt(0).startContainer : null;
    const element = start?.nodeType === Node.ELEMENT_NODE ? start : start?.parentElement;
    const highlight = targetHighlight || element?.closest?.(".user-highlight");
    if (!highlight) {
      removeMode = !removeMode;
      highlightMode = false;
      actions["remove-highlight"]?.setAttribute("aria-pressed", String(removeMode));
      actions.highlight?.setAttribute("aria-pressed", "false");
      if (actions["remove-highlight"]) actions["remove-highlight"].textContent = removeMode ? "结束移除" : "移除已标记";
      if (actions.highlight) actions.highlight.textContent = "标记选中文字";
      announce(removeMode ? "请点击要移除的标记文字" : "已结束移除");
      return;
    }
    const parent = highlight.parentNode;
    highlight.replaceWith(...highlight.childNodes);
    parent.normalize();
    clearTarget();
    persist();
    removeMode = false;
    actions["remove-highlight"]?.setAttribute("aria-pressed", "false");
    if (actions["remove-highlight"]) actions["remove-highlight"].textContent = "移除已标记";
    announce("已移除标记");
  }

  function toggleFocus() {
    const focused = document.body.classList.toggle("is-focused");
    actions.focus?.setAttribute("aria-pressed", String(focused));
    if (actions.focus) actions.focus.textContent = focused ? "显示全部" : "聚焦重点";
    try { localStorage.setItem(focusStorageKey, focused ? "1" : "0"); } catch (_) {}
    announce(focused ? "已聚焦各板块重点" : "已显示完整内容");
  }

  function exportIdentity() {
    const token = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    return `${baseKey}-copy-${token}`;
  }

  function saveCopy() {
    if (!interactive) return;
    clearTarget();
    persist();
    const clone = document.documentElement.cloneNode(true);
    clone.dataset.documentKey = exportIdentity();
    clone.dataset.contentVersion = "v1";
    clone.querySelector("body")?.classList.remove("is-focused", "is-editing");
    clone.querySelectorAll("[data-editable]").forEach(node => {
      node.removeAttribute("contenteditable");
      node.removeAttribute("spellcheck");
    });
    const clonedEditorToolbar = clone.querySelector("[data-editor-toolbar]");
    if (clonedEditorToolbar) clonedEditorToolbar.hidden = true;
    clone.querySelectorAll(".is-target").forEach(node => node.classList.remove("is-target"));
    const blob = new Blob([`<!doctype html>\n${clone.outerHTML}`], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${(document.title || "document").replace(/[\\/:*?"<>|]+/g, "-")}-修改副本.html`;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    announce("已生成修改副本");
  }

  function updateReadingProgress() {
    if (!readingProgress) return;
    const scroller = activeRoom || document.scrollingElement || document.documentElement;
    const available = Math.max(0, scroller.scrollHeight - scroller.clientHeight);
    const percent = available ? Math.min(100, Math.max(0, scroller.scrollTop / available * 100)) : 0;
    readingProgress.style.width = `${percent}%`;
  }

  function clearSearchHits() {
    searchHits.forEach(node => node.classList.remove("search-hit", "is-current"));
    searchHits = [];
    searchIndex = -1;
    if (searchCount) searchCount.textContent = "";
  }

  function roomForNode(node) {
    return node?.closest?.("[data-section]") || null;
  }

  function showSearchHit(index) {
    if (!searchHits.length) return;
    searchIndex = (index + searchHits.length) % searchHits.length;
    searchHits.forEach(node => node.classList.remove("is-current"));
    const hit = searchHits[searchIndex];
    const room = roomForNode(hit);
    if (room && activateSection) activateSection(room, false);
    hit.classList.add("is-current");
    const scroller = room || document.scrollingElement;
    if (room && scroller) {
      const top = Math.max(0, hit.offsetTop - 24);
      scroller.scrollTo({ top, behavior: "smooth" });
    } else {
      hit.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    if (searchCount) searchCount.textContent = `${searchIndex + 1} / ${searchHits.length}`;
  }

  function runSearch() {
    clearSearchHits();
    const query = searchInput?.value.trim().toLocaleLowerCase();
    if (!query || !main) return;
    const nodes = [...main.querySelectorAll("h1, h2, h3, h4, h5, h6, p, li, td, th, summary, figcaption, .annotation-box__title, .semantic-note__title")];
    searchHits = nodes.filter(node => node.textContent.toLocaleLowerCase().includes(query));
    searchHits.forEach(node => node.classList.add("search-hit"));
    if (!searchHits.length) {
      if (searchCount) searchCount.textContent = "未找到";
      return;
    }
    showSearchHit(0);
  }

  function setupSearch() {
    if (!searchEnabled) return false;
    if (!searchPanel || !searchInput || !actions.search || !actions["search-next"] || !actions["search-prev"] || !actions["search-close"]) return false;
    actions.search.addEventListener("click", () => {
      searchPanel.hidden = !searchPanel.hidden;
      actions.search.setAttribute("aria-pressed", String(!searchPanel.hidden));
      if (!searchPanel.hidden) window.setTimeout(() => searchInput.focus(), 0);
      else clearSearchHits();
    });
    actions["search-close"].addEventListener("click", () => {
      searchPanel.hidden = true;
      actions.search.setAttribute("aria-pressed", "false");
      clearSearchHits();
    });
    actions["search-next"].addEventListener("click", () => showSearchHit(searchIndex + 1));
    actions["search-prev"].addEventListener("click", () => showSearchHit(searchIndex - 1));
    let timer = null;
    searchInput.addEventListener("input", () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(runSearch, 180);
    });
    searchInput.addEventListener("keydown", event => {
      if (event.key === "Enter") { event.preventDefault(); showSearchHit(searchIndex + (event.shiftKey ? -1 : 1)); }
      if (event.key === "Escape") actions["search-close"].click();
    });
    return true;
  }

  function setupNavigation() {
    if (!navigationEnabled) return false;
    const nav = document.querySelector(".section-nav");
    const roomStack = document.querySelector(".room-stack");
    const links = [...document.querySelectorAll(".section-nav a[href^='#']")];
    const pairs = links.map(link => [link, document.querySelector(link.getAttribute("href"))]).filter(([, section]) => section && roomStack?.contains(section));
    if (!nav || !roomStack || !pairs.length) return false;
    const setCurrent = active => links.forEach(link => link.setAttribute("aria-current", String(link === active)));
    const activate = (link, updateHistory) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target || !roomStack.contains(target)) return;
      pairs.forEach(([, section]) => {
        const active = section === target;
        section.classList.toggle("is-active", active);
        section.toggleAttribute("aria-hidden", !active);
      });
      activeRoom = target;
      setCurrent(link);
      if (updateHistory) history.pushState(null, "", link.getAttribute("href"));
      updateReadingProgress();
    };
    activateSection = (section, updateHistory = false) => {
      const pair = pairs.find(([, candidate]) => candidate === section);
      if (pair) activate(pair[0], updateHistory);
    };
    links.forEach(link => link.addEventListener("click", event => {
      event.preventDefault();
      activate(link, true);
    }));
    const fromHash = () => pairs.find(([link]) => link.getAttribute("href") === location.hash)?.[0] || pairs[0]?.[0];
    const initial = fromHash();
    if (initial) activate(initial, false);
    window.addEventListener("popstate", () => { const link = fromHash(); if (link) activate(link, false); });
    pairs.forEach(([, section]) => section.addEventListener("scroll", updateReadingProgress, { passive: true }));
    return true;
  }

  try {
    const saved = interactive && (localStorage.getItem(storageKey) || localStorage.getItem(legacyStorageKey));
    if (saved && main) main.innerHTML = saved;
    if (focusEnabled) {
      const focused = localStorage.getItem(focusStorageKey) === "1";
      document.body.classList.toggle("is-focused", focused);
      actions.focus?.setAttribute("aria-pressed", String(focused));
      if (actions.focus) actions.focus.textContent = focused ? "显示全部" : "聚焦重点";
    }
  } catch (_) {}

  if (reviewEnabled || editorEnabled) {
    document.addEventListener("selectionchange", () => {
      const range = selectionRange();
      if (reviewEnabled && range) savedRange = range;
      const editingRange = editorEnabled ? rememberEditorRange() : null;
      if (editingRange) positionEditorToolbar(editingRange);
      else if (editMode && !editorToolbar?.matches(":focus-within")) hideEditorToolbar();
    });
  }
  if (focusEnabled) actions.focus?.addEventListener("click", toggleFocus);
  if (reviewEnabled) {
    main?.addEventListener("click", event => {
      clearTarget();
      const highlight = event.target.closest?.(".user-highlight");
      if (highlight && removeMode) { targetHighlight = highlight; removeHighlight(); }
      else if (highlight) { targetHighlight = highlight; highlight.classList.add("is-target"); }
    });
    const addOnSelection = () => window.setTimeout(() => { const range = selectionRange(); if (range) addHighlight(range); }, 0);
    main?.addEventListener("mouseup", () => { if (highlightMode) addOnSelection(); });
    main?.addEventListener("touchend", () => { if (highlightMode) addOnSelection(); }, { passive: true });
    actions.highlight?.addEventListener("click", addHighlight);
    actions["remove-highlight"]?.addEventListener("click", removeHighlight);
  }
  actions.print?.addEventListener("click", () => window.print());
  actions.top?.addEventListener("click", () => {
    const scroller = activeRoom || document.scrollingElement;
    scroller?.scrollTo?.({ top: 0, behavior: "smooth" });
  });
  if (interactive) actions["save-copy"]?.addEventListener("click", saveCopy);
  setupEditor();
  if (setupNavigation()) root.classList.add("is-enhanced");
  window.addEventListener("scroll", updateReadingProgress, { passive: true });
  setupSearch();
  updateReadingProgress();

  window.personalHtmlQa = () => ({
    capabilities: [...capabilities],
    focused: document.body.classList.contains("is-focused"),
    currentSection: document.querySelector(".section-nav a[aria-current='true']")?.getAttribute("href") || null,
    searchOpen: Boolean(searchPanel && !searchPanel.hidden),
    searchHits: searchHits.length,
    highlightCount: main?.querySelectorAll(".user-highlight").length || 0,
    editableBlocks: editableRoots().length,
    editing: editMode,
    editorToolbarVisible: Boolean(editorToolbar && !editorToolbar.hidden),
    overflowing: [...document.querySelectorAll("main *, footer *")]
      .filter(node => node.scrollWidth - node.clientWidth > 1)
      .map(node => node.id || node.className || node.tagName.toLowerCase())
  });
})();
