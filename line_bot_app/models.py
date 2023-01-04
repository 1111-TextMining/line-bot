from django.db import models

class User_Note(models.Model):
    uid = models.CharField(max_length = 50, null = False, default = '')
    notes = models.CharField(max_length = 2000, blank = True, null = False)
    mdt = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.uid

class User_Message(models.Model):
    uid = models.CharField(max_length = 50, null = False, default = '')
    mtext = models.CharField(max_length = 2000, blank = True, null = False)
    rtext = models.CharField(max_length = 2000, blank = True, null = False)
    ner_result = models.CharField(max_length = 2000, blank = True, null = False)
    mdt = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.uid
