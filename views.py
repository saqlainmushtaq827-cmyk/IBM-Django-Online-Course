from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, Choice, Submission


def submit(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)

        submission = Submission.objects.create(
            user=request.user,
            exam=lesson
        )

        selected_choices = request.POST.getlist('choice')

        for choice_id in selected_choices:
            choice = get_object_or_404(Choice, id=choice_id)
            submission.choices.add(choice)

        return redirect(
            'onlinecourse:show_exam_result',
            lesson_id=lesson.id
        )

    return redirect('onlinecourse:course_list')


def show_exam_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    submission = Submission.objects.filter(
        user=request.user,
        exam=lesson
    ).last()

    score = 0
    total = 0

    if submission:
        questions = lesson.question_set.all()
        total = questions.count()

        for question in questions:
            correct = question.choices.filter(is_correct=True)
            selected = submission.choices.filter(question=question)

            if correct.exists() and set(correct) == set(selected):
                score += 1

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'lesson': lesson,
        'submission': submission,
        'score': score,
        'total': total,
    })