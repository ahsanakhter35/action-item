<!DOCTYPE html>
<html>
<head>
    <title>Client Links</title>
</head>
<body>
    <h1>Client Access Links</h1>
    <ul>
        {% for client_id in client_ids %}
            <li><a href="/client/{{ client_id }}">{{ client_id }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>