from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.db.models import Count
from .models import Paper, Badge, Notification, PaperReport


# ---------- Admin credentials ----------
ADMIN_IDENTIFIERS = {
    '+254718624338',
    '0718624338',
    '254718624338',
    'admin',
    'mutongahermes@gmail.com',
}


def _is_admin_identifier(value):
    if not value:
        return False
    v = value.strip().lower()
    if v.startswith('07') and len(v) == 10:
        v = '+254' + v[1:]
    if v.startswith('254') and len(v) == 12:
        v = '+' + v
    for a in ADMIN_IDENTIFIERS:
        al = a.strip().lower()
        if v == al or value.strip().lower() == al:
            return True
    return False


# ---------- Constants ----------
UNIVERSITIES = [
    ('uon', 'University of Nairobi'),
    ('ku', 'Kenyatta University'),
    ('strathmore', 'Strathmore University'),
    ('jkuat', 'JKUAT'),
    ('moi', 'Moi University'),
    ('egerton', 'Egerton University'),
    ('maseno', 'Maseno University'),
    ('tuk', 'Technical University of Kenya'),
    ('mmu', 'Multimedia University of Kenya'),
    ('daystar', 'Daystar University'),
    ('usiu', 'USIU Africa'),
    ('cuea', 'Catholic University of Eastern Africa'),
    ('anu', 'Africa Nazarene University'),
    ('mku', 'Mount Kenya University'),
    ('zetech', 'Zetech University'),
    ('riara', 'Riara University'),
    ('other', 'Other University'),
]

UNIVERSITY_CAMPUSES = {
    'uon': [('main', 'Main Campus'), ('kikuyu', 'Kikuyu Campus'), ('chiromo', 'Chiromo Campus'),
            ('lower_kabete', 'Lower Kabete Campus'), ('parklands', 'Parklands Campus'), ('kisumu', 'Kisumu Campus')],
    'ku': [('main', 'Main Campus (Thika)'), ('ruiru', 'Ruiru Campus'), ('parklands', 'Parklands Campus'),
           ('city', 'City Campus'), ('kericho', 'Kericho Campus'), ('nakuru', 'Nakuru Campus')],
    'strathmore': [('main', 'Main Campus (Madaraka)'), ('cbd', 'CBD Campus')],
    'jkuat': [('main', 'Main Campus (Juja)'), ('nairobi', 'Nairobi CBD Campus'), ('karen', 'Karen Campus'),
              ('mombasa', 'Mombasa Campus'), ('kisii', 'Kisii Campus')],
    'moi': [('main', 'Main Campus (Eldoret)'), ('town', 'Town Campus'), ('nairobi', 'Nairobi Campus')],
    'egerton': [('main', 'Main Campus (Njoro)'), ('nakuru', 'Nakuru Campus'), ('njoro', 'Njoro Campus')],
    'maseno': [('main', 'Main Campus'), ('kisumu', 'Kisumu Campus')],
    'tuk': [('main', 'Main Campus'), ('cbd', 'CBD Campus')],
    'mmu': [('main', 'Main Campus')],
    'daystar': [('athi_river', 'Athi River Campus'), ('nairobi', 'Nairobi Campus')],
    'usiu': [('main', 'Main Campus')],
    'cuea': [('main', 'Main Campus'), ('karen', 'Karen Campus')],
    'anu': [('main', 'Main Campus')],
    'mku': [('main', 'Main Campus (Thika)'), ('nairobi', 'Nairobi Campus'), ('mombasa', 'Mombasa Campus')],
    'zetech': [('main', 'Main Campus')],
    'riara': [('main', 'Main Campus')],
    'other': [('main', 'Main Campus'), ('other', 'Other')],
}

CAMPUSES = UNIVERSITY_CAMPUSES['uon']
REPORT_THRESHOLD = 5


def get_campuses_for(university_code):
    if not university_code:
        return CAMPUSES
    return UNIVERSITY_CAMPUSES.get(university_code, UNIVERSITY_CAMPUSES['other'])


