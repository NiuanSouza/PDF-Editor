from django.db import models
from django.utils import timezone

class AuditLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    task_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    tool_used = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    file_count = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tool_used} - {self.status} at {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']
