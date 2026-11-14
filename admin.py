{% extends "onlinecourse/base.html" %}

{% block content %}

<div class="container mt-5">
    <h2>{{ course.name }}</h2>

    <div class="list-group mt-4">
        {% for lesson in course.lesson_set.all %}
        <div class="list-group-item">
            <h5>{{ lesson.title }}</h5>
            <p>{{ lesson.description }}</p>
        </div>
        {% endfor %}
    </div>
</div>

{% endblock %}