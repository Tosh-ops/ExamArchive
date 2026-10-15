from django.db import models


class Paper(models.Model):
    CAMPUS_CHOICES = [
        ('main', 'Main Campus'),
        ('kikuyu', 'Kikuyu Campus'),
        ('chiromo', 'Chiromo Campus'),
        ('lower_kabete', 'Lower Kabete Campus'),
        ('parklands', 'Parklands Campus'),
        ('other', 'Other Campus'),
    ]

    EXAM_TYPE_CHOICES = [
        ('final', 'Final Exam'),
        ('cat', 'CAT'),
        ('midterm', 'Midterm'),
        ('assignment', 'Assignment'),
    ]

    SEMESTER_CHOICES = [
        ('sem1', 'Semester 1'),
        ('sem2', 'Semester 2'),
    ]

    UNIVERSITY_CHOICES = [
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

    unit_code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    course = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    university = models.CharField(max_length=30, choices=UNIVERSITY_CHOICES, default='uon')
    campus = models.CharField(max_length=30, choices=CAMPUS_CHOICES, default='main')

    year = models.IntegerField()
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='sem1')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='final')

    uploaded_file = models.FileField(upload_to='papers/', blank=True, null=True)

    verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=100, blank=True, default='')
    downloads = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    uploader_name = models.CharField(max_length=100, default='Anonymous')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.unit_code} - {self.title}"


class PaperReport(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='reports')
    reporter_name = models.CharField(max_length=100, blank=True, default='Anonymous')
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.paper.unit_code} — {self.reason}"


class Badge(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='🏆')
    description = models.CharField(max_length=200)
    earned = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Notification(models.Model):
    recipient_name = models.CharField(max_length=100, blank=True, default='')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title