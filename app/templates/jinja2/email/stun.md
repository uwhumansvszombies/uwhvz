Hey {{ tag.receiver }}!

A stun has been reported on you at {{ tag.tagged_at | format_datetime }} by {{ tag.initiator }}{% if tag.location %}{{ tag.location }}{% endif %}.
