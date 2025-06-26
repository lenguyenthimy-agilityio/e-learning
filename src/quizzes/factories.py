"""
Quizz factories for creating quiz instances with predefined questions and answers.
"""

from core import factories
from courses.factories import CourseFactory
from quizzes.models import Question, Quiz, QuizSubmission
from users.factories import UserFactory


class QuizFactory(factories.ModelFactory):
    """
    Faker for Quiz model.
    """

    class Meta:
        """
        Class Meta for QuizFactory.
        """

        model = Quiz

    title = factories.Sequence(lambda n: f"Quiz {n}")
    course = factories.SubFactory(CourseFactory)


class QuestionFactory(factories.ModelFactory):
    """
    Faker for Question model.
    """

    class Meta:
        """
        Class Meta for QuestionFactory.
        """

        model = Question

    quiz = factories.SubFactory(QuizFactory)
    text = factories.Faker("sentence", nb_words=10)
    options = factories.Faker("words", nb=4, unique=True)
    correct_answer = factories.Faker("random_element", elements=["A", "B", "C", "D"])


class QuizSubmissionFactory(factories.ModelFactory):
    """
    Faker for QuizSubmission model.
    """

    class Meta:
        """
        Class Meta for QuizSubmissionFactory.
        """

        model = QuizSubmission

    student = factories.SubFactory(UserFactory)
    quiz = factories.SubFactory(QuizFactory)
    score = factories.Faker("random_int", min=0, max=100)
    submitted_at = factories.Faker("date_time_this_year")
