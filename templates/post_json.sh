#!/bin/bash
set -e && set -x

curl \
	-X POST \
{% for header in post["headers"] %}
	-H "{{header}}" \
{% endfor %}
	{{post["protocol"]}}://{{post["uri"]}} \
	-d '{{post["data"]|tojson}}'
