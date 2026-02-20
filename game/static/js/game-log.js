/**
 * Game Log Panel - Real-time event log with filtering
 * Uses safe DOM manipulation (textContent, createElement) to prevent XSS
 */
class GameLog {
    constructor(gameId, username, containerId) {
        this.gameId = gameId;
        this.username = username;
        this.containerId = containerId || 'game-log-col';
        this.events = [];
        this.maxEvents = 200;
        this.filters = {
            categories: new Set(["rolls", "combat", "spells", "chat", "dm"]),
            characters: new Set(), // Empty = show all
        };
        this.isAtBottom = true;
        this.newEventsCount = 0;
        this.characters = [];

        this.init();
    }

    async init() {
        this.createPanel();
        this.bindEvents();
        await this.loadHistory();
    }

    createPanel() {
        var container = document.getElementById(this.containerId);
        if (!container) return;

        var header = this._createHeader();
        var entries = document.createElement("div");
        entries.className = "game-log-stream";
        entries.id = "game-log-entries";

        var indicator = document.createElement("div");
        indicator.className = "new-events-indicator";
        indicator.id = "new-events-indicator";
        indicator.appendChild(document.createTextNode("↓ "));
        var countSpan = document.createElement("span");
        countSpan.id = "new-events-count";
        countSpan.textContent = "0";
        indicator.appendChild(countSpan);
        indicator.appendChild(document.createTextNode(" new"));

        var filters = this._createFilters();

        container.appendChild(header);
        container.appendChild(entries);
        container.appendChild(indicator);
        container.appendChild(filters);

        // No expand button needed — column is always visible
        this.panel = container;
        this.entriesContainer = entries;
        this.newEventsIndicator = indicator;
        this.newEventsCountEl = countSpan;
        this.expandBtn = null;
    }

    _createHeader() {
        var header = document.createElement("div");
        header.className = "game-log-header";

        var title = document.createElement("h3");
        title.textContent = "Game Log";

        var toggle = document.createElement("button");
        toggle.className = "game-log-toggle";
        toggle.title = "Collapse";
        toggle.textContent = "=";

        header.appendChild(title);
        header.appendChild(toggle);
        return header;
    }

    _createFilters() {
        var filters = document.createElement("div");
        filters.className = "game-log-filters";

        var toggles = document.createElement("div");
        toggles.className = "filter-toggles";

        var categories = [
            { key: "rolls", icon: "🎲", title: "Dice Rolls" },
            { key: "combat", icon: "⚔️", title: "Combat" },
            { key: "spells", icon: "✨", title: "Spells" },
            { key: "chat", icon: "💬", title: "Chat" },
            { key: "dm", icon: "📢", title: "DM" },
        ];

        categories.forEach(function (cat) {
            var btn = document.createElement("button");
            btn.className = "filter-toggle active";
            btn.dataset.category = cat.key;
            btn.title = cat.title;
            btn.textContent = cat.icon;
            toggles.appendChild(btn);
        });

        var charFilter = document.createElement("div");
        charFilter.className = "character-filter";

        var charBtn = document.createElement("button");
        charBtn.className = "character-filter-btn";
        var charBtnText = document.createElement("span");
        charBtnText.textContent = "All Characters";
        var charBtnArrow = document.createElement("span");
        charBtnArrow.textContent = "▼";
        charBtn.appendChild(charBtnText);
        charBtn.appendChild(charBtnArrow);

        var charDropdown = document.createElement("div");
        charDropdown.className = "character-filter-dropdown";
        charDropdown.id = "character-dropdown";

        var allOption = this._createCharacterOption("all", "All Characters", true);
        charDropdown.appendChild(allOption);

        charFilter.appendChild(charBtn);
        charFilter.appendChild(charDropdown);

        filters.appendChild(toggles);
        filters.appendChild(charFilter);
        return filters;
    }

    _createCharacterOption(value, name, checked) {
        var label = document.createElement("label");
        label.className = "character-filter-option";

        var input = document.createElement("input");
        input.type = "checkbox";
        input.value = value;
        input.checked = checked;

        var span = document.createElement("span");
        span.textContent = name;

        label.appendChild(input);
        label.appendChild(span);
        return label;
    }

    bindEvents() {
        var self = this;

        // Toggle panel collapse (noop in column layout — toggle is hidden by CSS)
        var toggleBtn = this.panel.querySelector(".game-log-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", function () {
                self.panel.classList.toggle("collapsed");
            });
        }

        if (this.expandBtn) {
            this.expandBtn.addEventListener("click", function () {
                self.panel.classList.remove("collapsed");
            });
        }

