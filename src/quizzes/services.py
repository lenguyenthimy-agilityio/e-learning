"""
Service functions for quizzes.
"""

from core.exception import QuizException
from quizzes.models import Quiz, QuizSubmission


class QuizService:
    """
    Service class for managing quizzes.
    """

    def create_quiz(self, course, title):
        """
        Create a new quiz for a course.
        """
        return Quiz.objects.create(title=title, course=course)

    def submit_quiz(self, answers, user, quiz):
        """
        Submit a quiz for a student.
        """
        questions = {str(q.id): q for q in quiz.questions.all()}
        total_questions = len(questions)
        correct_count = 0

        for answer in answers:
            question_id = str(answer.get("question_id"))
            selected_option = answer.get("selected_option")

            question = questions.get(question_id)
            if question and question.correct_answer == selected_option:
                correct_count += 1

        score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0.0

        submission = QuizSubmission.objects.create(
            student=user,
            quiz=quiz,
            score=score,
        )

        return submission, score

    def is_submitted(self, student, quiz):
        """
        Verify if a student has already submitted the quiz.
        """
        if QuizSubmission.objects.filter(student=student, quiz=quiz).exists():
            raise QuizException(code="ALREADY_COMPLETED")

    def verify_all_questions_answered(self, answers, quiz):
        """
        Verify if all questions are answered.
        """
        questions = quiz.questions.count()
        if len(answers) != questions:
            raise QuizException(code="MISSING_ANSWER")
