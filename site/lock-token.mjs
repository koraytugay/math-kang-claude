#!/usr/bin/env node
// Lock the GitHub token with a password and write site/token.json.
//
//     node site/lock-token.mjs
//
// It asks for the token and the password (nothing is shown while you type), or takes them from
// the MK_TOKEN and MK_PASSWORD environment variables. MK_DB (optional) is the Neon connection string
// of the limited mk_site user; then both secrets are locked together as {"github", "db"}. Only the locked
// token goes into token.json; the real token is never saved. The website unlocks it with the
// same password (PBKDF2-SHA256 + AES-GCM, the browser's built-in crypto).
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const ITER = 600_000;
const out = fileURLToPath(new URL("token.json", import.meta.url));

function ask(question) {
    return new Promise((resolve) => {
        process.stdout.write(question);
        const stdin = process.stdin;
        stdin.setRawMode(true);
        stdin.resume();
        stdin.setEncoding("utf8");
        let s = "";
        const onData = (ch) => {
            for (const c of ch) {
                if (c === "\r" || c === "\n") {
                    stdin.setRawMode(false); stdin.pause(); stdin.off("data", onData);
                    process.stdout.write("\n");
                    return resolve(s);
                }
                if (c === "\u0003") process.exit(1);                     // Ctrl-C
                if (c === "\u007f" || c === "\b") s = s.slice(0, -1);   // backspace
                else s += c;
            }
        };
        stdin.on("data", onData);
    });
}

const b64 = (u8) => Buffer.from(u8).toString("base64");

async function keyFor(password, salt, usage) {
    const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveKey"]);
    return crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt, iterations: ITER },
        base, { name: "AES-GCM", length: 256 }, false, [usage]);
}

const fromEnv = Boolean(process.env.MK_TOKEN && process.env.MK_PASSWORD);
const token = (fromEnv ? process.env.MK_TOKEN : await ask("GitHub token (starts with github_pat_): ")).trim();
if (!token.startsWith("github_pat_")) {
    console.error("That does not look like a fine-grained token (github_pat_...).");
    process.exit(1);
}
const password = fromEnv ? process.env.MK_PASSWORD : await ask("Password: ");
if (password.length < 16) {
    console.warn("Warning: a short password can be guessed. 4 random words (purple-river-lamp-seven) are much safer.");
}
if (!fromEnv && (await ask("Password again: ")) !== password) {
    console.error("The passwords are different.");
    process.exit(1);
}

const db = (process.env.MK_DB || "").trim();
if (db && !db.startsWith("postgres")) {
    console.error("MK_DB does not look like a Postgres connection string.");
    process.exit(1);
}
const plain = db ? JSON.stringify({ github: token, db }) : token;

const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const data = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv },
    await keyFor(password, salt, "encrypt"), new TextEncoder().encode(plain)));

// round trip, the same way the website does it
const back = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv },
    await keyFor(password, salt, "decrypt"), data));
if (back !== plain) throw new Error("round trip failed");

writeFileSync(out, JSON.stringify({ v: db ? 2 : 1, kdf: "PBKDF2-SHA256", iter: ITER, salt: b64(salt), iv: b64(iv), data: b64(data) }, null, 1) + "\n");
console.log(`Wrote ${out}. It only holds the locked token, so it is safe to commit.`);