def get_ai_suggestions(paper):
    related = Paper.objects.filter(course=paper.course, verified=True).exclude(id=paper.id).order_by('-downloads')[:4]
    prefix = paper.unit_code[:2] if len(paper.unit_code) >= 2 else paper.unit_code
    similar_unit = Paper.objects.filter(unit_code__startswith=prefix, verified=True).exclude(id=paper.id).order_by('-downloads')[:3]
    return {'related': related, 'similar_unit': similar_unit}


def generate_sample_questions(paper):
    return [
        f"Explain the core concept covered in {paper.unit_code} — {paper.title}.",
        f"Compare and contrast two approaches discussed in {paper.title}.",
        f"Given a scenario related to {paper.course}, describe how you would apply the principles of {paper.title}.",
        f"Identify and describe 3 key terms from {paper.unit_code} with examples.",
        f"Discuss the advantages and disadvantages of the approach used in {paper.title}.",
        f"Draw a diagram illustrating the process covered in {paper.unit_code} — {paper.year} paper.",
    ]


# ---------- Session helpers ----------
def get_user_name(request):
    return request.session.get('user_name', 'Guest')


def get_user_first_name(request):
    full = request.session.get('user_name', '')
    if not full:
        return 'Guest'
    return full.strip().split()[0]


def get_user_email(request):
    return request.session.get('user_email', '')


def get_user_initials(request):
    full = request.session.get('user_name', '')
    if not full:
        return 'G'
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0][:1].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def is_admin(request):
    return bool(request.session.get('is_admin', False))


def get_unread_notifications_count(request):
    user = get_user_name(request)
    if not user or user == 'Guest':
        return 0
    return Notification.objects.filter(
        models.Q(recipient_name=user) | models.Q(recipient_name='')
    ).filter(is_read=False, recipient_name=user).count()


# ---------- Landing ----------
def landing(request):
    return render(request, 'Tests/landing.html')


