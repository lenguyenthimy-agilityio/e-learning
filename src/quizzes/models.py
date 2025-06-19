"""
Quizzes models for the online learning platform.
"""

from django.db import models

from courses.models import Course
from users.models import User


class Quiz(models.Model):
    """
    Quiz model to represent a quiz in a course.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)


class Question(models.Model):
    """
    Question model to represent a question in a quiz.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255)


class QuizSubmission(models.Model):
    """
    QuizSubmission model to track student submissions for quizzes.
    """

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_at = models.DateTimeField(auto_now_add=True)
