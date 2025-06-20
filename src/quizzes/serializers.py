"""
Register serializers for the quizzes app.
"""

from rest_framework import serializers

from core.serializers import BaseSerializer
from quizzes.models import Question, Quiz


class QuizRequestSerializer(BaseSerializer):
    """
    QuizRequestSerializer for creating a new quiz.
    """

    title = serializers.CharField()
    course_id = serializers.IntegerField()


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating quiz details.
    """

    class Meta:
        """
        Meta class for QuizUpdateSerializer.
        """

        model = Quiz
        fields = ["title"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model, used for creating and updating questions in a quiz.
    """

    class Meta:
        """
        Meta class for QuestionSerializer.
        """

        model = Question
        fields = ["id", "text", "options", "correct_answer"]
        # quiz is not required from input, handled in view
        extra_kwargs = {
            "quiz": {"write_only": True, "required": False},
        }

    def validate(self, attrs):
        """
        Validate the question data to ensure the correct answer is one of the options.
        """
        if attrs["correct_answer"] not in attrs["options"]:
            raise serializers.ValidationError({"correct_answer": "Correct answer must be one of the options."})
        return attrs


class QuestionDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer for displaying questions in a quiz without the correct answer.
    """

    class Meta:
        """
        Meta class for QuestionDisplaySerializer.
        """

        model = Question
        fields = ["id", "text", "options"]


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for Quiz model.
    """

    questions = QuestionDisplaySerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class for QuizSerializer.
        """

        model = Quiz
        fields = ["id", "title", "questions"]


class QuizSubmissionSerializer(BaseSerializer):
    """
    Serializer for quiz submission data.
    """

    answers = serializers.ListField(child=serializers.DictField(child=serializers.CharField()))
