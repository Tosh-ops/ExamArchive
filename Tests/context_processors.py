def user_context(request):
    full = request.session.get('user_name', '')
    parts = full.strip().split() if full else []
    if not parts:
        initials = 'G'
    elif len(parts) == 1:
        initials = parts[0][:1].upper()
    else:
        initials = (parts[0][:1] + parts[-1][:1]).upper()

    return {
        'user_name': parts[0] if parts else 'Guest',
        'user_full_name': full or 'Guest',
        'user_initials': initials,
        'user_email': request.session.get('user_email', ''),
    }