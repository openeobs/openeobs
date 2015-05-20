These ARE the objects your are looking for:
{% for r in routes %}
    {{ r.name }}
{% endfor %}
And this is the additional context: {{ foo }}