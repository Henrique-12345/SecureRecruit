import re


def mask_cpf(cpf: str | None) -> str | None:
    if not cpf:
        return cpf
    digits = re.sub(r"\D", "", cpf)
    if len(digits) < 2:
        return "***"
    return f"***.***.***-{digits[-2:]}"


def mask_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if not local:
        return f"*@{domain}"
    return f"{local[0]}{'*' * max(len(local) - 1, 1)}@{domain}"


def mask_phone(phone: str | None) -> str | None:
    if not phone:
        return phone
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "****"
    suffix = digits[-4:]
    if len(digits) >= 10:
        ddd = digits[-11:-9] if len(digits) >= 11 else digits[:2]
        return f"({ddd}) *****-{suffix}"
    return f"****-{suffix}"


def mask_name(name: str | None) -> str | None:
    if not name:
        return name
    parts = name.split()
    if not parts:
        return name
    masked = [parts[0]]
    for part in parts[1:]:
        masked.append(f"{part[0]}***" if part else "")
    return " ".join(masked)
