/**
 * Quick Reference Panels - Draggable, collapsible D&D 5e SRD rule panels
 * Uses safe DOM manipulation (textContent, createElement) to prevent XSS
 */
class QuickReference {
    constructor() {
        this.panels = {};
        this.pinnedPanels = new Set();
        this.dragState = null;
        this.zIndexCounter = 200;

        this._loadState();
        this.init();
    }

    init() {
        this._createToolbar();
        this._bindGlobalEvents();
    }

    _createToolbar() {
        var toolbar = document.createElement("div");
        toolbar.className = "qr-toolbar";
        toolbar.id = "qr-toolbar";

        var buttons = [
            { key: "conditions", icon: "\uD83D\uDCA0", label: "Conditions" },
            { key: "actions", icon: "\u2694\uFE0F", label: "Actions" },
            { key: "cover", icon: "\uD83D\uDEE1\uFE0F", label: "Cover" },
            { key: "spellcasting", icon: "\u2728", label: "Spellcasting" },
        ];

        var self = this;
        buttons.forEach(function (btn) {
            var button = document.createElement("button");
            button.className = "qr-toolbar-btn";
            button.dataset.panel = btn.key;
            button.title = btn.label;

            var iconSpan = document.createElement("span");
            iconSpan.className = "qr-toolbar-icon";
            iconSpan.textContent = btn.icon;

            var labelSpan = document.createElement("span");
            labelSpan.className = "qr-toolbar-label";
            labelSpan.textContent = btn.label;

            button.appendChild(iconSpan);
            button.appendChild(labelSpan);

            button.addEventListener("click", function () {
                self.togglePanel(btn.key);
            });

            toolbar.appendChild(button);
        });

        document.body.appendChild(toolbar);
        this.toolbar = toolbar;
    }

    togglePanel(key) {
        if (this.panels[key]) {
            this._closePanel(key);
        } else {
            this._openPanel(key);
        }
        this._updateToolbarState();
    }

    _openPanel(key) {
        var content = QUICK_REFERENCE_DATA[key];
        if (!content) return;

        var panel = this._createPanel(key, content);
        document.body.appendChild(panel);
        this.panels[key] = panel;

        // Restore saved position or cascade
        var saved = this._getSavedPosition(key);
        if (saved) {
            panel.style.left = saved.left;
            panel.style.top = saved.top;
        } else {
            var offset = Object.keys(this.panels).length * 30;
            panel.style.left = (100 + offset) + "px";
            panel.style.top = (100 + offset) + "px";
        }

        this._bringToFront(panel);
    }

    _closePanel(key) {
        var panel = this.panels[key];
        if (panel) {
            panel.remove();
            delete this.panels[key];
            this.pinnedPanels.delete(key);
            this._saveState();
        }
    }

