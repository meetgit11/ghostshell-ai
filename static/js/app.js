/**
 * GhostShell — Frontend Logic
 * Handles API communication, UI state, typewriter effect, and atmospheric particles.
 * No user data is stored or sent to third parties.
 */

(function () {
    "use strict";

    // -----------------------------------------------------------------------
    // DOM References
    // -----------------------------------------------------------------------
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const statusIndicator = $("#status-indicator");
    const statusText = $("#status-text");
    const setupBanner = $("#setup-banner");
    const setupInstructions = $("#setup-instructions");
    const errorDisplay = $("#error-display");
    const errorText = $("#error-text");
    const errorDismiss = $("#error-dismiss");

    // Explainer
    const commandInput = $("#command-input");
    const explainBtn = $("#explain-btn");
    const explainOutput = $("#explain-output");
    const explainText = $("#explain-text");
    const copyExplainBtn = $("#copy-explain-btn");

    // Story
    const themeInput = $("#theme-input");
    const storyBtn = $("#story-btn");
    const storyOutput = $("#story-output");
    const storyText = $("#story-text");
    const copyStoryBtn = $("#copy-story-btn");

    // -----------------------------------------------------------------------
    // Ghost Particles
    // -----------------------------------------------------------------------
    function initParticles() {
        const container = $("#particles");
        const count = 15;
        for (let i = 0; i < count; i++) {
            const p = document.createElement("div");
            p.className = "particle";
            p.style.left = Math.random() * 100 + "%";
            p.style.animationDelay = Math.random() * 8 + "s";
            p.style.animationDuration = 6 + Math.random() * 6 + "s";
            p.style.width = p.style.height = 2 + Math.random() * 4 + "px";
            container.appendChild(p);
        }
    }

    // -----------------------------------------------------------------------
    // Tabs
    // -----------------------------------------------------------------------
    function initTabs() {
        $$(".tab").forEach((tab) => {
            tab.addEventListener("click", () => {
                $$(".tab").forEach((t) => t.classList.remove("active"));
                $$(".panel").forEach((p) => p.classList.remove("active"));
                tab.classList.add("active");
                const panelId = "panel-" + tab.dataset.tab;
                const panel = $("#" + panelId);
                if (panel) {
                    panel.classList.remove("hidden");
                    panel.classList.add("active");
                }
            });
        });
    }

    // -----------------------------------------------------------------------
    // Status & Health Check
    // -----------------------------------------------------------------------
    async function checkHealth() {
        try {
            const resp = await fetch("/api/health");
            const data = await resp.json();

            if (data.status === "ready") {
                setStatus("ready", `Connected — ${data.model_name}`);
                setupBanner.classList.add("hidden");
            } else {
                setStatus("error", "Setup required");
                showSetupInstructions(data);
            }
        } catch {
            setStatus("error", "Cannot reach server");
        }
    }

    function setStatus(state, text) {
        statusIndicator.className = "status-indicator status-" + state;
        statusText.textContent = text;
    }

    function showSetupInstructions(data) {
        let html = "";
        if (!data.ollama_running) {
            html += `<p>1. Install Ollama from <a href="https://ollama.com" target="_blank" rel="noopener" style="color:var(--green-bright)">ollama.com</a></p>`;
            html += `<p>2. Start Ollama: <code>ollama serve</code></p>`;
            html += `<p>3. Pull a model: <code>ollama pull ${data.model_name}</code></p>`;
        } else if (!data.model_available) {
            html += `<p>Ollama is running but the model <code>${data.model_name}</code> is not installed.</p>`;
            html += `<p>Pull it with: <code>ollama pull ${data.model_name}</code></p>`;
        }
        html += `<p style="margin-top:0.5rem;opacity:0.7">Then refresh this page.</p>`;
        setupInstructions.innerHTML = html;
        setupBanner.classList.remove("hidden");
    }

    // -----------------------------------------------------------------------
    // Error Handling
    // -----------------------------------------------------------------------
    let errorTimeout = null;

    function showError(message) {
        errorText.textContent = message;
        errorDisplay.classList.remove("hidden");
        clearTimeout(errorTimeout);
        errorTimeout = setTimeout(() => {
            errorDisplay.classList.add("hidden");
        }, 8000);
    }

    function hideError() {
        errorDisplay.classList.add("hidden");
        clearTimeout(errorTimeout);
    }

    // -----------------------------------------------------------------------
    // Typewriter Effect
    // -----------------------------------------------------------------------
    let activeTypewriter = null;

    function typewriter(element, text, speed = 12) {
        if (activeTypewriter) {
            clearInterval(activeTypewriter.interval);
            if (activeTypewriter.cursor) activeTypewriter.cursor.remove();
            activeTypewriter = null;
        }

        return new Promise((resolve) => {
            element.textContent = "";
            const cursor = document.createElement("span");
            cursor.className = "cursor-blink";
            element.appendChild(cursor);

            let i = 0;
            const interval = setInterval(() => {
                if (i < text.length) {
                    const charNode = document.createTextNode(text[i]);
                    element.insertBefore(charNode, cursor);
                    i++;
                } else {
                    clearInterval(interval);
                    activeTypewriter = null;
                    setTimeout(() => {
                        cursor.remove();
                        resolve();
                    }, 1200);
                }
            }, speed);

            activeTypewriter = { interval, cursor, resolve };
        });
    }

    // -----------------------------------------------------------------------
    // Clipboard Helper
    // -----------------------------------------------------------------------
    async function copyToClipboard(button, text) {
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            const orig = button.textContent;
            button.textContent = "✓ Copied!";
            button.style.borderColor = "var(--green-bright)";
            button.style.color = "var(--green-bright)";
            setTimeout(() => {
                button.textContent = orig;
                button.style.borderColor = "";
                button.style.color = "";
            }, 2000);
        } catch {
            showError("Could not copy to clipboard.");
        }
    }

    // -----------------------------------------------------------------------
    // Suggestion Chips
    // -----------------------------------------------------------------------
    function initChips() {
        $$(".chip").forEach((chip) => {
            chip.addEventListener("click", () => {
                const targetId = chip.dataset.target;
                const val = chip.dataset.value;
                const input = $("#" + targetId);
                if (input) {
                    input.value = val;
                    input.focus();
                    if (targetId === "command-input") {
                        explainCommand();
                    } else if (targetId === "theme-input") {
                        generateStory();
                    }
                }
            });
        });
    }

    // -----------------------------------------------------------------------
    // Loading State with Elapsed Timer
    // -----------------------------------------------------------------------
    function showLoadingBox(outputEl, textEl, title, subtitle) {
        outputEl.classList.remove("hidden");
        textEl.innerHTML = `
            <div class="loading-box">
                <span class="loading-ghost" aria-hidden="true">👻</span>
                <div class="loading-details">
                    <span class="loading-title">${title}</span>
                    <span class="loading-subtitle">${subtitle}</span>
                    <span class="loading-timer">Elapsed: <strong id="elapsed-sec">0</strong>s</span>
                </div>
            </div>
        `;
        const startTime = Date.now();
        const timerInterval = setInterval(() => {
            const timerEl = textEl.querySelector("#elapsed-sec");
            if (timerEl) {
                timerEl.textContent = Math.floor((Date.now() - startTime) / 1000);
            }
        }, 1000);

        return () => clearInterval(timerInterval);
    }

    // -----------------------------------------------------------------------
    // Button State
    // -----------------------------------------------------------------------
    function setLoading(btn, loading) {
        const textEl = btn.querySelector(".btn-text");
        const loadingEl = btn.querySelector(".btn-loading");
        btn.disabled = loading;
        if (loading) {
            textEl.classList.add("hidden");
            loadingEl.classList.remove("hidden");
        } else {
            textEl.classList.remove("hidden");
            loadingEl.classList.add("hidden");
        }
    }

    // -----------------------------------------------------------------------
    // API Calls
    // -----------------------------------------------------------------------
    async function explainCommand() {
        const command = commandInput.value.trim();
        if (!command) {
            showError("Please enter a command to explain.");
            commandInput.focus();
            return;
        }

        setLoading(explainBtn, true);
        hideError();
        const stopLoading = showLoadingBox(
            explainOutput,
            explainText,
            "Channeling the command spirits...",
            "Local CPU inference in progress — typically takes 30–60 seconds"
        );

        try {
            const resp = await fetch("/api/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command }),
            });
            const data = await resp.json();
            stopLoading();

            if (!resp.ok) {
                explainOutput.classList.add("hidden");
                showError(data.error || "The spirits encountered a dark anomaly.");
                return;
            }

            await typewriter(explainText, data.explanation);
        } catch (err) {
            stopLoading();
            explainOutput.classList.add("hidden");
            showError("Network error — lost connection to the GhostShell server.");
        } finally {
            setLoading(explainBtn, false);
        }
    }

    async function generateStory() {
        const theme = themeInput.value.trim();
        if (!theme) {
            showError("Please enter a theme for the ghost story.");
            themeInput.focus();
            return;
        }

        setLoading(storyBtn, true);
        hideError();
        const stopLoading = showLoadingBox(
            storyOutput,
            storyText,
            "Conjuring digital dread...",
            "Local CPU inference in progress — weaving a tale from the depths"
        );

        try {
            const resp = await fetch("/api/story", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ theme }),
            });
            const data = await resp.json();
            stopLoading();

            if (!resp.ok) {
                storyOutput.classList.add("hidden");
                showError(data.error || "The spirits encountered a dark anomaly.");
                return;
            }

            await typewriter(storyText, data.story);
        } catch (err) {
            stopLoading();
            storyOutput.classList.add("hidden");
            showError("Network error — lost connection to the GhostShell server.");
        } finally {
            setLoading(storyBtn, false);
        }
    }

    // -----------------------------------------------------------------------
    // Event Listeners
    // -----------------------------------------------------------------------
    explainBtn.addEventListener("click", explainCommand);
    storyBtn.addEventListener("click", generateStory);
    errorDismiss.addEventListener("click", hideError);

    if (copyExplainBtn) {
        copyExplainBtn.addEventListener("click", () => {
            copyToClipboard(copyExplainBtn, explainText.textContent);
        });
    }

    if (copyStoryBtn) {
        copyStoryBtn.addEventListener("click", () => {
            copyToClipboard(copyStoryBtn, storyText.textContent);
        });
    }

    commandInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") explainCommand();
    });
    themeInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") generateStory();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") hideError();
    });

    // -----------------------------------------------------------------------
    // Initialization
    // -----------------------------------------------------------------------
    initParticles();
    initTabs();
    initChips();
    checkHealth();
})();
