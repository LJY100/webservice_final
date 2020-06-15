from django.db import models

# Create your models here.
class Board(models.Model):
	board_id = models.IntegerField()
	board_title = models.TextField()
	board_url = models.URLField(max_length=300)
	board_text = models.TextField()
	board_date = models.TextField()
	board_alert = models.BooleanField()