Hey {{ tag.receiver }}!

Looks like you’ve been tagged by {{ tag.initiator }} at {{ tag.tagged_at | format_datetime }}{% if tag.location %} at the location {{ tag.location }}{% endif %}. Congrats! You’re now a zombie.

{% if tag.description %}The following description has been added: {{ tag.description }}{% endif %}