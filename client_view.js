<!DOCTYPE html>
<html>
<head>
    <title>Action Items for {{ client_id }}</title>
</head>
<body>
    <h1>Update Action Items: {{ client_id }}</h1>
    <form method="post">
        <table border="1" cellpadding="8">
            <tr>
                <th>Action Item</th>
                <th>Update Status</th>
            </tr>
            {% for index, row in items.iterrows() %}
            <tr>
                <td>{{ row["Action Items"] }}</td>
                <td>
                    <select name="{{ row['Action Items'] }}">
                        {% for status in status_options %}
                            <option value="{{ status }}">{{ status }}</option>
                        {% endfor %}
                    </select>
                </td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <input type="submit" value="Submit Updates">
    </form>
</body>
</html>