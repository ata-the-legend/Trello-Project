from django.db import models


class Task(BaseModel):
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=300)
    order = models.IntegerField()
    label = models.ForeignKey('Label',on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    assigned_to = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Label(BaseModel):
    title = models.CharField(max_length=300)
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(BaseModel):
    body = models.TextField()
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)    