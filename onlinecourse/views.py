
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Enrollment,
    Submission
)


def home(request):
    courses = Course.objects.all()

    return render(
        request,
        'onlinecourse/home.html',
        {'courses': courses}
    )


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(
        request,
        'onlinecourse/course_details_bootstrap.html',
        {'course': course}
    )


@login_required
def exam(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    return render(
        request,
        'onlinecourse/exam_bootstrap.html',
        {'lesson': lesson}
    )


@login_required
def submit(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    if request.method != 'POST':
        return redirect(
            'onlinecourse:course_details',
            course_id=course.id
        )

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    submission = Submission.objects.create(
        enrollment=enrollment,
        user=request.user
    )

    selected_ids = request.POST.getlist('choice')

    valid_choices = Choice.objects.filter(
        id__in=selected_ids
    ).filter(
        Q(question__course=course) |
        Q(question__lesson__course=course)
    )

    submission.choices.set(valid_choices)

    return redirect(
        'onlinecourse:show_exam_result',
        course_id=course.id,
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):

    course = get_object_or_404(Course, id=course_id)

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course
    )

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment=enrollment
    )

    questions = Question.objects.filter(
        Q(course=course) |
        Q(lesson__course=course)
    ).distinct().prefetch_related('choices')

    score = 0
    total = 0
    results = []

    selected_ids = list(
        submission.choices.values_list('id', flat=True)
    )

    for question in questions:

        total += question.grade

        question_selected_ids = submission.choices.filter(
            question=question
        ).values_list('id', flat=True)

        question_score = question.is_get_score(
            question_selected_ids
        )

        score += question_score

        results.append({
            'question': question,
            'selected': submission.choices.filter(
                question=question
            ),
            'correct_choices': question.choices.filter(
                is_correct=True
            ),
            'is_correct': question_score > 0,
            'grade': question_score,
        })

    percentage = round((score / total) * 100) if total else 0

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        {
            'course': course,
            'submission': submission,
            'enrollment': enrollment,
            'selected_ids': selected_ids,
            'grade': score,
            'score': score,
            'total': total,
            'percentage': percentage,
            'results': results,
        }
    )
