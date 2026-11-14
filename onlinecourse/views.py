
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Choice, Submission


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
def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method != 'POST':
        return redirect('onlinecourse:exam', lesson_id=lesson.id)

    submission = Submission.objects.create(
        user=request.user,
        exam=lesson
    )

    selected_ids = request.POST.getlist('choice')

    # Only accept choices belonging to this lesson.
    valid_choices = Choice.objects.filter(
        id__in=selected_ids,
        question__lesson=lesson
    )

    submission.choices.set(valid_choices)

    return redirect(
        'onlinecourse:show_exam_result',
        lesson_id=lesson.id,
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, lesson_id, submission_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user,
        exam=lesson
    )

    questions = lesson.questions.prefetch_related('choices').all()

    score = 0
    total = questions.count()
    results = []

    for question in questions:
        correct_choices = set(
            question.choices.filter(is_correct=True).values_list(
                'id', flat=True
            )
        )

        selected_choices = set(
            submission.choices.filter(
                question=question
            ).values_list('id', flat=True)
        )

        is_correct = (
            bool(correct_choices)
            and correct_choices == selected_choices
        )

        if is_correct:
            score += 1

        results.append({
            'question': question,
            'selected': submission.choices.filter(
                question=question
            ),
            'correct_choices': question.choices.filter(
                is_correct=True
            ),
            'is_correct': is_correct,
        })

    percentage = round((score / total) * 100) if total else 0

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        {
            'lesson': lesson,
            'submission': submission,
            'score': score,
            'total': total,
            'percentage': percentage,
            'results': results,
        }
    )
def home(request):
    courses = Course.objects.all()

    return render(
        request,
        'onlinecourse/home.html',
        {'courses': courses}
    )