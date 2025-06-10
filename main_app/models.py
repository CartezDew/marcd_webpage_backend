from django.db import models

class ContactSubmission(models.Model):
    contact_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.contact_id:
            last_contact = ContactSubmission.objects.order_by('-id').first()
            if last_contact and last_contact.contact_id:
                last_id_num = int(last_contact.contact_id.replace("CT-", ""))
                new_id_num = last_id_num + 1
            else:
                new_id_num = 1
            self.contact_id = f"CT-{new_id_num:03d}"  # CT-001, CT-002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_id} - {self.first_name} {self.last_name}"
