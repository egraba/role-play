/**
 * Keyboard shortcuts for the game page.
 *
 * Shortcuts:
 *   R   - Open dice roller (quick roll d20)
 *   A   - Open attack dialog (combat)
 *   S   - Cast spell (combat)
 *   E   - End turn / Next turn (DM)
 *   I   - Jump to initiative tracker
 *   C   - Open character sheet
 *   Esc - Close open modals
 *   ?   - Toggle shortcuts help
 */
class KeyboardShortcuts {
    constructor() {
        this.helpModalId = 'keyboard-shortcuts-modal';
        this.highlightTimeout = null;
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    /** Returns true when an input element has focus. */
    isInputFocused() {
        const el = document.activeElement;
        if (!el) return false;
        const tag = el.tagName;
        return (
            tag === 'INPUT' ||
            tag === 'TEXTAREA' ||
            tag === 'SELECT' ||
            el.isContentEditable
        );
    }

    /** Returns true when any game modal is visible. */
    isGameModalOpen() {
        const modals = document.querySelectorAll('.rpg-modal.active');
        for (const modal of modals) {
            if (modal.id !== this.helpModalId) return true;
        }
        return false;
    }

    handleKeydown(e) {
        // Escape always works
        if (e.key === 'Escape') {
            const helpModal = document.getElementById(this.helpModalId);
            if (helpModal && helpModal.classList.contains('active')) {
                helpModal.classList.remove('active');
                e.stopPropagation();
            }
            return;
        }

        // Don't fire shortcuts when typing in inputs
        if (this.isInputFocused()) return;

        // Don't fire with modifier keys (allow Shift for ?)
        if (e.ctrlKey || e.metaKey || e.altKey) return;

        // Don't fire if a game modal is open
        if (this.isGameModalOpen()) return;

        switch (e.key) {
            case 'r':
            case 'R':
                this.openDiceRoller(e);
                break;
            case 'a':
            case 'A':
                this.openAttack(e);
                break;
            case 's':
            case 'S':
                this.castSpell(e);
                break;
            case 'e':
            case 'E':
                this.endTurn(e);
                break;
            case 'i':
            case 'I':
                this.jumpToInitiative(e);
                break;
            case 'c':
            case 'C':
                this.openCharacterSheet(e);
                break;
            case '?':
                this.toggleHelp(e);
                break;
        }
    }

    // ── Actions ──────────────────────────────────────────────

    /** Open the dice roller modal via the existing HTMX button. */
    openDiceRoller(e) {
        e.preventDefault();
        const btn = document.querySelector('#player-actions [hx-get*="dice-roller"]');
        if (btn) btn.click();
    }

    /** Open the attack modal in combat. */
    openAttack(e) {
        e.preventDefault();
        const btn = document.querySelector('.action-btn[hx-get*="attack"]');
        if (btn && !btn.classList.contains('disabled') && !btn.hasAttribute('disabled')) {
            btn.click();
        }
    }

    /** Click the Cast Spell action button in combat. */
    castSpell(e) {
        e.preventDefault();
        const btns = document.querySelectorAll('#action-panel .action-btn');
        for (const btn of btns) {
            const name = btn.querySelector('.action-name');
            if (name && name.textContent.trim().toLowerCase().includes('cast')) {
                if (!btn.classList.contains('disabled') && !btn.hasAttribute('disabled')) {
                    btn.click();
                }
                return;
            }
        }
    }

    /** End the current turn (DM: Next Turn). */
    endTurn(e) {
        e.preventDefault();
        // DM: submit the Next Turn form
        const nextTurnBtn = document.querySelector('.dm-controls .btn-primary[type="submit"]');
        if (nextTurnBtn) {
            nextTurnBtn.click();
            return;
        }
    }

    /** Scroll to and briefly highlight the initiative tracker. */
    jumpToInitiative(e) {
        e.preventDefault();
        const tracker = document.getElementById('initiative-tracker');
        if (!tracker) return;

        tracker.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Brief highlight effect
        tracker.style.transition = 'box-shadow 0.3s ease';
        tracker.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.6)';
        if (this.highlightTimeout) clearTimeout(this.highlightTimeout);
        this.highlightTimeout = setTimeout(() => {
            tracker.style.boxShadow = '';
        }, 1500);
    }

    /** Open the current player's character sheet in a new tab. */
    openCharacterSheet(e) {
        e.preventDefault();
        // Find the character link marked "(played by you)"
        const markers = document.querySelectorAll('#characters .text-muted');
        for (const span of markers) {
            if (span.textContent.includes('played by you')) {
                const link = span.closest('p')?.querySelector('a');
                if (link) {
                    window.open(link.href, '_blank');
                }
                return;
            }
        }
    }

    /** Toggle the keyboard shortcuts help modal. */
    toggleHelp(e) {
        e.preventDefault();
        const modal = document.getElementById(this.helpModalId);
        if (modal) {
            modal.classList.toggle('active');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.keyboardShortcuts = new KeyboardShortcuts();
});