        // Category filter toggles
        this.panel.querySelectorAll(".filter-toggle").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var category = btn.dataset.category;
                btn.classList.toggle("active");

                if (btn.classList.contains("active")) {
                    self.filters.categories.add(category);
                } else {
                    self.filters.categories.delete(category);
                }
                self.applyFilters();
            });
        });

        // Character filter dropdown
        var charBtn = this.panel.querySelector(".character-filter-btn");
        var charDropdown = this.panel.querySelector("#character-dropdown");

        charBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            charDropdown.classList.toggle("open");
        });

        document.addEventListener("click", function () {
            charDropdown.classList.remove("open");
        });

        charDropdown.addEventListener("click", function (e) {
            e.stopPropagation();
        });

        // Scroll detection for smart auto-scroll
        this.entriesContainer.addEventListener("scroll", function () {
            var el = self.entriesContainer;
            self.isAtBottom = (el.scrollHeight - el.scrollTop - el.clientHeight) < 50;

            if (self.isAtBottom) {
                self.clearNewEventsIndicator();
            }
        });

        // New events indicator click
        this.newEventsIndicator.addEventListener("click", function () {
            self.scrollToBottom();
            self.clearNewEventsIndicator();
        });
    }

    async loadHistory() {
        try {
            var response = await fetch("/game/" + this.gameId + "/log/");
            var data = await response.json();

            this.characters = data.characters;
            this.updateCharacterFilter();

            var self = this;
            data.events.forEach(function (event) {
                self.addEvent(event, false);
            });
            this.scrollToBottom();
        } catch (error) {
            console.error("Failed to load game log history:", error);
        }
    }

    updateCharacterFilter() {
        var dropdown = this.panel.querySelector("#character-dropdown");
        dropdown.replaceChildren();

        var allOption = this._createCharacterOption("all", "All Characters", true);
        dropdown.appendChild(allOption);

        var self = this;
        this.characters.forEach(function (char) {
            var option = self._createCharacterOption(char.id, char.name, true);
            dropdown.appendChild(option);
        });

        dropdown.querySelectorAll('input[type="checkbox"]').forEach(function (checkbox) {
            checkbox.addEventListener("change", function (e) {
                if (e.target.value === "all") {
                    var isChecked = e.target.checked;
                    dropdown.querySelectorAll('input[type="checkbox"]').forEach(function (cb) {
                        cb.checked = isChecked;
                    });
                    self.filters.characters.clear();
                } else {
                    var charId = parseInt(e.target.value);

                    if (e.target.checked) {
                        self.filters.characters.delete(charId);
                    } else {
                        self.filters.characters.add(charId);
                    }

                    var allCheckbox = dropdown.querySelector('input[value="all"]');
                    var allChecked = dropdown.querySelectorAll('input:not([value="all"]):checked').length ===
                                     dropdown.querySelectorAll('input:not([value="all"])').length;
                    allCheckbox.checked = allChecked;
                }

                self.updateCharacterButtonText();
                self.applyFilters();
            });
        });
    }

    updateCharacterButtonText() {
        var btn = this.panel.querySelector(".character-filter-btn span:first-child");
        var dropdown = this.panel.querySelector("#character-dropdown");
        var checkedCount = dropdown.querySelectorAll('input:not([value="all"]):checked').length;
        var totalCount = this.characters.length;

        if (checkedCount === totalCount || checkedCount === 0) {
            btn.textContent = "All Characters";
        } else if (checkedCount === 1) {
            var checked = dropdown.querySelector('input:not([value="all"]):checked');
            var name = checked.parentElement.querySelector("span").textContent;
            btn.textContent = name;
        } else {
            btn.textContent = checkedCount + " Characters";
        }
    }

    addEvent(event, isNew) {
        if (isNew === undefined) isNew = true;

        // Check max events limit
        if (this.events.length >= this.maxEvents) {
            this.events.shift();
            var firstEntry = this.entriesContainer.firstElementChild;
            if (firstEntry) firstEntry.remove();
        }

        this.events.push(event);

        var entry = this.createEventEntry(event);
        this.entriesContainer.appendChild(entry);

        if (isNew) {
            if (this.isAtBottom) {
                this.scrollToBottom();
            } else {
                this.newEventsCount++;
                this.showNewEventsIndicator();
            }
        }

        this.applyFiltersToEntry(entry, event);
    }

    createEventEntry(event) {
        var entry = document.createElement("div");
        entry.className = "log-entry";
        entry.dataset.category = event.category;
        entry.dataset.eventId = event.id;
        if (event.character_id) {
            entry.dataset.characterId = event.character_id;
        }

        var bar = document.createElement("div");
        bar.className = "log-entry-bar";

        var content = document.createElement("div");
        content.className = "log-entry-content";

        var header = document.createElement("div");
        header.className = "log-entry-header";

        var date = new Date(event.date);
        var time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        var timeSpan = document.createElement("span");
        timeSpan.className = "log-entry-time";
        timeSpan.textContent = time;

        var authorSpan = document.createElement("span");
        authorSpan.className = "log-entry-author";
        authorSpan.textContent = event.character_name || event.author_name;

        header.appendChild(timeSpan);
        header.appendChild(authorSpan);

        var message = document.createElement("div");
        message.className = "log-entry-message";
        message.textContent = event.message;

        content.appendChild(header);
        content.appendChild(message);

        var details = this.createDetailsElement(event);
        if (details) {
            content.appendChild(details);
        }

        entry.appendChild(bar);
        entry.appendChild(content);

        entry.addEventListener("click", function () {
            entry.classList.toggle("expanded");
        });

        return entry;
    }

    createDetailsElement(event) {
        if (!event.details) return null;

        var details = document.createElement("div");
        details.className = "log-entry-details";

        if (event.details.dice_notation) {
            this._addDetailLine(details, "Roll", event.details.dice_notation);
            this._addDetailLine(details, "Dice", "[" + event.details.individual_rolls.join(", ") + "]");
            if (event.details.modifier) {
                var mod = event.details.modifier > 0 ? "+" + event.details.modifier : event.details.modifier;
                this._addDetailLine(details, "Modifier", mod);
            }
            this._addDetailLine(details, "Total", event.details.total);
            if (event.details.roll_purpose) {
                this._addDetailLine(details, "Purpose", event.details.roll_purpose);
            }
        } else if (event.details.score !== undefined) {
            this._addDetailLine(details, "Ability", event.details.ability_type);
            this._addDetailLine(details, "Score", event.details.score);
            if (event.details.difficulty_class) {
                this._addDetailLine(details, "DC", event.details.difficulty_class);
            }
            var resultClass = event.details.result.toLowerCase() === "success" ? "success" : "failure";
            this._addDetailLine(details, "Result", event.details.result, resultClass);
        } else if (event.details.spell_name) {
            this._addDetailLine(details, "Spell", event.details.spell_name);
            this._addDetailLine(details, "Slot Level", event.details.slot_level);
            if (event.details.targets && event.details.targets.length) {
                this._addDetailLine(details, "Targets", event.details.targets.join(", "));
            }
        }

        return details.children.length > 0 ? details : null;
    }

    _addDetailLine(container, label, value, valueClass) {
        var p = document.createElement("p");

        var labelSpan = document.createElement("span");
        labelSpan.className = "label";
        labelSpan.textContent = label + ": ";

        var valueSpan = document.createElement("span");
        valueSpan.textContent = value;
        if (valueClass) {
            valueSpan.className = valueClass;
        }

        p.appendChild(labelSpan);
        p.appendChild(valueSpan);
        container.appendChild(p);
    }

    applyFilters() {
        var self = this;
        this.entriesContainer.querySelectorAll(".log-entry").forEach(function (entry) {
            var event = self.events.find(function (e) {
                return String(e.id) === entry.dataset.eventId;
            });
            if (event) {
                self.applyFiltersToEntry(entry, event);
            }
        });
    }

    applyFiltersToEntry(entry, event) {
        var visible = true;

        // Category filter
        if (!this.filters.categories.has(event.category)) {
            visible = false;
        }

        // Character filter (if filtering specific characters)
        if (visible && this.filters.characters.size > 0 && event.character_id) {
            if (this.filters.characters.has(event.character_id)) {
                visible = false;
            }
        }

        if (visible) {
            entry.classList.remove("hidden");
        } else {
            entry.classList.add("hidden");
        }
    }

    scrollToBottom() {
        this.entriesContainer.scrollTop = this.entriesContainer.scrollHeight;
    }

    showNewEventsIndicator() {
        this.newEventsCountEl.textContent = this.newEventsCount;
        this.newEventsIndicator.classList.add("visible");
    }

    clearNewEventsIndicator() {
        this.newEventsCount = 0;
        this.newEventsIndicator.classList.remove("visible");
    }

    // Called by WebSocket handler
    handleWebSocketEvent(event) {
        if (event.category) {
            this.addEvent({
                id: Date.now(),
                type: event.type,
                category: event.category,
                date: event.date,
                message: event.message,
                author_name: event.username,
                character_id: event.character_id,
                character_name: event.character_name,
                details: event.details || null,
            });
        }
    }
}

// Export for use in templates
window.GameLog = GameLog;
