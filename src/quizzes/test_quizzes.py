"""
Test cases for the quizzes module.
"""

from core.constants import UserRole
from core.tests import BaseAPITestCase
from courses.factories import CategoryFactory, CourseFactory
from courses.models import Enrollment
from quizzes.apis import QuizViewSet
from quizzes.models import Question, Quiz


class QuizAPITestCase(BaseAPITestCase):
    """
    Test case for Quiz API endpoints.
    """

    resource = QuizViewSet

    def setUp(self):
        """
        Set up the test case with initial data.
        """
        super().setUp()

        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.student = self.make_user(role=UserRole.STUDENT.value)

        self.category = CategoryFactory(name="Programming")
        self.course = CourseFactory(instructor=self.instructor, category=self.category)
        self.quiz = Quiz.objects.create(title="Intro Quiz", course=self.course)
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            options=["3", "4", "5"],
            correct_answer="4",
        )

    def test_create_quiz_success(self):
        """
        Test creating a new quiz as an instructor.
        """
        self.set_authenticate(user=self.instructor)

        payload = {"title": "New Quiz", "course_id": self.course.id}
        response = self.post_json_created(data=payload)

        assert response.status_code == 201
        assert response.data["title"] == "New Quiz"

    def test_create_quiz_forbidden_if_not_owner(self):
        """
        Test that a student cannot create a quiz.
        """
        self.set_authenticate(user=self.student)

        payload = {"title": "Unauthorized Quiz", "course_id": self.course.id}
        response = self.post_json_forbidden(data=payload)

        assert response.status_code == 403

    def test_add_question_to_quiz_success(self):
        """
        Test adding a question to a quiz as an instructor.
        """
        self.set_authenticate(user=self.instructor)

        payload = {"text": "What is the output of print(1+1)?", "options": ["1", "2", "11"], "correct_answer": "2"}
        response = self.post_json_ok(data=payload, fragment=f"{self.quiz.id}/questions/")

        assert response.status_code == 201
        assert response.data["correct_answer"] == "2"

    def test_student_can_not_add_question(self):
        """
        Test that a student cannot add a question to a quiz.
        """
        self.set_authenticate(user=self.student)
        payload = {"text": "Hack?", "options": ["A", "B"], "correct_answer": "A"}
        response = self.post_json_forbidden(data=payload, fragment=f"{self.quiz.id}/questions/")
        assert response.status_code == 403

    def test_add_question_forbidden_for_non_owner(self):
        """
        Test that a question cannot be added by a user who is not the quiz owner.
        """
        another_instructor = self.make_user(role=UserRole.INSTRUCTOR.value)

        self.set_authenticate(user=another_instructor)
        payload = {"text": "Hack?", "options": ["A", "B"], "correct_answer": "A"}
        response = self.post_json_forbidden(data=payload, fragment=f"{self.quiz.id}/questions/")
        assert response.status_code == 403

    def test_retrieve_quiz_as_enrolled_student(self):
        """
        Test that an enrolled student can view a quiz.
        """
        Enrollment.objects.create(course=self.course, student=self.student)
        self.set_authenticate(user=self.student)

        response = self.get_json_ok(fragment=f"{self.quiz.id}")

        assert response.status_code == 200
        assert "questions" in response.data

    def test_retrieve_quiz_forbidden_if_not_enrolled(self):
        """
        Test that a student cannot view a quiz if not enrolled.
        """
        self.set_authenticate(user=self.student)
        response = self.get_json_forbidden(fragment=f"{self.quiz.id}")
        assert response.status_code == 403

    def test_submit_quiz_success(self):
        """
        Test submitting a quiz with correct answers.
        """
        Enrollment.objects.create(course=self.course, student=self.student)
        self.set_authenticate(user=self.student)

        payload = {"answers": [{"question_id": str(self.question.id), "selected_option": "4"}]}
        response = self.post_json_ok(data=payload, fragment=f"{self.quiz.id}/submit/")
        assert response.status_code == 200
        assert response.data["score"] == 100

    def test_submit_quiz_missing_answer(self):
        """
        Test submitting a quiz with missing answers.
        """
        Enrollment.objects.create(course=self.course, student=self.student)
        self.set_authenticate(user=self.student)

        payload = {"answers": []}  # No answers provided
        response = self.post_json_bad_request(data=payload, fragment=f"{self.quiz.id}/submit/")
        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_QUIZ_MISSING_ANSWER"

    def test_submit_quiz_already_submitted(self):
        """
        Test submitting a quiz that has already been submitted.
        """
        Enrollment.objects.create(course=self.course, student=self.student)
        self.set_authenticate(user=self.student)

        payload = {"answers": [{"question_id": str(self.question.id), "selected_option": "4"}]}
        self.post_json_ok(data=payload, fragment=f"{self.quiz.id}/submit/")

        response = self.post_json_bad_request(data=payload, fragment=f"{self.quiz.id}/submit/")
        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_QUIZ_ALREADY_COMPLETED"

    def test_delete_quiz_success(self):
        """
        Test deleting a quiz as an instructor.
        """
        self.set_authenticate(user=self.instructor)

        response = self.delete_json_no_content(fragment=f"{self.quiz.id}")
        assert response.status_code == 204
        assert Quiz.objects.filter(id=self.quiz.id).count() == 0

    def test_delete_quiz_forbidden_if_not_owner(self):
        """
        Test that a student cannot delete a quiz.
        """
        self.set_authenticate(user=self.student)

        response = self.delete_json_forbidden(fragment=f"{self.quiz.id}")
        assert response.status_code == 403

    def test_delete_quiz_forbidden_if_another_instructor(self):
        """
        Test that a non-instructor cannot delete a quiz.
        """
        another_instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.set_authenticate(user=another_instructor)

        response = self.delete_json_forbidden(fragment=f"{self.quiz.id}")
        assert response.status_code == 403

    def test_quiz_not_found(self):
        """
        Test that accessing a non-existent quiz returns a 404 error.
        """
        self.set_authenticate(user=self.instructor)

        response = self.get_json_not_found(fragment="9999")
        assert response.status_code == 404

    def test_student_can_take_quiz(self):
        """
        Test that a student can take a quiz.
        """
        Enrollment.objects.create(course=self.course, student=self.student)
        self.set_authenticate(user=self.student)

        response = self.get_json_ok(fragment=f"{self.quiz.id}/")
        assert response.status_code == 200
        assert "questions" in response.data
