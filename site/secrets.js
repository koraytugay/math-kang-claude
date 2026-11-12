// The site's secrets (GitHub token for exams, Neon connection string for practice) are locked in
// token.json with one password (site/lock-token.mjs). Shared by the exam page and the practice page.
"use strict";

const Secrets = {
    KEY: "mk.secrets",
    OLD_KEY: "mk.token",                     // before the database: only the GitHub token was saved

    /** The unlocked secrets remembered on this device, or null. */
    saved() {
        try {
            const s = JSON.parse(localStorage.getItem(this.KEY));
            if (s) return s;
            const t = localStorage.getItem(this.OLD_KEY);
            return t ? { github: t } : null;
        } catch { return null; }
    },
    save(s) {
        try { localStorage.setItem(this.KEY, JSON.stringify(s)); localStorage.removeItem(this.OLD_KEY); } catch { /* blocked */ }
    },
    forget() {
        try { localStorage.removeItem(this.KEY); localStorage.removeItem(this.OLD_KEY); } catch { /* blocked */ }
    },

    /** Unlock token.json with the password: {github, db}. Throws "Wrong password." */
    async unlock(password) {
        const r = await fetch("token.json", { cache: "no-store" });
        if (!r.ok) throw new Error("This site has no locked secrets yet (token.json is missing).");
        const box = await r.json();
        const b64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
        const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveKey"]);
        const key = await crypto.subtle.deriveKey(
            { name: "PBKDF2", hash: "SHA-256", salt: b64(box.salt), iterations: box.iter },
            base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
        let text;
        try {
            text = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(box.iv) }, key, b64(box.data)));
        } catch {
            throw new Error("Wrong password.");
        }
        return text.startsWith("{") ? JSON.parse(text) : { github: text };   // v1 files hold only the token
    },
};
