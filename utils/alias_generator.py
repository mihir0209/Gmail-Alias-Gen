import itertools
import random

def generate_aliases(email, count):
    if '@gmail.com' not in email.lower():
        raise ValueError("Only Gmail addresses are supported")
    
    local_part, domain = email.split('@')
    local_part = local_part.lower().replace('.', '')
    aliases = set()
    length = len(local_part)
    max_dots = length - 1

    # Generate dot variations
    for _ in range(count * 10):
        if len(aliases) >= count:
            break
        positions = sorted(random.sample(range(1, length), random.randint(0, max_dots)))
        new_local = []
        for idx, char in enumerate(local_part):
            new_local.append(char)
            if idx in positions and idx != length - 1:
                new_local.append('.')
        alias = ''.join(new_local) + f'@{domain}'
        aliases.add(alias)

    # Add +aliases if needed
    suffix_num = 1
    while len(aliases) < count:
        aliases.add(f"{local_part}+alias{suffix_num}@{domain}")
        aliases.add(f"{local_part}+{random.randint(1000,9999)}@{domain}")
        suffix_num += 1

    return list(aliases)[:count]
