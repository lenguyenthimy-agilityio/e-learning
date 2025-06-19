"""
Service functions for quizzes.
"""

from quizzes.models import Question, Quiz, QuizSubmission


class QuizService:
    """
    Service class for managing quizzes.
    """

    def create_quiz(self, course, title):
        """
        Create a new quiz for a course.
        """
        return Quiz.objects.create(title=title, course=course)

    def add_question(self, quiz, text, options, correct_answer):
        """
        Add a question to a quiz.
        """
        return Question.objects.create(quiz=quiz, text=text, options=options, correct_answer=correct_answer)

    def submit_quiz(self, student, quiz, score):
        """
        Submit a quiz for a student.
        """
        return QuizSubmission.objects.create(student=student, quiz=quiz, score=score)
