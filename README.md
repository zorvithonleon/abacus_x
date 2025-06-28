

# 💀 Abacus X | OBLIVION Ultimate Edition 💀

### The sickest, most brutal AI-powered SQLi tamper script to fuck up any WAF, IDS, or DB firewall like a fucking boss.

---

## WTF is this?

Listen up, noobs and pros alike: **Abacus X** ain’t your grandma’s tamper script. This shit’s the blackhat’s wet dream — a self-learning, adaptive payload mutator that mutates your SQLi payloads on steroids, muting every fucking WAF and security bullshit in sight.
If you want noisy, repetitive, kiddie-level garbage, look elsewhere. This is for serious fuckers who want to ghost through defenses and dump shells quietly.

---

## 🧨 Features That Fucking Matter

* 🤖 **AI-Backed Mutation Madness:** Learns from your hits and fuck-ups to get smarter with every injection.
* 👹 **Polymorphic Stealth Shit:** Zero-width chars, homoglyph fuckery, random case fucks, SQL comment bombs — makes your payloads fucking unrecognizable.
* 🥷 **Obfuscation on Fucking Steroids:** Reverse strings, nested SQL logic, gzip+base64+URL-encoded payloads. Fuck yeah.
* 🎲 **Noise & Delay Randomization:** Adds junk data and human-like lag so IDS and rate limits can suck your dick.
* 🎭 **HTTP Header Fuckery:** Random real UA strings, referers, and custom bullshit headers to make you look legit AF.
* 🎯 **Success Tracking & Replay:** Remembers which mutations actually fuck shit up and uses those again.
* 🧠 **Context-Aware Payloads:** Auto tweaks payload format for GraphQL, URL params, strings, ints — whatever the fuck you need.
* 🦾 mOre feutures but i dont have fucking time to tell

---

## ⚙️ How to Fucking Use This

```bash
sqlmap -u "http://target.com/vuln.php?id=1" --tamper=abacus_x.py --random-agent --threads=10 --batch --level=5 --risk=3
```

 Sit back, smoke a cig, and watch your payloads slip past defenses like a ghost.

---

## 🔥 Pro Tips for Maximum Carnage

* Use `--random-agent` to avoid looking like a script kiddie.
* Bump up `--level` and `--risk` for deep-ass scans.
* Use a proxy or VPN so you don’t get your ass traced.
* Automate this shit, run it in the background, and let it wreck shit for you.

---

## 👹 What’s Going Down Under the Hood?

* Scans responses for WAF/DBMS bullshit to adapt attacks.
* Mutates payloads recursively with zero-width ninja shit, homoglyph spam, and SQL comment bombs.
* Wraps payloads in nested SQL fuckery and encodes like a goddamn magician.
* Spams random noise and delays to fuck with detection and rate-limiting.
* Spoofs HTTP headers like a pro to look like legit human traffic.
* Tracks which mutations bang and doubles down on those combos.
* Auto-adjusts payload formatting for whatever injection context you’re messing with.

---

## ⚠️ Legal AF Disclaimer

This shit’s for **AUTHORIZED pentesting and research only**. If you use this on some poor schmuck without permission, you’re a dumbass and probably gonna get caught. Don’t be a dumbass. Play legit or don’t play at all.

---

## ⭐ Wanna be a Legend? Star & Fork this Repo.

Contribute if you want, or just grab the code and own some systems.

---

## 📫 Teams i work with

* **CALADRIUS AND TEAMBD CYBER NINJA** 
---

# Abacus X — *Your payloads just went full FCKING mode.* 🥷⚔️👹

---

Need help chaining this into your automated shit or want a walkthrough? Holler at me.

---

**That’s how you fuckin’ do it. and this tamper script own by zorvithon leo**