    _createPanel(key, data) {
        var self = this;
        var panel = document.createElement("div");
        panel.className = "qr-panel";
        panel.dataset.panelKey = key;
        panel.style.zIndex = this.zIndexCounter++;

        // Header (drag handle)
        var header = document.createElement("div");
        header.className = "qr-panel-header";

        var icon = document.createElement("span");
        icon.className = "qr-panel-icon";
        icon.textContent = data.icon;

        var title = document.createElement("span");
        title.className = "qr-panel-title";
        title.textContent = data.title;

        var controls = document.createElement("div");
        controls.className = "qr-panel-controls";

        var pinBtn = document.createElement("button");
        pinBtn.className = "qr-control-btn qr-pin-btn";
        pinBtn.title = "Pin panel";
        pinBtn.textContent = "\uD83D\uDCCC";
        pinBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            self._togglePin(key, pinBtn);
        });

        var collapseBtn = document.createElement("button");
        collapseBtn.className = "qr-control-btn qr-collapse-btn";
        collapseBtn.title = "Collapse";
        collapseBtn.textContent = "\u2013";
        collapseBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            panel.classList.toggle("qr-collapsed");
            collapseBtn.textContent = panel.classList.contains("qr-collapsed") ? "+" : "\u2013";
            collapseBtn.title = panel.classList.contains("qr-collapsed") ? "Expand" : "Collapse";
        });

        var closeBtn = document.createElement("button");
        closeBtn.className = "qr-control-btn qr-close-btn";
        closeBtn.title = "Close";
        closeBtn.textContent = "\u00D7";
        closeBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            self._closePanel(key);
            self._updateToolbarState();
        });

        controls.appendChild(pinBtn);
        controls.appendChild(collapseBtn);
        controls.appendChild(closeBtn);

        header.appendChild(icon);
        header.appendChild(title);
        header.appendChild(controls);

        // Body
        var body = document.createElement("div");
        body.className = "qr-panel-body";

        this._populateBody(body, data);

        panel.appendChild(header);
        panel.appendChild(body);

        // Drag events on header
        this._makeDraggable(panel, header);

        // Click to bring to front
        panel.addEventListener("mousedown", function () {
            self._bringToFront(panel);
        });

        return panel;
    }

    _populateBody(body, data) {
        if (data.sections) {
            var self = this;
            data.sections.forEach(function (section) {
                self._createSection(body, section);
            });
        }
    }

    _createSection(container, section) {
        var sectionEl = document.createElement("div");
        sectionEl.className = "qr-section";

        if (section.title) {
            var titleEl = document.createElement("div");
            titleEl.className = "qr-section-title";
            titleEl.textContent = section.title;

            // Collapsible sections
            var contentEl = document.createElement("div");
            contentEl.className = "qr-section-content";

            titleEl.addEventListener("click", function () {
                sectionEl.classList.toggle("qr-section-collapsed");
            });

            sectionEl.appendChild(titleEl);

            if (section.items) {
                var self = this;
                section.items.forEach(function (item) {
                    self._createItem(contentEl, item);
                });
            }

            if (section.text) {
                var textEl = document.createElement("p");
                textEl.className = "qr-text";
                textEl.textContent = section.text;
                contentEl.appendChild(textEl);
            }

            sectionEl.appendChild(contentEl);
        }

        container.appendChild(sectionEl);
    }

    _createItem(container, item) {
        var itemEl = document.createElement("div");
        itemEl.className = "qr-item";

        var nameEl = document.createElement("div");
        nameEl.className = "qr-item-name";
        nameEl.textContent = item.name;

        var descEl = document.createElement("div");
        descEl.className = "qr-item-desc";
        descEl.textContent = item.desc;

        itemEl.appendChild(nameEl);
        itemEl.appendChild(descEl);

        // Click to expand/collapse description
        itemEl.addEventListener("click", function () {
            itemEl.classList.toggle("qr-item-expanded");
        });

        container.appendChild(itemEl);
    }

    _makeDraggable(panel, handle) {
        var self = this;

        handle.addEventListener("mousedown", function (e) {
            if (e.target.closest(".qr-control-btn")) return;
            e.preventDefault();

            var rect = panel.getBoundingClientRect();
            self.dragState = {
                panel: panel,
                offsetX: e.clientX - rect.left,
                offsetY: e.clientY - rect.top,
            };
            panel.classList.add("qr-dragging");
        });

        handle.addEventListener("touchstart", function (e) {
            if (e.target.closest(".qr-control-btn")) return;
            e.preventDefault();

            var touch = e.touches[0];
            var rect = panel.getBoundingClientRect();
            self.dragState = {
                panel: panel,
                offsetX: touch.clientX - rect.left,
                offsetY: touch.clientY - rect.top,
            };
            panel.classList.add("qr-dragging");
        }, { passive: false });
    }

    _bindGlobalEvents() {
        var self = this;

        document.addEventListener("mousemove", function (e) {
            if (!self.dragState) return;
            e.preventDefault();

            var x = e.clientX - self.dragState.offsetX;
            var y = e.clientY - self.dragState.offsetY;

            // Keep within viewport
            x = Math.max(0, Math.min(x, window.innerWidth - 50));
            y = Math.max(0, Math.min(y, window.innerHeight - 50));

            self.dragState.panel.style.left = x + "px";
            self.dragState.panel.style.top = y + "px";
        });

        document.addEventListener("mouseup", function () {
            if (self.dragState) {
                self.dragState.panel.classList.remove("qr-dragging");
                self._saveState();
                self.dragState = null;
            }
        });

        document.addEventListener("touchmove", function (e) {
            if (!self.dragState) return;
            e.preventDefault();

            var touch = e.touches[0];
            var x = touch.clientX - self.dragState.offsetX;
            var y = touch.clientY - self.dragState.offsetY;

            x = Math.max(0, Math.min(x, window.innerWidth - 50));
            y = Math.max(0, Math.min(y, window.innerHeight - 50));

            self.dragState.panel.style.left = x + "px";
            self.dragState.panel.style.top = y + "px";
        }, { passive: false });

        document.addEventListener("touchend", function () {
            if (self.dragState) {
                self.dragState.panel.classList.remove("qr-dragging");
                self._saveState();
                self.dragState = null;
            }
        });

        // Close on Escape (non-pinned only)
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                var keys = Object.keys(self.panels);
                for (var i = keys.length - 1; i >= 0; i--) {
                    var key = keys[i];
                    if (!self.pinnedPanels.has(key)) {
                        self._closePanel(key);
                        self._updateToolbarState();
                        break;
                    }
                }
            }
        });
    }

    _togglePin(key, btnEl) {
        if (this.pinnedPanels.has(key)) {
            this.pinnedPanels.delete(key);
            btnEl.classList.remove("qr-pinned");
            btnEl.title = "Pin panel";
        } else {
            this.pinnedPanels.add(key);
            btnEl.classList.add("qr-pinned");
            btnEl.title = "Unpin panel";
        }
        this._saveState();
    }

    _bringToFront(panel) {
        panel.style.zIndex = this.zIndexCounter++;
    }

    _updateToolbarState() {
        var self = this;
        this.toolbar.querySelectorAll(".qr-toolbar-btn").forEach(function (btn) {
            var key = btn.dataset.panel;
            if (self.panels[key]) {
                btn.classList.add("qr-active");
            } else {
                btn.classList.remove("qr-active");
            }
        });
    }

    // Persistence via localStorage
    _saveState() {
        var state = {
            pinned: Array.from(this.pinnedPanels),
            positions: {},
        };
        var self = this;
        Object.keys(this.panels).forEach(function (key) {
            var panel = self.panels[key];
            state.positions[key] = {
                left: panel.style.left,
                top: panel.style.top,
            };
        });
        try {
            localStorage.setItem("qr_panel_state", JSON.stringify(state));
        } catch (e) {
            // localStorage not available
        }
    }

    _loadState() {
        try {
            var raw = localStorage.getItem("qr_panel_state");
            if (raw) {
                this._savedState = JSON.parse(raw);
            }
        } catch (e) {
            // localStorage not available
        }
    }

    _getSavedPosition(key) {
        if (this._savedState && this._savedState.positions && this._savedState.positions[key]) {
            return this._savedState.positions[key];
        }
        return null;
    }
}

