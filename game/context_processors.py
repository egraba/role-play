def navbar_context(request):
    """Provide navbar-related context variables to all templates."""
    context = {
        "user_character": None,
    }

    if request.user.is_authenticated:
        # Character has OneToOneField to User, so we can access it via reverse relation
        try:
            context["user_character"] = request.user.character
        except request.user._meta.model.character.RelatedObjectDoesNotExist:
            pass

    return context