# ---------- Auth ----------
def login_view(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        contact = (request.POST.get('contact') or request.POST.get('phone') or '').strip()

        if not contact:
            contact = name

        request.session['user_name'] = name or contact or 'Student'
        request.session['user_email'] = contact

        if _is_admin_identifier(contact) or _is_admin_identifier(name):
            request.session['is_admin'] = True
        else:
            request.session['is_admin'] = False

        return redirect('home')
    return render(request, 'Tests/login.html')


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        contact = (request.POST.get('contact') or request.POST.get('phone') or '').strip()
        university = request.POST.get('university', '').strip()

        if not name or not contact or not university:
            return render(request, 'Tests/register.html', {
                'universities': UNIVERSITIES,
                'error': 'Name, phone/email and university are required.',
            })

        request.session['user_name'] = name
        request.session['user_email'] = contact
        request.session['user_university'] = university

        if _is_admin_identifier(contact) or _is_admin_identifier(name):
            request.session['is_admin'] = True
        else:
            request.session['is_admin'] = False

        return redirect('home')

    return render(request, 'Tests/register.html', {'universities': UNIVERSITIES})


def logout_view(request):
    request.session.flush()
    return redirect('landing')


def otp_view(request):
    return render(request, 'Tests/otp.html')


# ---------- Home ----------
def home(request):
    trending = Paper.objects.filter(verified=True).order_by('-downloads')[:3]
    recent = Paper.objects.order_by('-created_at')[:3]

    context = {
        'trending': trending,
        'recent': recent,
        'active': 'home',
        'user_name': get_user_first_name(request),
        'has_papers': Paper.objects.exists(),
        'is_admin': is_admin(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/home.html', context)


# ---------- Search ----------
def search(request):
    query = request.GET.get('q', '')
    university = request.GET.get('university', '')
    campus = request.GET.get('campus', '')
    year = request.GET.get('year', '')
    exam_type = request.GET.get('exam_type', '')
    verified_only = request.GET.get('verified', '')

    results = Paper.objects.all()

    if query:
        results = results.filter(unit_code__icontains=query) | \
                  results.filter(title__icontains=query) | \
                  results.filter(course__icontains=query)

    if university:
        results = results.filter(university=university)
    if campus:
        results = results.filter(campus=campus)
    if year:
        results = results.filter(year=year)
    if exam_type:
        results = results.filter(exam_type=exam_type)
    if verified_only == '1':
        results = results.filter(verified=True)

    years = Paper.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'query': query,
        'results': results,
        'result_count': results.count(),
        'active': 'search',
        'universities': UNIVERSITIES,
        'campuses': get_campuses_for(university),
        'years': years,
        'exam_types': Paper.EXAM_TYPE_CHOICES,
        'selected_university': university,
        'selected_campus': campus,
        'selected_year': year,
        'selected_exam_type': exam_type,
        'verified_only': verified_only,
        'has_filters': bool(university or campus or year or exam_type or verified_only),
        'is_admin': is_admin(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/search.html', context)


# ---------- Paper Detail ----------
def paper_detail(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    paper.downloads += 1
    paper.save()

    suggestions = get_ai_suggestions(paper)
    sample_questions = generate_sample_questions(paper) if request.GET.get('ai') == '1' else []

    context = {
        'paper': paper,
        'related': suggestions['related'],
        'similar_unit': suggestions['similar_unit'],
        'sample_questions': sample_questions,
        'show_ai': request.GET.get('ai') == '1',
        'active': 'home',
        'is_admin': is_admin(request),
        'can_delete': (paper.uploader_name == request.session.get('user_name', '')) or is_admin(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/paper_detail.html', context)


# ---------- Upload ----------
def upload(request):
    if request.method == 'POST':
        unit_code = request.POST.get('unit_code', '').strip()
        title = request.POST.get('title', '').strip()
        course = request.POST.get('course', '').strip()
        year = request.POST.get('year', '').strip()
        university = request.POST.get('university', 'uon')

        if not unit_code or not title or not course or not year:
            return render(request, 'Tests/upload.html', {
                'active': 'upload',
                'universities': UNIVERSITIES,
                'campuses': get_campuses_for(university),
                'exam_types': Paper.EXAM_TYPE_CHOICES,
                'user_name': get_user_name(request),
                'error': 'Unit code, course name, category, and year are required.',
                'unread_count': get_unread_notifications_count(request),
            })

        uploaded_file = request.FILES.get('paper_file') or request.FILES.get('paper_file_camera')

        Paper.objects.create(
            unit_code=unit_code,
            title=title,
            course=course,
            description=request.POST.get('description', ''),
            university=university,
            campus=request.POST.get('campus', 'main'),
            year=int(year),
            exam_type=request.POST.get('exam_type', 'final'),
            uploader_name=request.POST.get('uploader_name') or get_user_name(request),
            uploaded_file=uploaded_file,
            verified=False,
        )
        return redirect('upload_success')

    context = {
        'active': 'upload',
        'universities': UNIVERSITIES,
        'campuses': get_campuses_for('uon'),
        'exam_types': Paper.EXAM_TYPE_CHOICES,
        'user_name': get_user_name(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/upload.html', context)


def upload_success(request):
    return render(request, 'Tests/upload_success.html', {
        'active': 'upload',
        'unread_count': get_unread_notifications_count(request),
    })


# ---------- Profile ----------
def profile(request):
    context = {
        'active': 'profile',
        'points': 120,
        'uploads_count': Paper.objects.count(),
        'badges_count': Badge.objects.filter(earned=True).count(),
        'my_uploads': Paper.objects.all()[:3],
        'user_name': get_user_name(request),
        'user_first_name': get_user_first_name(request),
        'user_email': get_user_email(request),
        'user_initials': get_user_initials(request),
        'is_admin': is_admin(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/profile.html', context)


# ---------- Badges ----------
def badges(request):
    all_badges = Badge.objects.all()
    context = {
        'active': 'badges',
        'badges': all_badges,
        'earned_count': all_badges.filter(earned=True).count(),
        'total_count': all_badges.count(),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/badges.html', context)


# ---------- Notifications ----------
def notifications(request):
    user = get_user_name(request)
    notes = Notification.objects.filter(
        models.Q(recipient_name=user) | models.Q(recipient_name='')
    ).order_by('-created_at')
    notes.filter(is_read=False, recipient_name=user).update(is_read=True)

    context = {
        'active': 'notifications',
        'notifications': notes,
        'has_notifications': notes.exists(),
        'unread_count': 0,
    }
    return render(request, 'Tests/notifications.html', context)


# ---------- Saved ----------
def saved_papers(request):
    context = {
        'active': 'profile',
        'user_name': get_user_name(request),
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/saved.html', context)


# ---------- Admin queue (ADMIN ONLY) ----------
def admin_queue(request):
    if not is_admin(request):
        return redirect('home')

    pending = Paper.objects.filter(verified=False)
    verified = Paper.objects.filter(verified=True)

    flagged = Paper.objects.annotate(
        report_count=Count('reports')
    ).filter(report_count__gte=REPORT_THRESHOLD).order_by('-report_count')

    reports = PaperReport.objects.select_related('paper').order_by('-created_at')[:30]

    context = {
        'pending': pending,
        'verified': verified,
        'flagged': flagged,
        'reports': reports,
        'pending_count': pending.count(),
        'verified_count': verified.count(),
        'flagged_count': flagged.count(),
        'report_count': reports.count(),
        'report_threshold': REPORT_THRESHOLD,
        'unread_count': get_unread_notifications_count(request),
    }
    return render(request, 'Tests/admin_queue.html', context)


def approve_paper(request, paper_id):
    if not is_admin(request):
        return redirect('home')

    paper = get_object_or_404(Paper, id=paper_id)
    paper.verified = True
    paper.verified_by = get_user_name(request)
    paper.save()

    Notification.objects.create(
        recipient_name=paper.uploader_name,
        title="✅ Your paper was approved",
        message=f"{paper.unit_code} — {paper.title} has been verified and is now live in the archive.",
    )
    return redirect(request.META.get('HTTP_REFERER') or 'admin_queue')


def reject_paper(request, paper_id):
    if not is_admin(request):
        return redirect('home')

    paper = get_object_or_404(Paper, id=paper_id)
    uploader = paper.uploader_name
    unit = paper.unit_code
    title = paper.title
    paper.delete()

    Notification.objects.create(
        recipient_name=uploader,
        title="❌ Your paper was rejected",
        message=f"{unit} — {title} did not pass verification. It may have been unclear, incomplete, or a duplicate.",
    )
    return redirect(request.META.get('HTTP_REFERER') or 'admin_queue')


def admin_delete_paper(request, paper_id):
    if not is_admin(request):
        return redirect('home')

    paper = get_object_or_404(Paper, id=paper_id)
    uploader = paper.uploader_name
    unit = paper.unit_code
    title = paper.title
    paper.delete()

    Notification.objects.create(
        recipient_name=uploader,
        title="🗑️ Your paper was removed",
        message=f"{unit} — {title} was removed from the archive by a moderator.",
    )
    return redirect(request.META.get('HTTP_REFERER') or 'admin_queue')


# ---------- Delete own paper ----------
def delete_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    current_user = get_user_name(request)
    is_uploader = (paper.uploader_name == current_user)
    admin = is_admin(request)

    if not (is_uploader or admin):
        return redirect('paper_detail', paper_id=paper.id)

    uploader = paper.uploader_name
    unit = paper.unit_code
    title = paper.title
    paper.delete()

    if admin and not is_uploader:
        Notification.objects.create(
            recipient_name=uploader,
            title="🗑️ Your paper was removed",
            message=f"{unit} — {title} was removed from the archive by a moderator.",
        )
        return redirect('admin_queue')

    return redirect('home')


# ---------- Report ----------
def report_paper(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    reason = request.GET.get('reason', '').strip() or 'No reason given'
    reporter = get_user_name(request)

    PaperReport.objects.create(
        paper=paper,
        reporter_name=reporter,
        reason=reason,
    )

    Notification.objects.create(
        recipient_name='Moderators',
        title=f"⚠️ Paper reported: {paper.unit_code}",
        message=f"{reporter} reported '{paper.title}' ({paper.unit_code}). Reason: {reason}",
    )
    return redirect('paper_detail', paper_id=paper.id)