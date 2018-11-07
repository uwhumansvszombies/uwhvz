Hey {{ tag.receiver }}!

A stun has been reported on you at {{ tag.tagged_at | format_datetime }} by {{ tag.initiator }}{% if tag.location %} at the location {{ tag.location }}{% endif %}.

{% if tag.description %}The following description has been added: {{ tag.description }}{% endif %}