/**
 * D&D 5e SRD 5.2.1 Quick Reference Data
 * Content is from the Systems Reference Document, licensed under CC-BY-4.0.
 */
var QUICK_REFERENCE_DATA = {
    conditions: {
        title: "Conditions",
        icon: "\uD83D\uDCA0",
        sections: [
            {
                title: "Conditions",
                items: [
                    { name: "Blinded", desc: "Can't see. Auto-fails checks requiring sight. Attack rolls against have advantage. Own attack rolls have disadvantage." },
                    { name: "Charmed", desc: "Can't attack the charmer or target them with harmful abilities. Charmer has advantage on social ability checks against the creature." },
                    { name: "Deafened", desc: "Can't hear. Auto-fails checks requiring hearing." },
                    { name: "Exhaustion", desc: "Cumulative levels: 1) Disadvantage on ability checks. 2) Speed halved. 3) Disadvantage on attacks and saves. 4) HP max halved. 5) Speed 0. 6) Death." },
                    { name: "Frightened", desc: "Disadvantage on ability checks and attacks while source of fear is in line of sight. Can't willingly move closer to the source." },
                    { name: "Grappled", desc: "Speed becomes 0. Ends if grappler is incapacitated or effect moves creature out of reach." },
                    { name: "Incapacitated", desc: "Can't take actions or reactions." },
                    { name: "Invisible", desc: "Impossible to see without magic or special sense. Attack rolls against have disadvantage. Own attack rolls have advantage." },
                    { name: "Paralyzed", desc: "Incapacitated, can't move or speak. Auto-fails STR and DEX saves. Attacks against have advantage. Hits within 5 ft are critical." },
                    { name: "Petrified", desc: "Transformed to solid substance. Incapacitated. Resistance to all damage. Auto-fails STR and DEX saves. Attacks against have advantage." },
                    { name: "Poisoned", desc: "Disadvantage on attack rolls and ability checks." },
                    { name: "Prone", desc: "Can only crawl unless standing up (costs half movement). Disadvantage on attacks. Melee attacks against have advantage; ranged have disadvantage." },
                    { name: "Restrained", desc: "Speed 0. Attacks against have advantage. Own attacks have disadvantage. Disadvantage on DEX saves." },
                    { name: "Stunned", desc: "Incapacitated, can't move, speaks falteringly. Auto-fails STR and DEX saves. Attacks against have advantage." },
                    { name: "Unconscious", desc: "Incapacitated, can't move or speak, unaware. Drops held items, falls prone. Auto-fails STR and DEX saves. Attacks have advantage. Hits within 5 ft are critical." },
                ],
            },
        ],
    },

    actions: {
        title: "Actions in Combat",
        icon: "\u2694\uFE0F",
        sections: [
            {
                title: "Standard Actions",
                items: [
                    { name: "Attack", desc: "Make a melee or ranged attack. Some features allow multiple attacks with this action." },
                    { name: "Cast a Spell", desc: "Cast a spell with a casting time of 1 action. Follow all normal spellcasting rules." },
                    { name: "Dash", desc: "Gain extra movement equal to your speed (after modifiers) for the current turn." },
                    { name: "Disengage", desc: "Your movement doesn't provoke opportunity attacks for the rest of the turn." },
                    { name: "Dodge", desc: "Until your next turn, attacks against you have disadvantage (if you can see the attacker), and you make DEX saves with advantage. Lost if incapacitated or speed drops to 0." },
                    { name: "Help", desc: "Give an ally advantage on their next ability check for the task you're helping with, or advantage on their next attack roll against a creature within 5 ft of you." },
                    { name: "Hide", desc: "Make a DEX (Stealth) check to become hidden. Must not be clearly visible and must have cover or be heavily obscured." },
                    { name: "Ready", desc: "Prepare a reaction with a trigger. When triggered, use your reaction to take the readied action. Readied spells require concentration." },
                    { name: "Search", desc: "Make a WIS (Perception) or INT (Investigation) check to find something." },
                    { name: "Use an Object", desc: "Interact with a second object (first interaction is free). Includes using items like potions, caltrops, or special equipment." },
                ],
            },
            {
                title: "Bonus Actions",
                items: [
                    { name: "Bonus Action", desc: "Only available if a class feature, spell, or ability grants one. Can only take one bonus action per turn. Choose timing if multiple are available." },
                    { name: "Two-Weapon Fighting", desc: "When you Attack with a light melee weapon, you can use a bonus action to attack with a different light melee weapon in your other hand (no ability modifier to damage unless negative)." },
                ],
            },
            {
                title: "Reactions",
                items: [
                    { name: "Opportunity Attack", desc: "When a hostile creature you can see leaves your reach, you can use your reaction to make one melee attack against it." },
                    { name: "Readied Action", desc: "Execute a previously readied action when its trigger occurs." },
                ],
            },
            {
                title: "Movement",
                items: [
                    { name: "Movement", desc: "Move up to your speed. Can break up movement around actions. Costs 1 ft per ft moved (2 ft per ft in difficult terrain)." },
                    { name: "Standing Up", desc: "Costs half your total movement speed. Cannot stand if you have 0 speed remaining." },
                    { name: "Crawling", desc: "While prone, every foot of movement costs 1 extra foot (2 extra in difficult terrain)." },
                ],
            },
        ],
    },

    cover: {
        title: "Cover Rules",
        icon: "\uD83D\uDEE1\uFE0F",
        sections: [
            {
                title: "Cover Types",
                items: [
                    { name: "Half Cover", desc: "+2 bonus to AC and DEX saving throws. Obstacle blocks at least half the target (low wall, furniture, another creature)." },
                    { name: "Three-Quarters Cover", desc: "+5 bonus to AC and DEX saving throws. About three-quarters covered (portcullis, arrow slit, thick tree trunk)." },
                    { name: "Total Cover", desc: "Can't be targeted directly by attacks or spells. Completely concealed by an obstacle." },
                ],
            },
            {
                title: "Cover Details",
                items: [
                    { name: "Determining Cover", desc: "Draw an imaginary line from the attacker's space to the target's space. If the line is blocked by a solid obstacle, the target has cover." },
                    { name: "Creatures as Cover", desc: "A creature provides half cover to targets behind it, whether the creature is friend or foe." },
                ],
            },
            {
                title: "Summary Table",
                items: [
                    { name: "Half Cover", desc: "AC +2, DEX saves +2" },
                    { name: "Three-Quarters Cover", desc: "AC +5, DEX saves +5" },
                    { name: "Total Cover", desc: "Cannot be targeted" },
                ],
            },
        ],
    },

    spellcasting: {
        title: "Spellcasting Rules",
        icon: "\u2728",
        sections: [
            {
                title: "Spell Slots",
                items: [
                    { name: "Using Spell Slots", desc: "Casting a spell expends a slot of the spell's level or higher. Cantrips don't require slots." },
                    { name: "Casting at Higher Level", desc: "Some spells have enhanced effects when cast using a higher-level slot, as noted in the spell description." },
                    { name: "Recovering Slots", desc: "A long rest restores all expended spell slots. Some classes have features that restore slots on a short rest." },
                ],
            },
            {
                title: "Components",
                items: [
                    { name: "Verbal (V)", desc: "Requires chanting mystical words. Cannot cast if silenced or in an area of silence." },
                    { name: "Somatic (S)", desc: "Requires gestures with at least one free hand. A hand holding a spellcasting focus can perform somatic components." },
                    { name: "Material (M)", desc: "Requires specific material components. A component pouch or spellcasting focus can substitute unless the component has a cost or is consumed." },
                ],
            },
            {
                title: "Concentration",
                items: [
                    { name: "Maintaining Concentration", desc: "Some spells require concentration. You can only concentrate on one spell at a time. Casting another concentration spell ends the first." },
                    { name: "Breaking Concentration", desc: "Taking damage: make a CON save (DC = 10 or half damage taken, whichever is higher). Being incapacitated or killed also breaks concentration." },
                    { name: "Duration", desc: "Concentration spells last up to their stated duration. You can end concentration at any time (no action required)." },
                ],
            },
            {
                title: "Casting Details",
                items: [
                    { name: "Casting Time", desc: "Most spells are 1 action. Bonus action spells restrict other spells that turn to cantrips with 1 action casting time." },
                    { name: "Range", desc: "Self, Touch, or a specific distance. You must have a clear path to the target unless noted otherwise." },
                    { name: "Targets", desc: "A spell specifies what it can target: creatures, objects, or a point of origin for an area of effect." },
                    { name: "Areas of Effect", desc: "Cone, Cube, Cylinder, Line, Sphere. Originate from a point unless the spell says otherwise." },
                    { name: "Saving Throws", desc: "Target makes a save against your Spell Save DC (8 + proficiency + spellcasting modifier). Success usually means reduced or no effect." },
                    { name: "Ritual Casting", desc: "Spells with the ritual tag can be cast as a ritual (takes 10 extra minutes) without expending a spell slot, if the caster has the ritual casting feature." },
                ],
            },
        ],
    },
};

// Export for use in templates
window.QuickReference = QuickReference;
