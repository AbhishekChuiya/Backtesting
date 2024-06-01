from django.db import models
from users.models import User

# Create your models here.

class BacktestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # ForeignKey to User model
    pdf_file = models.BinaryField()
    # pdf_file = models.FileField(upload_to='backtest_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BacktestResult {self.pk}"  
